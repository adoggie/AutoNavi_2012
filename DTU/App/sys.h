#define Uart4_OnePocketLength	12	//һ�����ݰ����ֽ���
#define Uart4_BufSize		3 * Uart4_OnePocketLength	//���ڻ�����Ԥ��3�����ݰ��ĳ���
#define Usart3_OnePocketLength	26	//һ�����ݰ����ֽ���
#define Usart3_BufSize		3 * Usart3_OnePocketLength	//���ڻ�����Ԥ��3�����ݰ��ĳ���
#define Header_Pocket		0x2A
#define Ender_Pocket			0x2E


#define DataPocket_Temperature		0x81
#define DataPocket_FuelSetInitial		0x90
#define DataPocket_FuelRequire		0x91


#define Size_DataPocket				0x40//�洢�����ֽڴ�С
#define Size_OneFlashSize			0x200000//	Flash�洢����С
#define Max_DataPocketNumber		Size_OneFlashSize / Size_DataPocket	//�ܱ����������
#define Size_FlashErase				0x8000



#define App_TemperatureToCollectNSecond		10	//Ĭ�ϲ����¶�ʱ��5s
#define App_FuelToCollectNSecond		10	//Ĭ�ϲ����¶�ʱ��5s
#define App_AnalogToCollectNSecond		10	//Ĭ�ϲ����¶�ʱ��5s

#define App_CheckConnectTime 				10	//��ѯ����״̬ʱ����

#define App_HeartbeatPocketTime		300	//������ʱ����





#define Size_GSM_ReceiveBuf		200					// GSMģ��������������ݵ����ݻ�������С
#define Size_GSM_TCPTextBuf		200					// ����*RS   .....   #  ��ָ�ascii����ʽ����Ҫת��
#define Size_GSM_TCPText		200					// ����*RS   .....   #  ��ָ�����ָ���
#define Size_GSM_MessageText	200					// GPRS ���������Ķ���Ϣ��Ҫ�洢��LCD ����
#define Size_GSM_GPRSCommand_IPTCPSend	200		// TCP ������
#define Size_GSM_GPRSCommand_IPUDPSend	240		// UDP �����ͣ�Ŀǰ�������ͺİ�

#define Size_GSM_GPRSTCPPocketToSend	200
#define Size_GSM_GPRSUDPPocketToSend	96		//����udp������Ϊ96�ֽ�



void Delay1ms (int ms);

void Delay1us (int us);

void GPS_DataProcess(void);
unsigned char TemperatureDataCheck(void);
void TemperatureDataChange(void);