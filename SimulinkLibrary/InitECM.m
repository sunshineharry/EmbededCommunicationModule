modbus_rtu = ModbusRTU();
modbus_rtu.setModbusMsg( input("configFile: ","s") );
modbus_rtu.beginModbusRTU();
