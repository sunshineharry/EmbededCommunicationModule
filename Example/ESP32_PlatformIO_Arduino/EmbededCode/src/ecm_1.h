
// If use Platform IO, you should include Arduino.h
#include <Arduino.h>
#include <ModbusRTU.h>

// Make the mb global
extern ModbusRTU mb;

// Define the struct of Msg
typedef struct s_MsgConfig
{
    uint16_t address;
    uint16_t gain;
    uint16_t bias;
}MsgConfig;

void modbusRTUConfig();
uint16_t modbusRead(uint16_t parmName);
bool modbusWrite(uint16_t parmName, uint16_t value);

// Define the Slave ID

#define SLAVE_ID 1

// Define the parms
#define MODBUS_MSG_LEN 4
#define ECMtest01 0
#define ECMtest02 1
#define ECMtest03 2
#define ECMtest04 3
