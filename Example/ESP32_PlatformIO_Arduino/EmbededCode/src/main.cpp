#include <Arduino.h>
#include <ModbusRTU.h>
#include "ecm_1.h"

void modbus_comm(void *pt)
{
    while (1)
    {
        mb.task();
        vTaskDelay(50);
    }
}

void test_send(void *pt)
{
    uint32_t i = 0;
    while (1)
    {
        modbusWrite(M_test01,i);
        modbusWrite(M_test02,i);
        modbusWrite(M_test03,i);
        modbusWrite(M_test04,i);
        i++;
        vTaskDelay(1000);
    }
}


void setup()
{
    Serial.begin(115200, SERIAL_8N1);
    Serial.println("hello world");
    mb.begin(&Serial);
    modbusRTUConfig();
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

