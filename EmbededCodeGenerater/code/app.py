import streamlit as st
import json
import os
import pandas as pd
import numpy as np
from st_aggrid import AgGrid
import time

TEMPFile = """
{
    "port": "COM1",
    "baudRate": 115200,
    "msgConfig": {
        "ECMtest01": {
            "slaveID": 1,
            "address": 0,
            "gain": 1,
            "bias": 0
        }
    }
}
"""

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



class StreamlitApp():
    def __init__(self) -> None:
        # 系统参数
        pass
        
    def start(self):
        # 页面标题
        st.title("ECM 配置界面")
        st.write("> Note: 你可以使用本项目，自动生成多个嵌入式设备和Simulink代码，快速构建Simulink和多个嵌入式设备的交互程序。")
        # 侧边栏
        st.sidebar.title("配置选项")
        # self.slaveNum = st.sidebar.number_input("请输入从机个数",value=1)
        self.filePath = st.sidebar.text_input("请输入文件保存路径",value=os.getcwd())
        # 读取配置
        if not os.path.exists( os.path.join(self.filePath, "modbus_config.json") ):
            with open(os.path.join(self.filePath, "modbus_config.json"), "w") as json_file:
                json_file.write(TEMPFile)

        with open(os.path.join(self.filePath, "modbus_config.json"), "r") as json_file:
            self.modbus_config = json.load(json_file)

        # 继续显示页面
        # radio_avilable = ["基础配置"] +["从机"+str(i) for i in range(1, self.slaveNum+1)]
        radio_avilable = ["基础配置"] + ["从机配置"] + ["配置完成导出"]
        self.conf_choose = st.sidebar.radio(
            "请选择需要配置的参数",
            tuple(radio_avilable),
        )
        if self.conf_choose == "基础配置":
            self.base_config()
        if self.conf_choose == "从机配置":
            self.msg_config()
        if self.conf_choose == "配置完成导出":
            self.finish_conf()

        # if st.sidebar.button("配置完成"):
            

    def finish_conf(self):
        code_gen = CoderGenerater(os.path.join(self.filePath, "modbus_config.json"))
        code_gen.write_file()
        st.write("## 成功导出配置文件！系统在5s后关闭")
        time.sleep(5)
        st.stop()
        


    def base_config(self):
        st.write("## 基础配置") 
        with st.form("base_conf"):
            port = st.text_input("请输入端口号", value=self.modbus_config["port"])
            baudRate = st.number_input("请输入波特率",value=self.modbus_config["baudRate"])
            if st.form_submit_button("Submit"):
                self.modbus_config["port"] = port
                self.modbus_config["baudRate"] = baudRate
                with open(os.path.join(self.filePath, "modbus_config.json"), "w") as json_file:
                    json_file.write(json.dumps(self.modbus_config , indent=4))

    def msg_config(self):
        st.write("## 从机配置")
        
        msgConfig = pd.DataFrame(self.modbus_config['msgConfig']).T
        msgConfig.insert(0, 'parmName', msgConfig.index)
        # msgConfig = msgConfig.reindex(['parmName', 'slaveID', 'address', 'gain', 'bias'])
        msgLen = len(msgConfig)

        nan_df = pd.DataFrame(np.nan, index=np.arange(50), columns=msgConfig.columns)
        msgConfig = msgConfig.append(nan_df, ignore_index=True)
        # msgConfig['parmName'] = msgConfig.index
        # msgConfig = msgConfig['parmName', 'slaveID', 'address', 'gain', 'bias']
        parmNum = st.number_input("请输入总变量个数",value=msgLen)
        with st.form("modbus_conf"):
            msgConfig = AgGrid(
                msgConfig[:parmNum],
                editable=True
            )
            print(msgConfig)
            msgConfig["data"].set_index('parmName', inplace = True)
            msgConfigNew = json.loads(msgConfig["data"].to_json(orient='index'))
            self.modbus_config["msgConfig"] = msgConfigNew
            if st.form_submit_button("Submit"):           
                with open(os.path.join(self.filePath, "modbus_config.json"), "w") as json_file:
                    json_file.write(json.dumps(self.modbus_config , indent=4))
        # parmNum = st.number_input("请输入总变量个数",value=1)
        # msgConfig = AgGrid(
        #     pd.DataFrame(columns=['parmName', 'slaveID', 'address', 'gain', 'bias'], index=range(1,parmNum+1)),
        #     editable=True
        # )
        # msgConfig["data"].set_index('parmName', inplace = True)
        # msgConfigNew = json.loads(msgConfig["data"].to_json(orient='index'))
        # self.modbus_config["msgConfig"] = msgConfigNew

                #     with open(os.path.join(self.filePath, "modbus_config.json"), "w") as json_file:
                #         json_file.write(json.dumps(self.modbus_config , indent=4))


if __name__ == "__main__":
    streamlit_app = StreamlitApp()
    streamlit_app.start()
    
