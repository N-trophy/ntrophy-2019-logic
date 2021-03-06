/* N-trphy 2019 final task:
   Allows to send data between 2 ESPs (buttons -> LEDs)
   This code is inspired by ESP32 TCP client example.
*/
#include <string.h>
#include <sys/param.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/queue.h"
#include "freertos/event_groups.h"
#include "driver/gpio.h"
#include "driver/ledc.h"
#include "driver/mcpwm.h"
#include "soc/mcpwm_reg.h"
#include "soc/mcpwm_struct.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event_loop.h"
#include "esp_log.h"
#include "nvs_flash.h"

#include "lwip/err.h"
#include "lwip/sockets.h"
#include "lwip/sys.h"
#include <lwip/netdb.h>

#define EXAMPLE_WIFI_SSID "Ntrophy"
#define EXAMPLE_WIFI_PASS "ruzovouckyslon"
const char* HOST_IP_ADDR = "192.168.0.60";
uint16_t host_port = 2000;

#define GPIO_LED_R 22
#define GPIO_LED_Y 23
#define GPIO_LED_G 17
#define GPIO_LED_B 5
#define GPIO_RGB_R 4
#define GPIO_RGB_G 21
#define GPIO_RGB_B 16
#define GPIO_BTN1 15
#define GPIO_BTN2 0
#define GPIO_BEEP 19

size_t GPIO_OUTS[] = {
	GPIO_LED_R,
	GPIO_LED_Y,
	GPIO_LED_G,
	GPIO_LED_B,
	GPIO_RGB_R,
	GPIO_RGB_G,
	GPIO_RGB_B,
};

size_t PORT_GPIO[] = {26, 27, 14};

/* FreeRTOS event group to signal when we are connected & ready to make a request */
static EventGroupHandle_t wifi_event_group;
static int sock = -1;

const int IPV4_GOTIP_BIT = BIT0;
const int IPV6_GOTIP_BIT = BIT1;

static const char *TAG = "N-trophy";
volatile uint64_t rgb_led_timeout = UINT64_MAX;
volatile uint64_t normal_led_timeout = UINT64_MAX;
const uint64_t LED_BLINK_TIME = 800000; // 800 ms

static void data_received(char rx_buf[]) {
	if (rx_buf[0] == '0' || rx_buf[0] == '1') {
		gpio_set_level(GPIO_RGB_B, 0);
		gpio_set_level(GPIO_RGB_G, 0);
		rgb_led_timeout = esp_timer_get_time() + LED_BLINK_TIME;

		if (rx_buf[0] == '0')
			gpio_set_level(GPIO_RGB_B, 1);
		if (rx_buf[0] == '1')
			gpio_set_level(GPIO_RGB_G, 1);
	}
}

static void led_keep_alive(void* arg) {
	while (1) {
		if (sock > -1) {
			gpio_set_level(GPIO_LED_R, 1);
			vTaskDelay(5/portTICK_PERIOD_MS);
			gpio_set_level(GPIO_LED_R, 0);
			vTaskDelay(10/portTICK_PERIOD_MS);
		} else {
			vTaskDelay(1000/portTICK_PERIOD_MS);
		}
	}
	vTaskDelete(NULL);
}

static void sock_keep_alive(void* arg) {
	while (1) {
		if (sock > -1)
			send(sock, "K", 1, 0);
		vTaskDelay(5000/portTICK_PERIOD_MS);
	}
	vTaskDelete(NULL);
}

static esp_err_t event_handler(void *ctx, system_event_t *event) {
	switch (event->event_id) {
	case SYSTEM_EVENT_STA_START:
		esp_wifi_connect();
		ESP_LOGI(TAG, "SYSTEM_EVENT_STA_START");
		break;
	case SYSTEM_EVENT_STA_CONNECTED:
		/* enable ipv6 */
		tcpip_adapter_create_ip6_linklocal(TCPIP_ADAPTER_IF_STA);
		break;
	case SYSTEM_EVENT_STA_GOT_IP:
		xEventGroupSetBits(wifi_event_group, IPV4_GOTIP_BIT);
		ESP_LOGI(TAG, "SYSTEM_EVENT_STA_GOT_IP");
		break;
	case SYSTEM_EVENT_STA_DISCONNECTED:
		/* This is a workaround as ESP32 WiFi libs don't currently auto-reassociate. */
		esp_wifi_connect();
		xEventGroupClearBits(wifi_event_group, IPV4_GOTIP_BIT);
		xEventGroupClearBits(wifi_event_group, IPV6_GOTIP_BIT);
		break;
	case SYSTEM_EVENT_AP_STA_GOT_IP6:
		xEventGroupSetBits(wifi_event_group, IPV6_GOTIP_BIT);
		ESP_LOGI(TAG, "SYSTEM_EVENT_STA_GOT_IP6");

		char *ip6 = ip6addr_ntoa(&event->event_info.got_ip6.ip6_info.ip);
		ESP_LOGI(TAG, "IPv6: %s", ip6);
	default:
		break;
	}
	return ESP_OK;
}

