#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "nvs_flash.h"
#include "audio_pipeline.h"
#include "i2s_stream.h"
#include "mp3_decoder.h"
#include "audio_event_iface.h"
#include "board.h"
#include "periph_wifi.h"
#include "lwip/sockets.h"
#include "raw_stream.h"
#include "esp_wn_iface.h"
#include "esp_wn_models.h"
#include "model_path.h"
#include "driver/gpio.h"
#include "ding_mp3.h"

static const char *TAG = "WAKENET_CLIENT";

// Playback Modes
typedef enum {
    PLAY_MODE_FLASH,
    PLAY_MODE_SOCKET
} play_mode_t;

static play_mode_t current_play_mode = PLAY_MODE_FLASH;
static int active_tts_sock = -1;
static int mp3_pos = 0;

// 1. Dual-Mode MP3 Callback
int mp3_read_cb(audio_element_handle_t el, char *buf, int len, TickType_t wait_time, void *ctx)
{
    if (current_play_mode == PLAY_MODE_FLASH) {
        int read_size = ding_mp3_len - mp3_pos;
        if (read_size <= 0) return AEL_IO_DONE; 
        if (read_size > len) read_size = len;
        
        memcpy(buf, ding_mp3 + mp3_pos, read_size);
        mp3_pos += read_size;
        return read_size;
        
    } else if (current_play_mode == PLAY_MODE_SOCKET) {
        if (active_tts_sock < 0) return AEL_IO_DONE;
        
        // Read directly from the TCP network socket
        int bytes_read = recv(active_tts_sock, buf, len, 0);
        
        // If recv returns 0, the Python server finished sending the MP3 and closed the connection
        if (bytes_read <= 0) return AEL_IO_DONE; 
        
        return bytes_read;
    }
    return AEL_IO_DONE;
}

// 2. Universal Anti-Pop Playback Function
void play_mp3_audio(audio_pipeline_handle_t play_pipeline, audio_element_handle_t mp3_decoder, audio_element_handle_t i2s_writer) {
    int pa_gpio = get_pa_enable_gpio();
    if (pa_gpio >= 0) gpio_set_level(pa_gpio, 0); // Keep amplifier OFF
    
    if (current_play_mode == PLAY_MODE_FLASH) mp3_pos = 0;
    
    audio_event_iface_cfg_t evt_cfg = AUDIO_EVENT_IFACE_DEFAULT_CFG();
    audio_event_iface_handle_t evt = audio_event_iface_init(&evt_cfg);
    audio_pipeline_set_listener(play_pipeline, evt);

    audio_pipeline_reset_ringbuffer(play_pipeline);
    audio_pipeline_reset_elements(play_pipeline);
    audio_pipeline_run(play_pipeline);

    while (1) {
        audio_event_iface_msg_t msg;
        esp_err_t ret = audio_event_iface_listen(evt, &msg, portMAX_DELAY);
        if (ret != ESP_OK) continue;

        // Catch the decoder info and apply it to the hardware dynamically
        if (msg.source_type == AUDIO_ELEMENT_TYPE_ELEMENT && msg.source == (void *) mp3_decoder
            && msg.cmd == AEL_MSG_CMD_REPORT_MUSIC_INFO) {
            audio_element_info_t music_info = {0};
            audio_element_getinfo(mp3_decoder, &music_info);
            
            audio_element_set_music_info(i2s_writer, music_info.sample_rates, music_info.channels, music_info.bits);
            i2s_stream_set_clk(i2s_writer, music_info.sample_rates, music_info.bits, music_info.channels);
            
            // Soft-start the amplifier
            vTaskDelay(pdMS_TO_TICKS(20));
            if (pa_gpio >= 0) gpio_set_level(pa_gpio, 1);
            continue;
        }

        // Wait for the sound to naturally finish draining
        if (msg.source_type == AUDIO_ELEMENT_TYPE_ELEMENT && msg.source == (void *) i2s_writer
            && msg.cmd == AEL_MSG_CMD_REPORT_STATUS
            && (((int)msg.data == AEL_STATUS_STATE_STOPPED) || ((int)msg.data == AEL_STATUS_STATE_FINISHED))) {
            break;
        }
    }

    if (pa_gpio >= 0) gpio_set_level(pa_gpio, 0); // Kill amplifier BEFORE pipeline closes

    audio_pipeline_stop(play_pipeline);
    audio_pipeline_wait_for_stop(play_pipeline);
    audio_pipeline_remove_listener(play_pipeline);
    audio_event_iface_destroy(evt);
}

