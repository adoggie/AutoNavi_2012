#define Uart4_OnePocketLength	12	//一个数据包的字节数
#define Uart4_BufSize		3 * Uart4_OnePocketLength	//串口缓冲区预留3个数据包的长度
#define Usart3_OnePocketLength	26	//一个数据包的字节数
#define Usart3_BufSize		3 * Usart3_OnePocketLength	//串口缓冲区预留3个数据包的长度
#define Header_Pocket		0x2A
#define Ender_Pocket			0x2E


#define DataPocket_Temperature		0x81
#define DataPocket_FuelSetInitial		0x90
#define DataPocket_FuelRequire		0x91


#define Size_DataPocket				0x40//存储包的字节大小
#define Size_OneFlashSize			0x200000//	Flash存储器大小
#define Max_DataPocketNumber		Size_OneFlashSize / Size_DataPocket	//能保存的最大包数
#define Size_FlashErase				0x8000



#define App_TemperatureToCollectNSecond		10	//默认测试温度时间5s
#define App_FuelToCollectNSecond		10	//默认测试温度时间5s
#define App_AnalogToCollectNSecond		10	//默认测试温度时间5s

#define App_CheckConnectTime 				10	//查询连接状态时间间隔

#define App_HeartbeatPocketTime		300	//心跳包时间间隔





#define Size_GSM_ReceiveBuf		200					// GSM模块输出的所有数据的数据缓冲区大小
#define Size_GSM_TCPTextBuf		200					// 包含*RS   .....   #  的指令，ascii码形式，需要转换
#define Size_GSM_TCPText		200					// 包含*RS   .....   #  的指令，进行指令处理
#define Size_GSM_MessageText	200					// GPRS 发送下来的短消息，要存储到LCD 上面
#define Size_GSM_GPRSCommand_IPTCPSend	200		// TCP 包发送
#define Size_GSM_GPRSCommand_IPUDPSend	240		// UDP 包发送，目前最大的是油耗包

#define Size_GSM_GPRSTCPPocketToSend	200
#define Size_GSM_GPRSUDPPocketToSend	96		//最大的udp包数据为96字节



void Delay1ms (int ms);

void Delay1us (int us);

void GPS_DataProcess(void);
unsigned char TemperatureDataCheck(void);
void TemperatureDataChange(void);