static void initialise_wifi(void) {
	tcpip_adapter_init();
	wifi_event_group = xEventGroupCreate();
	ESP_ERROR_CHECK( esp_event_loop_init(event_handler, NULL) );
	wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
	ESP_ERROR_CHECK( esp_wifi_init(&cfg) );
	ESP_ERROR_CHECK( esp_wifi_set_storage(WIFI_STORAGE_RAM) );
	wifi_config_t wifi_config = {
		.sta = {
			.ssid = EXAMPLE_WIFI_SSID,
			.password = EXAMPLE_WIFI_PASS,
		},
	};
	ESP_LOGI(TAG, "Setting WiFi configuration SSID %s...", wifi_config.sta.ssid);
	ESP_ERROR_CHECK( esp_wifi_set_mode(WIFI_MODE_STA) );
	ESP_ERROR_CHECK( esp_wifi_set_config(ESP_IF_WIFI_STA, &wifi_config) );
	ESP_ERROR_CHECK( esp_wifi_start() );
}

static void wait_for_ip() {
	uint32_t bits = IPV4_GOTIP_BIT | IPV6_GOTIP_BIT ;

	ESP_LOGI(TAG, "Waiting for AP connection...");
	xEventGroupWaitBits(wifi_event_group, bits, false, true, portMAX_DELAY);
	ESP_LOGI(TAG, "Connected to AP");
}

static void tcp_client_task(void *pvParameters) {
	wait_for_ip();

	gpio_set_level(GPIO_LED_B, 0);
	gpio_set_level(GPIO_LED_G, 0);

	char rx_buffer[128];
	char addr_str[128];
	int addr_family;
	int ip_protocol;

	while (1) {
		struct sockaddr_in destAddr;
		destAddr.sin_addr.s_addr = inet_addr(HOST_IP_ADDR);
		destAddr.sin_family = AF_INET;
		destAddr.sin_port = htons(host_port);
		addr_family = AF_INET;
		ip_protocol = IPPROTO_IP;
		inet_ntoa_r(destAddr.sin_addr, addr_str, sizeof(addr_str) - 1);

		int err = 0;
		do {
			gpio_set_level(GPIO_LED_Y, 1);
			gpio_set_level(GPIO_LED_R, 1);

			sock = socket(addr_family, SOCK_STREAM, ip_protocol);
			if (sock < 0) {
				ESP_LOGE(TAG, "Unable to create socket: errno %d", errno);
				vTaskDelay(1000 / portTICK_PERIOD_MS);
				continue;
			}
			ESP_LOGI(TAG, "Socket created");

			err = connect(sock, (struct sockaddr *)&destAddr, sizeof(destAddr));
			if (err != 0) {
				ESP_LOGE(TAG, "Socket unable to connect: errno %d", errno);
				vTaskDelay(1000 / portTICK_PERIOD_MS);
			}

		} while (sock < 0 && err != 0);
		ESP_LOGI(TAG, "Successfully connected");
		gpio_set_level(GPIO_LED_Y, 0);

		while (1) {
			int len = recv(sock, rx_buffer, sizeof(rx_buffer) - 1, 0);
			// Error occured during receiving
			if (len < 0) {
				ESP_LOGE(TAG, "recv failed: errno %d", errno);
				break;
			}
			// Data received
			else {
				rx_buffer[len] = 0; // Null-terminate whatever we received and treat like a string
				ESP_LOGI(TAG, "Received %d bytes from %s: %s", len, addr_str, rx_buffer);
				data_received(rx_buffer);
			}

			vTaskDelay(20 / portTICK_PERIOD_MS);
		}

		if (sock != -1) {
			ESP_LOGE(TAG, "Shutting down socket and restarting...");
			shutdown(sock, 0);
			close(sock);
		}
	}
	vTaskDelete(NULL);
}

