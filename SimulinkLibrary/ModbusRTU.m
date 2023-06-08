classdef ModbusRTU < handle    
    properties
        % 串口相关的参数
        serialConfig = struct(...
            'port', 'COM12', ...
            'baudRate', 115200);
        % 和modbus相关的参数
        msgConfig = struct();
        % modbus连接的句柄
        modbusHandle = 0;
    end

    methods
        %% 设置串口相关的参数，并初始化modbus连接
        function setSerial(obj, port, baudRate)
            obj.serialConfig.port = port;
            obj.serialConfig.baudRate = baudRate;
        end

        %% 设置modbus连接信息
        % parmValue = gain * trueValue + bias
        % 默认以 uint32 传输
        function setModbusMsg(obj, config_file)
            %% 以 csv形式存储配置文件
            % config = readcell(config_file);
            % [msgNum, ~] = size(config);
            % for i = 2:msgNum
            %     obj.msgConfig = setfield(obj.msgConfig,cell2mat(config(i,1)),...
            %         struct(...
            %             'slaveID', cell2mat(config(i,2)), ...
            %             'address', cell2mat(config(i,3)) + 1, ...
            %             'gain'   , cell2mat(config(i,4)), ...
            %             'bias'   , cell2mat(config(i,5)) ));
            % end

            %% 以json存储
            config = loadjson(config_file);
            obj.setSerial(config.port, config.baudRate);
            obj.msgConfig = config.msgConfig;
        end

        %% 启动modbus连接
        function beginModbusRTU(obj)
            obj.modbusHandle = modbus('serialrtu',obj.serialConfig.port,'BaudRate',obj.serialConfig.baudRate);
            try
                parm_name = fields(obj.msgConfig);
                disp("Try Connect")
                obj.read( cell2mat(parm_name(1)) );
            catch
            end
        end


        %% 读数
        function trueValue = read(obj, parmName)
            parmCongig = getfield(obj.msgConfig, parmName);
            parmValue = read(obj.modbusHandle, 'holdingregs', parmCongig.address+1, 1, parmCongig.slaveID, 'uint16');
            trueValue = (parmValue - parmCongig.bias) / parmCongig.gain;
        end
        
        %% 写数据
        function write(obj, parmName, trueValue)
            parmCongig = getfield(obj.msgConfig, parmName);
            parmValue = round( parmCongig.gain * trueValue + parmCongig.bias );
            write(obj.modbusHandle, 'holdingregs', parmCongig.address+1, parmValue, parmCongig.slaveID, 'uint16');
            
        end


    end
end