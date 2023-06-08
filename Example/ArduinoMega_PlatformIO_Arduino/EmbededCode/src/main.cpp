#include <Arduino.h>
#include <Arduino_FreeRTOS.h>
// #include "ecm_1.h"


void modbus_comm(void *pt)
{
    while (1)
    {
        analogWrite(8,2000);
        vTaskDelay(1000);
    }
}

void test_send(void *pt)
{
    uint32_t i = 0;
    while (1)
    {
        Serial.println("hello world");
        vTaskDelay(1000);
    }
}


void setup()
{
    Serial.begin(9600, SERIAL_8N1);
    Serial.println("111hello world");
    // mb.begin(&Serial);
    // mb.setBaudrate(9600);
    // modbusRTUConfig();
    xTaskCreate(modbus_comm,
                "ModbusComm",
                1024,
                NULL,
                2,
                NULL);
    xTaskCreate(test_send,
                "test_send",
                1024,
                NULL,
                1,
                NULL);
}

void loop()
{
    ;
}

