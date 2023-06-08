#include "ecm_1.h"
MsgConfig msgConfigs[MODBUS_MSG_LEN];
ModbusRTU mb;

uint16_t modbusRead(uint16_t parmName)
{
    return mb.Hreg( (msgConfigs[parmName].address-msgConfigs[parmName].bias)/msgConfigs[parmName].gain);
}

bool modbusWrite(uint16_t parmName, uint16_t value)
{
    return mb.Hreg(msgConfigs[parmName].address,value*msgConfigs[parmName].gain+msgConfigs[parmName].bias);
}

void modbusRTUConfig()
{
    mb.slave(SLAVE_ID);
    msgConfigs[0].address = 0;
    msgConfigs[0].gain = 1;
    msgConfigs[0].bias = 0;
    msgConfigs[1].address = 1;
    msgConfigs[1].gain = 1;
    msgConfigs[1].bias = 0;
    msgConfigs[2].address = 2;
    msgConfigs[2].gain = 1;
    msgConfigs[2].bias = 0;
    msgConfigs[3].address = 3;
    msgConfigs[3].gain = 1;
    msgConfigs[3].bias = 0;

    for(int i=0; i<MODBUS_MSG_LEN; i++){
        mb.addHreg(msgConfigs[i].address);
    }
}
