import numpy as np
import pandas as pd
import json
import os

ECM_H_Header = """
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

"""

ECM_CPP_Header = """
ModbusRTU mb;

uint16_t modbusRead(uint16_t parmName)
{
    return mb.Hreg( (msgConfigs[parmName].address-msgConfigs[parmName].bias)/msgConfigs[parmName].gain);
}

bool modbusWrite(uint16_t parmName, double value)
{
    return mb.Hreg(msgConfigs[parmName].address, (uint16_t)(value*msgConfigs[parmName].gain+msgConfigs[parmName].bias+0.5));
}

void modbusRTUConfig()
{
    mb.slave(SLAVE_ID);
"""

ECM_CPP_Tail = """
    for(int i=0; i<MODBUS_MSG_LEN; i++){
        mb.addHreg(msgConfigs[i].address);
    }
}
"""


class CoderGenerater(object):
    def __init__(self, file_path) -> None:
        self.dirname, filename = os.path.split(file_path)
        # 读 Json 文件
        with open(file_path, 'r') as config_file:
            config = json.load(config_file)
            msgConfig = pd.DataFrame(config['msgConfig']).T
            self.groupmsgConfigs = []
            for i in msgConfig.groupby('slaveID'):
                self.groupmsgConfigs.append(i)
        # 创建文件夹
        if not os.path.exists(os.path.join(self.dirname, "auto_code_gen")):
            os.mkdir(os.path.join(self.dirname, "auto_code_gen"))

    def write_file(self):
        # 写头文件
        for i in self.groupmsgConfigs:
            slaveID, msg = i
            with open(os.path.join(self.dirname, "auto_code_gen", "ecm_"+str(slaveID)+".h"), "w") as h_file:
                h_file.write(ECM_H_Header)
                h_file.write("#define SLAVE_ID " + str(slaveID) + "\n\n")
                h_file.write("// Define the parms\n")
                parm_num = 0
                h_file.write("#define MODBUS_MSG_LEN " +
                             str(len(msg.index)) + "\n")
                for parm_name in msg.index:
                    h_file.write("#define " + parm_name +
                                 " " + str(parm_num) + "\n")
                    parm_num += 1

        # 写cpp文件
        for i in self.groupmsgConfigs:
            slaveID, msg = i
            with open(os.path.join(self.dirname, "auto_code_gen", "ecm_"+str(slaveID)+".cpp"), "w") as c_file:
                c_file.write('#include "ecm_' + str(slaveID) + '.h"\n')
                c_file.write("MsgConfig msgConfigs[MODBUS_MSG_LEN];")
                c_file.write(ECM_CPP_Header)
                parm_num = 0
                for parm_name in msg.index:
                    c_file.write(
                        "    msgConfigs[" + str(parm_num) + "].address = " + str(msg["address"][parm_num]) + ";\n")
                    c_file.write(
                        "    msgConfigs[" + str(parm_num) + "].gain = " + str(msg["gain"][parm_num]) + ";\n")
                    c_file.write(
                        "    msgConfigs[" + str(parm_num) + "].bias = " + str(msg["bias"][parm_num]) + ";\n")
                    parm_num += 1
                c_file.write(ECM_CPP_Tail)


if __name__ == "__main__":
    code_gen = CoderGenerater(input('Input filepath of modbus_config.json:\n'))
    code_gen.write_file()
