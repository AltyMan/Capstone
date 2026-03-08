#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_wifi.h"
#include "nvs_flash.h"
#include "audio_pipeline.h"
#include "i2s_stream.h"
#include "tcp_client_stream.h"
#include "board.h"
#include "periph_wifi.h"
#include "algorithm_stream.h"
#include "audio_event_iface.h"
#include "lwip/sockets.h"
#include "raw_stream.h"
#include "esp_wn_iface.h"
#include "esp_wn_models.h"
#include "model_path.h"

static const char *TAG = "WAKENET_CLIENT";

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
    audio_hal_ctrl_codec(board_handle->audio_hal, AUDIO_HAL_CODEC_MODE_ENCODE, AUDIO_HAL_CTRL_START);
    
    ESP_LOGI(TAG, "Initialize WakeNet");
    srmodel_list_t *models = esp_srmodel_init("model");
    char *model_name = esp_srmodel_filter(models, ESP_WN_PREFIX, NULL); 
    if (model_name == NULL) {
        ESP_LOGE(TAG, "WakeNet model not found in partition!");
        return;
    }
    ESP_LOGI(TAG, "Using WakeNet model: %s", model_name);

    esp_wn_iface_t *wakenet = (esp_wn_iface_t*)esp_wn_handle_from_name(model_name);

    model_iface_data_t *model_data = wakenet->create(model_name, DET_MODE_95);

    int audio_chunksize_bytes = wakenet->get_samp_chunksize(model_data) * sizeof(int16_t);
    int16_t *buffer = (int16_t *) malloc(audio_chunksize_bytes);

    ESP_LOGI(TAG, "Create audio pipeline");
    audio_pipeline_cfg_t pipeline_cfg = DEFAULT_AUDIO_PIPELINE_CONFIG();
    audio_pipeline_handle_t pipeline = audio_pipeline_init(&pipeline_cfg);

    ESP_LOGI(TAG, "Create I2S stream");
    i2s_stream_cfg_t i2s_cfg = I2S_STREAM_CFG_DEFAULT_WITH_TYLE_AND_CH(CODEC_ADC_I2S_PORT, 16000, 16, AUDIO_STREAM_READER, 1);
    i2s_cfg.type = AUDIO_STREAM_READER;
    audio_element_handle_t i2s_stream_reader = i2s_stream_init(&i2s_cfg);

    raw_stream_cfg_t raw_cfg = RAW_STREAM_CFG_DEFAULT();
    raw_cfg.type = AUDIO_STREAM_WRITER;
    audio_element_handle_t raw_read = raw_stream_init(&raw_cfg);

    ESP_LOGI(TAG, "Register elements and link pipeline");
    audio_pipeline_register(pipeline, i2s_stream_reader, "i2s");
    audio_pipeline_register(pipeline, raw_read, "raw");

    const char *link_tag[3] = {"i2s", "raw"};
    audio_pipeline_link(pipeline, &link_tag[0], 2);

    ESP_LOGI(TAG, "Start audio pipeline");
    audio_pipeline_run(pipeline);

    ESP_LOGI(TAG, "Listening for Wake Word...");

    while (1) {
        raw_stream_read(raw_read, (char *)buffer, audio_chunksize_bytes);
        
        int res = wakenet->detect(model_data, buffer);
        
        if (res > 0) {
            ESP_LOGI(TAG, "WAKE WORD DETECTED");
            ESP_LOGI(TAG, "Opening TCP socket...");
            
            int sock = socket(AF_INET, SOCK_STREAM, 0);
            struct sockaddr_in server_addr;
            server_addr.sin_family = AF_INET;
            server_addr.sin_port = htons(CONFIG_TCP_PORT);
            inet_pton(AF_INET, CONFIG_TCP_URL, &server_addr.sin_addr.s_addr);
            
            if (connect(sock, (struct sockaddr *)&server_addr, sizeof(server_addr)) == 0) {
                ESP_LOGI(TAG, "Streaming 5 seconds of audio for command processing...");
                
                int bytes_to_send = 160000;
                int bytes_sent = 0;
                
                while (bytes_sent < bytes_to_send) {
                    raw_stream_read(raw_read, (char *)buffer, audio_chunksize_bytes);
                    send(sock, buffer, audio_chunksize_bytes, 0);
                    bytes_sent += audio_chunksize_bytes;
                }
                
                close(sock);
                ESP_LOGI(TAG, "Transmission complete. Listening for wake word again...");
            } else {
                ESP_LOGE(TAG, "Failed to connect to Mac! Is the Python script running?");
                close(sock);
            }
        }
    }
}