static void button_task(void* arg) {
	static int btn1_cnt = 0;
	static int btn2_cnt = 0;
	const size_t no_ticks = 5; // 50 ms

	gpio_set_level(GPIO_LED_B, 1);
	vTaskDelay(200 / portTICK_PERIOD_MS);
	gpio_set_level(GPIO_LED_G, 1);
	vTaskDelay(200 / portTICK_PERIOD_MS);
	gpio_set_level(GPIO_LED_Y, 1);
	vTaskDelay(200 / portTICK_PERIOD_MS);
	gpio_set_level(GPIO_LED_R, 1);
	vTaskDelay(200 / portTICK_PERIOD_MS);

	while (1) {
		if (gpio_get_level(GPIO_BTN1) == 0) {
			if (btn1_cnt >= 0)
				btn1_cnt++;
			if (btn1_cnt == no_ticks) {
				btn1_cnt = -1;
				if (sock >= 0)
					send(sock, "0", 1, 0);
				normal_led_timeout = esp_timer_get_time() + LED_BLINK_TIME;
				gpio_set_level(GPIO_LED_G, 0);
				gpio_set_level(GPIO_LED_B, 1);
			}
		} else {
			btn1_cnt = 0;
		}

		if (gpio_get_level(GPIO_BTN2) == 0) {
			if (btn2_cnt >= 0)
				btn2_cnt++;
			if (btn2_cnt == no_ticks) {
				btn2_cnt = -1;
				if (sock >= 0)
					send(sock, "1", 1, 0);
				normal_led_timeout = esp_timer_get_time() + LED_BLINK_TIME;
				gpio_set_level(GPIO_LED_G, 1);
				gpio_set_level(GPIO_LED_B, 0);
			}
		} else {
			btn2_cnt = 0;
		}

		if ((rgb_led_timeout < esp_timer_get_time()) &&
		    ((GPIO_REG_READ(GPIO_OUT_REG) >> GPIO_RGB_B) & 1u ||
			 (GPIO_REG_READ(GPIO_OUT_REG) >> GPIO_RGB_G & 1u))) {
			gpio_set_level(GPIO_RGB_B, 0);
			gpio_set_level(GPIO_RGB_G, 0);

			rgb_led_timeout = LONG_MAX;
		}

		if (normal_led_timeout < esp_timer_get_time() &&
		    ((GPIO_REG_READ(GPIO_OUT_REG) >> GPIO_LED_B) & 1u ||
			 (GPIO_REG_READ(GPIO_OUT_REG) >> GPIO_LED_G & 1u))) {
			gpio_set_level(GPIO_LED_B, 0);
			gpio_set_level(GPIO_LED_G, 0);
			normal_led_timeout = LONG_MAX;
		}

		vTaskDelay(10/portTICK_PERIOD_MS);
	}

	vTaskDelete(NULL);
}

static void initialise_io() {
	gpio_config_t io_conf;

	for (size_t i = 0; i < sizeof(GPIO_OUTS)/sizeof(*GPIO_OUTS); i++) {
		//gpio_pad_select_gpio(GPIO_OUTS[i]); TODO check if not required
		gpio_set_direction(GPIO_OUTS[i], GPIO_MODE_OUTPUT);
	}

	io_conf.intr_type = GPIO_PIN_INTR_DISABLE;
	io_conf.pin_bit_mask = (1ull << GPIO_BTN1);
	io_conf.mode = GPIO_MODE_INPUT;
	io_conf.pull_up_en = 1;
	io_conf.pull_down_en = 0;
	gpio_config(&io_conf);

	io_conf.intr_type = GPIO_PIN_INTR_DISABLE;
	io_conf.pin_bit_mask = (1ull << GPIO_BTN2);
	io_conf.mode = GPIO_MODE_INPUT;
	io_conf.pull_up_en = 1;
	io_conf.pull_down_en = 0;
	gpio_config(&io_conf);
}

uint16_t get_port() {
	for (size_t i = 0; i < sizeof(PORT_GPIO)/sizeof(*PORT_GPIO); i++) {
		gpio_set_direction(PORT_GPIO[i], GPIO_MODE_INPUT);
		gpio_set_pull_mode(PORT_GPIO[i], GPIO_PULLUP_ONLY);
	}

	uint16_t result = 2000;
	for (size_t i = 0; i < sizeof(PORT_GPIO)/sizeof(*PORT_GPIO); i++)
		if (!gpio_get_level(PORT_GPIO[i]))
			result += (1 << i);
	return result;
}

void app_main() {
	ESP_ERROR_CHECK(nvs_flash_init());
	host_port = get_port();
	ESP_LOGI(TAG, "Port %d", host_port);
	initialise_io();
	initialise_wifi();

	xTaskCreate(tcp_client_task, "tcp_client", 4096, NULL, 5, NULL);
	xTaskCreate(button_task, "button_task", 2048, NULL, 10, NULL);
	xTaskCreate(led_keep_alive, "led_keep_alive", 2048, NULL, 10, NULL);
	xTaskCreate(sock_keep_alive, "sock_keep_alive", 2048, NULL, 10, NULL);
}
