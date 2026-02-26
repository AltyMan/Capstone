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

static const char *TAG = "MAC_STREAM";

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
    // Using ENCODE mode exactly as the working example does
    audio_hal_ctrl_codec(board_handle->audio_hal, AUDIO_HAL_CODEC_MODE_ENCODE, AUDIO_HAL_CTRL_START);

    ESP_LOGI(TAG, "Create audio pipeline for recording");
    audio_pipeline_cfg_t pipeline_cfg = DEFAULT_AUDIO_PIPELINE_CONFIG();
    audio_pipeline_handle_t pipeline = audio_pipeline_init(&pipeline_cfg);

    ESP_LOGI(TAG, "Create I2S stream using example macro for Mono alignment");
    // This specific macro grabs the audio from the correct mono channel on the LyraT-Mini
    i2s_stream_cfg_t i2s_cfg = I2S_STREAM_CFG_DEFAULT_WITH_TYLE_AND_CH(CODEC_ADC_I2S_PORT, 48000, 16, AUDIO_STREAM_READER, 1);
    i2s_cfg.type = AUDIO_STREAM_READER;
    audio_element_handle_t i2s_stream_reader = i2s_stream_init(&i2s_cfg);

    ESP_LOGI(TAG, "Create TCP stream to send data to Mac");
    tcp_stream_cfg_t tcp_cfg = TCP_STREAM_CFG_DEFAULT();
    tcp_cfg.type = AUDIO_STREAM_WRITER;
    tcp_cfg.host = CONFIG_TCP_URL; 
    tcp_cfg.port = CONFIG_TCP_PORT;
    audio_element_handle_t tcp_stream_writer = tcp_stream_init(&tcp_cfg);

    ESP_LOGI(TAG, "Register elements and link pipeline");
    audio_pipeline_register(pipeline, i2s_stream_reader, "i2s");
    audio_pipeline_register(pipeline, tcp_stream_writer, "tcp");

    const char *link_tag[2] = {"i2s", "tcp"};
    audio_pipeline_link(pipeline, &link_tag[0], 2);

    ESP_LOGI(TAG, "Start audio pipeline");
    audio_pipeline_run(pipeline);

    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }
}