void app_main(void)
{
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);
    ESP_ERROR_CHECK(esp_netif_init());

    esp_periph_config_t periph_cfg = DEFAULT_ESP_PERIPH_SET_CONFIG();
    esp_periph_set_handle_t set = esp_periph_set_init(&periph_cfg);

    periph_wifi_cfg_t wifi_cfg = {
        .wifi_config.sta.ssid = CONFIG_WIFI_SSID,
        .wifi_config.sta.password = CONFIG_WIFI_PASSWORD,
    };
    esp_periph_handle_t wifi_handle = periph_wifi_init(&wifi_cfg);
    esp_periph_start(set, wifi_handle);
    periph_wifi_wait_for_connected(wifi_handle, portMAX_DELAY);

    ESP_LOGI(TAG, "Initialize Audio Board and Codec");
    audio_board_handle_t board_handle = audio_board_init();
    audio_hal_ctrl_codec(board_handle->audio_hal, AUDIO_HAL_CODEC_MODE_BOTH, AUDIO_HAL_CTRL_START);
    audio_hal_set_volume(board_handle->audio_hal, 100);
    audio_hal_set_mute(board_handle->audio_hal, false);
    
    int pa_gpio = get_pa_enable_gpio();
    if (pa_gpio >= 0) {
        gpio_set_direction(pa_gpio, GPIO_MODE_OUTPUT);
        gpio_set_level(pa_gpio, 0);
    }
    
    ESP_LOGI(TAG, "Initialize WakeNet");
    srmodel_list_t *models = esp_srmodel_init("model");
    char *model_name = esp_srmodel_filter(models, ESP_WN_PREFIX, NULL); 
    if (model_name == NULL) return;

    esp_wn_iface_t *wakenet = (esp_wn_iface_t*)esp_wn_handle_from_name(model_name);
    model_iface_data_t *model_data = wakenet->create(model_name, DET_MODE_95);

    int audio_chunksize_bytes = wakenet->get_samp_chunksize(model_data) * sizeof(int16_t);
    int16_t *buffer = (int16_t *) malloc(audio_chunksize_bytes);

    // Playback Pipeline (PORT 0)
    audio_pipeline_cfg_t play_pipeline_cfg = DEFAULT_AUDIO_PIPELINE_CONFIG();
    audio_pipeline_handle_t play_pipeline = audio_pipeline_init(&play_pipeline_cfg);

    mp3_decoder_cfg_t mp3_cfg = DEFAULT_MP3_DECODER_CONFIG();
    audio_element_handle_t mp3_decoder = mp3_decoder_init(&mp3_cfg);
    audio_element_set_read_cb(mp3_decoder, mp3_read_cb, NULL);

    i2s_stream_cfg_t i2s_cfg_write = I2S_STREAM_CFG_DEFAULT_WITH_TYLE_AND_CH(0, 16000, 16, AUDIO_STREAM_WRITER, 1);
    audio_element_handle_t i2s_stream_writer = i2s_stream_init(&i2s_cfg_write);

    audio_pipeline_register(play_pipeline, mp3_decoder, "mp3");
    audio_pipeline_register(play_pipeline, i2s_stream_writer, "i2s_out");
    const char *play_link_tag[2] = {"mp3", "i2s_out"};
    audio_pipeline_link(play_pipeline, &play_link_tag[0], 2); 

    // Recording Pipeline (PORT 1)
    audio_pipeline_cfg_t rec_pipeline_cfg = DEFAULT_AUDIO_PIPELINE_CONFIG();
    audio_pipeline_handle_t rec_pipeline = audio_pipeline_init(&rec_pipeline_cfg);

    i2s_stream_cfg_t i2s_cfg_read = I2S_STREAM_CFG_DEFAULT_WITH_TYLE_AND_CH(1, 16000, 16, AUDIO_STREAM_READER, 1);
    i2s_cfg_read.out_rb_size = 64*1024;
    audio_element_handle_t i2s_stream_reader = i2s_stream_init(&i2s_cfg_read);
    
    raw_stream_cfg_t raw_cfg_read = RAW_STREAM_CFG_DEFAULT();
    raw_cfg_read.type = AUDIO_STREAM_WRITER;
    audio_element_handle_t raw_read = raw_stream_init(&raw_cfg_read);

    audio_pipeline_register(rec_pipeline, i2s_stream_reader, "i2s_in");
    audio_pipeline_register(rec_pipeline, raw_read, "raw_in");
    const char *rec_link_tag[2] = {"i2s_in", "raw_in"};
    audio_pipeline_link(rec_pipeline, &rec_link_tag[0], 2);

    audio_pipeline_run(rec_pipeline);
    ESP_LOGI(TAG, "Listening for Wake Word...");

    while (1) {
        int read_len = raw_stream_read(raw_read, (char *)buffer, audio_chunksize_bytes);
        if (read_len < audio_chunksize_bytes) {
            vTaskDelay(pdMS_TO_TICKS(10)); 
            continue;
        }
        
        int res = wakenet->detect(model_data, buffer);
        if (res > 0) {
            ESP_LOGI(TAG, "WAKE WORD DETECTED");

            // Pause Mic
            audio_pipeline_stop(rec_pipeline);
            audio_pipeline_wait_for_stop(rec_pipeline);

            // Restart Mic
            audio_pipeline_reset_ringbuffer(rec_pipeline);
            audio_pipeline_reset_elements(rec_pipeline);
            audio_pipeline_run(rec_pipeline);

            // Play the Local MP3 Ding
            ESP_LOGI(TAG, "Triggering Local Ding...");
            current_play_mode = PLAY_MODE_FLASH;
            play_mp3_audio(play_pipeline, mp3_decoder, i2s_stream_writer);            
            
            ESP_LOGI(TAG, "Opening TCP socket...");
            int sock = socket(AF_INET, SOCK_STREAM, 0);
            struct sockaddr_in server_addr;
            server_addr.sin_family = AF_INET;
            server_addr.sin_port = htons(CONFIG_TCP_PORT);
            inet_pton(AF_INET, CONFIG_TCP_URL, &server_addr.sin_addr.s_addr);
            
            // Set 10-second timeout so  ESP doesn't freeze if Python server crashes
            struct timeval tv;
            tv.tv_sec = 10;
            tv.tv_usec = 0;
            setsockopt(sock, SOL_SOCKET, SO_RCVTIMEO, (const char*)&tv, sizeof(tv));
            
            if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == 0) {
                ESP_LOGI(TAG, "Streaming 5 seconds of audio...");
                int bytes_to_send = 160000; // 5 seconds * 16000 samples/second * 2 bytes/sample
                int bytes_sent = 0;
                
                while (bytes_sent < bytes_to_send) {
                    read_len = raw_stream_read(raw_read, (char *)buffer, audio_chunksize_bytes);
                    if (read_len > 0) {
                        send(sock, buffer, read_len, 0);
                        bytes_sent += read_len;
                    } else {
                        vTaskDelay(pdMS_TO_TICKS(10));
                    }
                }
                
                // Receive TTS Response
                ESP_LOGI(TAG, "Command sent. Waiting for TTS response...");
                
                // Stop Mic
                audio_pipeline_stop(rec_pipeline);
                audio_pipeline_wait_for_stop(rec_pipeline);
                
                // Switch Mode
                current_play_mode = PLAY_MODE_SOCKET;
                active_tts_sock = sock;
                play_mp3_audio(play_pipeline, mp3_decoder, i2s_stream_writer);
                
                // Cleanup
                close(sock);
                active_tts_sock = -1;
                ESP_LOGI(TAG, "TTS complete. Restarting Mic...");
                
                audio_pipeline_reset_ringbuffer(rec_pipeline);
                audio_pipeline_reset_elements(rec_pipeline);
                audio_pipeline_run(rec_pipeline);

            } else {
                ESP_LOGE(TAG, "Failed to connect to server");
                close(sock);
            }
        }
    }
}