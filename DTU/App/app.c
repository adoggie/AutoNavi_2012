

#include <includes.h>



/*
*********************************************************************************************************
*                                       LOCAL GLOBAL VARIABLES
*********************************************************************************************************
*/

static  OS_STK         App_TaskStartStk[APP_TASK_START_STK_SIZE];
static  OS_STK         App_TaskGSMStk[APP_TASK_GSM_STK_SIZE];
static  OS_STK         App_TaskGPSStk[APP_TASK_GPS_STK_SIZE];
static  OS_STK         App_TaskKbdStk[APP_TASK_KBD_STK_SIZE];
static  OS_STK         App_TaskLEDStk[APP_TASK_LED_STK_SIZE];
static  OS_STK         App_TaskUSBStk[APP_TASK_USB_STK_SIZE]
	;
static  OS_STK         App_TaskMainStk[APP_TASK_MAIN_STK_SIZE];

OS_EVENT 		*App_Usart2_Rev_Q;
OS_EVENT 		*App_GPS_Rev_Q;
OS_EVENT      	*App_USBInterruptMbox;

void *App_GPS_RevData[10]; //定义一个指针数组

unsigned char USB_DataBuf[128];


//gsm
unsigned int App_CounterForCheckConnect,App_CounterForHeartbeatPocket;

//gsm


/*
*********************************************************************************************************
*                                      LOCAL FUNCTION PROTOTYPES
*********************************************************************************************************
*/

static  void  App_TaskCreate	(void);
static  void  App_EventCreate	(void);
static  void  App_TaskStart		(void *p_arg);
static  void  App_TaskGSM			(void        *p_arg);
static  void  App_TaskGPS			(void        *p_arg);
static  void  App_TaskKbd		(void *p_arg);
static  void  App_TaskLED		(void *p_arg);
static  void  App_TaskUSB		(void *p_arg);
void App_GPSDataProcess(void);

static  void  App_Main (void *p_arg);


///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
#define  DVR_BOOL char
#define DVR_TRUE 1
#define DVR_FALSE 0

#define MODULE_ID_SIZE 15 
#define TCPCMD_SIZE 4

#define SLEEP_SEC(x)  OSTimeDlyHMSM(0, 0, x,0) 

struct PolicyItem_t{
	FP32		x;			/*x,y,width,height*/
	FP32		y;
	FP32		width;
	FP32		height;	
	UINT16 	year;
	INT8U	mon;
	INT8U	day;
	INT8U	sd_slot;	
	INT8U	hour1;
	INT8U hour2;
	
	DVR_BOOL ok;

};

struct MsgReboot_t{
  char null;	
};

struct  Packet_t{
	INT16U 	seq; //16 bit
	char 		mid[MODULE_ID_SIZE]; 
	char 		cmd[TCPCMD_SIZE];	
	union content{
		struct PolicyItem_t policy;
		struct MsgReboot_t	reboot;
	};	
};

void print_policy(struct PolicyItem_t* p){
	char buf[128];
	sprintf(buf,"policy: [%f,%f,%f,%f],[%d-%d-%d,%d-%d],sd:%d\n",p->x,p->y,p->width,p->height,p->year,p->mon,p->day,
			p->hour1,p->hour2,p->sd_slot);
	USART1_SendStr(buf);
}

//@return :  DVR_TRUE if okay,else DVR_FALSE 
/*
DVR_BOOL parseMsg(char * msg,size_t size, struct Packet_t* pkt){
  return DVR_FALSE;
}
*/

DVR_BOOL parse_AP06(char *src,struct Packet_t *pkt)
{
	int p_count = 1;
	char *token = NULL;

	token = strtok(src,",");
	while (token != NULL)
	{
		switch (p_count)
		{
			case 1:
				pkt->policy.sd_slot = atoi(token);
				break;
			case 2:
				pkt->policy.x = atof(token);
				break;
			case 3:
				pkt->policy.y = atof(token);
				break;
			case 4:
				pkt->policy.width = atof(token);
				break;
			case 5:
				pkt->policy.height = atof(token);
				break;
			case 6:
				pkt->policy.year = atoi(token);
				break;
			case 7:
				pkt->policy.mon = atoi(token);
				break;
			case 8:
				pkt->policy.day = atoi(token);
				break;
			case 9:
				pkt->policy.hour1 = atoi(token);
				break;
			case 10:
				pkt->policy.hour2 = atoi(token);
				break;
		}
		token = strtok(NULL,",");
		p_count ++;
	}
	if (p_count == 11)
	{
		pkt->policy.ok = DVR_TRUE;
		print_policy(&pkt->policy);
	}else{
		pkt->policy.ok = DVR_FALSE;
	}
	return 	pkt->policy.ok;
	
/*
	else
	{
		pkt->content_type.policy.ok = DVR_FALSE;
		return DVR_FALSE;
	}
	*/
}

DVR_BOOL parse_AP05(char *src,struct Packet_t *pkt)
{
	return DVR_FALSE;
}

DVR_BOOL parseMsg(char *msg,size_t size,struct Packet_t *pkt)
{
	char msgbackup[100] = {0x00};
	strcpy(msgbackup,msg);
	char *token = NULL;
	char *p = NULL;
	int token_count = 1;

	//if (msgbackup[0] == '*' && msgbackup[size - 1] == '#')
        if ( msgbackup[size - 1] == '#')
	{
		msgbackup[size - 1] = 0x00;
		//token  = strtok(msgbackup + 1,",");
                token  = strtok(msgbackup,",");
		while (token != NULL)
		{
			switch (token_count)
			{
				case 1:
					pkt->seq = atoi(token);
					break;
				case 2:
					strncpy(pkt->mid,token,MODULE_ID_SIZE);
					break;
				case 3:
					strncpy(pkt->cmd,token,TCPCMD_SIZE);
					break;
			}
			if (token_count < 3)
				token = strtok(NULL,",");
			else
			{
				p = (token += 5);
				break;
			}
			token_count ++;
		}
		if (strncmp(pkt->cmd,"AP06",TCPCMD_SIZE) == 0)
			return parse_AP06(p,pkt);
		else if (strncmp(pkt->cmd,"AP05",TCPCMD_SIZE) == 0)
			return parse_AP05(p,pkt);
	}
	
	return DVR_FALSE;
}


struct SysTime_t{
		int 	year;
		int	mon;
		int	day;
		int	hour;
		int	min;
		int	sec;
};

struct BehaviorTime_t{
	UINT32  gps;
	UINT32  reg;
	UINT32  policy;
	UINT32 upload;	
};

struct AppSettings_t{
	//char 	hostclk_ok;		//主机时钟是否被设置
	char 	isregsvr; 			//是否已注册到平台
	struct PolicyItem_t policy;		
	struct  SysTime_t  hostime;

	//UINT32 gpstime;	//gps定位时间 最近一次 

	UINT32 sys_elapsed;	//系统流逝秒

	struct BehaviorTime_t	 btime;	

	UINT32	gps_freq;		//采集上传频率
	UINT32	policy_freq;	//获取策略时间频率
    UINT8   sdslot;		// 0 - 未启动dvr录像澹澹1-16
	FP32		lon;						//当前行驶位置
	FP32		lat;	

	char		mid[MODULE_ID_SIZE+1];			//设备模块编号
	UINT16 seq;				//系统流水

	char  datbuf[128];
	
};

static struct AppSettings_t gAppSettings;


void debug_log(char * fmt,...){
	static char  logbuf[200];
	va_list ap;
	va_start(ap,c);
	sprintf(logbuf,fmt,ap);
	va_end(ap);
	USART1_SendStr(logbuf);
}

void debug_log2(char * msg,size_t size){
	USART1_SendBytes((unsigned char*)msg,size);
}

void debug_log3(char * msg){
	USART1_SendStr(msg);
}


//os 每一秒触发一次
void AppTimerUpdate(){
  gAppSettings.sys_elapsed +=1;
}

//发送tcp数据，注意dat长度不能超越发送缓冲区大小
DVR_BOOL sendTcpData( char* dat){
	if ( GSM_GPRSTCPSendData !=0){
		return DVR_FALSE; //BUSY
	}
	strcpy((char*) GSM_GPRSTCPPocketToSend,dat);	
	GSM_GPRSTCPSendData = 1;

	return DVR_TRUE;
}


void doProcessTcpMsg(char * msg,size_t size){
	debug_log2(msg,size);
	DVR_BOOL cr;
	struct Packet_t pkt;
	cr = parseMsg(msg,size, &pkt);
	if(cr != DVR_TRUE){
			return ;
	}
	//模块编号错误
	if ( strncmp(pkt.mid,gAppSettings.mid,MODULE_ID_SIZE) !=0){
		debug_log("mid unmatched!\n");	
		return ;
	}
	//策略复制
	if( strncmp(pkt.cmd,"AP06",TCPCMD_SIZE) == 0){
		gAppSettings.policy = pkt.policy;
	}
		
}

///////////////////////////////////////////////////////////////////////////////




/*****************************************************************************
** 函数名称:		main 
**
** 函数功能:		c 入口代码
**
** 输入参数:		
**
** 输出参数:		None
**
** 返回参数：   None
*****************************************************************************/

int  main (void)
{
    CPU_INT08U  os_err;


    BSP_IntDisAll();                                            /* Disable all ints until we are ready to accept them.  */
    
    //NVIC_SetVectorTable(NVIC_VectTab_FLASH, 0x8000);// 中断向量映射
    
    
    OSInit();                                                   /* Initialize "uC/OS-II, The Real-Time Kernel".         */

    os_err = OSTaskCreateExt((void (*)(void *)) App_TaskStart,  /* Create the start task.                               */
                             (void          * ) 0,
                             (OS_STK        * )&App_TaskStartStk[APP_TASK_START_STK_SIZE - 1],
                             (INT8U           ) APP_TASK_START_PRIO,
                             (INT16U          ) APP_TASK_START_PRIO,
                             (OS_STK        * )&App_TaskStartStk[0],
                             (INT32U          ) APP_TASK_START_STK_SIZE,
                             (void          * )0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

#if (OS_TASK_NAME_SIZE >= 11)
    OSTaskNameSet(APP_TASK_START_PRIO, (CPU_INT08U *)"Start Task", &os_err);
#endif

    OSStart();                                                  /* Start multitasking (i.e. give control to uC/OS-II).  */

    return (0);
}


/*****************************************************************************
** 函数名称:		App_TaskStart
**
** 函数功能:		调用App_TaskCreate 建立任务 ，App_EventCreate 创建消息队列等
**
** 输入参数:		
**
** 输出参数:		None
**
** 返回参数：   None
*****************************************************************************/

static  void  App_TaskStart (void *p_arg)
{

    (void)p_arg;

    BSP_Init();                                                 /* Initialize BSP functions.                            */
    OS_CPU_SysTickInit();                                       /* Initialize the SysTick.                              */

#if (OS_TASK_STAT_EN > 0)
    OSStatInit();                                               /* Determine CPU capacity.                              */
#endif


    
    App_EventCreate();                                          /* Create application events.                           */
    App_TaskCreate();                                           /* Create application tasks.                            */

    while (DEF_TRUE){                                          /* Task body, always written as an infinite loop.       */
	OSTimeDlyHMSM(0, 0, 0, 800);
	BSP_Watchdog_Reset();
    }
}



/*****************************************************************************
** 函数名称:		App_EventCreate
**
** 函数功能:		创建消息队列等
**
** 输入参数:		
**
** 输出参数:		None
**
** 返回参数：   None
*****************************************************************************/

static  void  App_EventCreate (void)
{

 	//App_Usart2_Rev_Q = OSQCreate(&App_Usart2_RevData[0],50);//串口中断接收到的数据传给进程
	//App_Usart3_Rev_Q = OSQCreate(&App_Usart3_RevData[0],50);
	App_USBInterruptMbox = OSMboxCreate((void *)0);
	App_GPS_Rev_Q = OSQCreate(&App_GPS_RevData[0],10);//串口中断接收到的数据传给进程
}


/*****************************************************************************
** 函数名称:		App_TaskCreate
**
** 函数功能:		创建各个ucos 任务
**
** 输入参数:		
**
** 输出参数:		None
**
** 返回参数：   None
*****************************************************************************/

static  void  App_TaskCreate (void)
{
    CPU_INT08U  os_err;



	os_err = OSTaskCreateExt((void (*)(void *)) App_Main,
                             (void          * ) 0,
                             (OS_STK        * )&App_TaskMainStk[APP_TASK_MAIN_STK_SIZE - 1],
                             (INT8U           ) APP_TASK_MAIN_PRIO,
                             (INT16U          ) APP_TASK_MAIN_PRIO,
                             (OS_STK        * )&App_TaskMainStk[0],
                             (INT32U          ) APP_TASK_GSM_STK_SIZE,
                             (void          * ) 0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));


    os_err = OSTaskCreateExt((void (*)(void *)) App_TaskGSM,
                             (void          * ) 0,
                             (OS_STK        * )&App_TaskGSMStk[APP_TASK_GSM_STK_SIZE - 1],
                             (INT8U           ) APP_TASK_GSM_PRIO,
                             (INT16U          ) APP_TASK_GSM_PRIO,
                             (OS_STK        * )&App_TaskGSMStk[0],
                             (INT32U          ) APP_TASK_GSM_STK_SIZE,
                             (void          * ) 0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

#if (OS_TASK_NAME_SIZE >= 9)
    OSTaskNameSet(APP_TASK_GSM_PRIO, "GSM", &os_err);
#endif


    os_err = OSTaskCreateExt((void (*)(void *)) App_TaskGPS,
                             (void          * ) 0,
                             (OS_STK        * )&App_TaskGPSStk[APP_TASK_GPS_STK_SIZE - 1],
                             (INT8U           ) APP_TASK_GPS_PRIO,
                             (INT16U          ) APP_TASK_GPS_PRIO,
                             (OS_STK        * )&App_TaskGPSStk[0],
                             (INT32U          ) APP_TASK_GPS_STK_SIZE,
                             (void          * ) 0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

#if (OS_TASK_NAME_SIZE >= 9)
    OSTaskNameSet(APP_TASK_GSM_PRIO, "GPS", &os_err);
#endif


    os_err = OSTaskCreateExt((void (*)(void *)) App_TaskLED,
                             (void          * ) 0,
                             (OS_STK        * )&App_TaskLEDStk[APP_TASK_LED_STK_SIZE - 1],
                             (INT8U           ) APP_TASK_LED_PRIO,
                             (INT16U          ) APP_TASK_LED_PRIO,
                             (OS_STK        * )&App_TaskLEDStk[0],
                             (INT32U          ) APP_TASK_LED_STK_SIZE,
                             (void          * ) 0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

#if (OS_TASK_NAME_SIZE >= 9)
    OSTaskNameSet(APP_TASK_LED_PRIO, "LED", &os_err);
#endif



    os_err = OSTaskCreateExt((void (*)(void *)) App_TaskKbd,
                             (void          * ) 0,
                             (OS_STK        * )&App_TaskKbdStk[APP_TASK_KBD_STK_SIZE - 1],
                             (INT8U           ) APP_TASK_KBD_PRIO,
                             (INT16U          ) APP_TASK_KBD_PRIO,
                             (OS_STK        * )&App_TaskKbdStk[0],
                             (INT32U          ) APP_TASK_KBD_STK_SIZE,
                             (void          * ) 0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

#if (OS_TASK_NAME_SIZE >= 9)
    OSTaskNameSet(APP_TASK_KBD_PRIO, "KBD", &os_err);
#endif

/*
    os_err = OSTaskCreateExt((void (*)(void *)) App_TaskUSB,
                             (void          * ) 0,
                             (OS_STK        * )&App_TaskUSBStk[APP_TASK_USB_STK_SIZE - 1],
                             (INT8U           ) APP_TASK_USB_PRIO,
                             (INT16U          ) APP_TASK_USB_PRIO,
                             (OS_STK        * )&App_TaskUSBStk[0],
                             (INT32U          ) APP_TASK_USB_STK_SIZE,
                             (void          * ) 0,
                             (INT16U          )(OS_TASK_OPT_STK_CLR | OS_TASK_OPT_STK_CHK));

#if (OS_TASK_NAME_SIZE >= 9)
    OSTaskNameSet(APP_TASK_USB_PRIO, "USB", &os_err);
#endif
*/

}


/*****************************************************************************
** 函数名称:		App_TaskGSM
**
** 函数功能:		运行GSM模块的发送数据及建立连接等
**
** 输入参数:		
**
** 输出参数:		None
**
** 返回参数：   None
*****************************************************************************/

extern unsigned int GSM_SizeOfTCPCommand;

static  void  App_TaskGSM (void *p_arg)
{
	//CPU_INT08U  *msg;
	//CPU_INT08U   err,error;


	(void)p_arg;

		
	GSM_Reset();
	GSM_PowerUp();
	App_CounterForCheckConnect = App_CheckConnectTime;
	App_CounterForHeartbeatPocket = App_HeartbeatPocketTime;


	while (DEF_TRUE) 
	{
		if(App_CounterForCheckConnect >= App_CheckConnectTime)
		{
			App_CounterForCheckConnect = 0;			
			if(GSM_GPRSTCPConnect())
			{
				GSM_GPRSTCPConnected = 1;
			}
			
		}	
		if(App_CounterForHeartbeatPocket >= App_HeartbeatPocketTime)
		{
			
			if(GSM_GPRSTCPConnected)
			{
				App_CounterForHeartbeatPocket = 0;
				GSM_GPRSCreatHeartbeatPocket();
				GSM_GPRSTCPSendData = 1;//发送心跳包
			}
		}
		//test
		//strcpy(GSM_GPRSTCPPocketToSend,"*RS,8060624034,R4,20101010,01,C00,123456,13811134693#");
		//GSM_TCPReceiveFinish = 1;
		//test
		if(GSM_GPRSTCPSendData)
		{
			if(GSM_GPRSTCPConnected)
			{
				GSM_GPRSSendTCPPocket(GSM_GPRSTCPPocketToSend,strlen(GSM_GPRSTCPPocketToSend));
				GSM_GPRSTCPSendData = 0;
			}
		}
		
			//GSM_GPRSTCPConnect();
		if(GSM_TCPReceiveFinish)
		{ 
			GSM_TCPReceiveFinish = 0;
			GSM_TCPReceiveData();
			//GSM_TCPCommandProcess();
			//GSM_TCPText[GSM_SizeOfTCPCommand] 
			doProcessTcpMsg( (char*)GSM_TCPText,GSM_SizeOfTCPCommand );
		}			
       
		OSTimeDlyHMSM(0, 0, 3, 0);
	}
}


//void 

//写入gps文件
void  commitGpsToFile(){
	/*
	根据当前日期打开当天log文件，追加写入log
	*/ 
		char buf32[32];
		if(CH376DiskMount()==USB_INT_SUCCESS){

			BSP_LED_On(2);
                        
			UINT16 done;
                        strcpy(buf32,"/");
			strncat( buf32,GPS_DateBuf,6);
			strcat(buf32,".TXT");
                        
			if ( CH376FileOpen( buf32) ==USB_INT_SUCCESS){
				CH376ByteLocate(0xffffffff);
			}else{
				done = CH376FileCreate( buf32);
				if( done != USB_INT_SUCCESS){
					debug_log("open file failed...\n");
					//OSTimeDlyHMSM(0, 0, 2, 200);
					//continue;
					return;
				}
			}
			CH376ByteWrite( gAppSettings.datbuf,strlen(gAppSettings.datbuf),&done );
			CH376FileClose( TRUE );
			//debug_log("%s\n",gAppSettings.datbuf);
			//USART1_SendStr(gAppSettings.datbuf);
			//USART1_SendStr("\n");
			
			BSP_LED_Off(2);
		}
						

//		OSTimeDlyHMSM(0, 0, 4, 200);

}

UINT32 makeTimeStamp(struct SysTime_t* stime);

//将gps时间加8小时的时差
int GmtPlus8(int *year,int *month,int *day,int *hour)
{
	int y = *year;
	int m = *month;
	int d = *day;
	int h = *hour;

	int TIME_DIFF = 8;
	int month_day[12] = {31,28,31,30,31,30,31,31,30,31,30,31};

	if (!(h >= 0 && h <= 23 && d >= 1 && d <= 31 && m >= 1 && m <= 12 && y > 1000))
		return -1;

	if (h + TIME_DIFF > 23)
	{
		if (d == month_day[m - 1] && d <= month_day[m - 1])
		{
			switch (m)
			{
				case 2:	// 2月
					if (y % 10 == 0) // 以0结尾的闰年计算
					{
						if (y % 400 == 0) // 闰年
						{
							*day = d + 1;
							*hour = h + TIME_DIFF - 24;
						}
						else	// 非闰年
						{
							*month = m + 1;
							*day = 1;
							*hour = h + TIME_DIFF - 24;
						}
					}
					else // 非0结尾的闰年计算
					{
						if (y % 4 == 0 && y % 100 > 0) //闰年
						{
							*day = d + 1;
							*hour = h + TIME_DIFF - 24;
						}
						else // 非闰年
						{
							*month = m + 1;
							*day = 1;
							*hour = h + TIME_DIFF - 24;
						}
					}
					break;
				case 12: // 12月
					*year = y + 1;
					*month = 1;
					*day = 1;
					*hour = h + TIME_DIFF - 24;
					break;
				default: // 非2月、12月运算
					*month = m + 1;
					*day = 1;
					*hour = h + TIME_DIFF - 24;
			}
		}
		else
		{
			if (d >= month_day[m -1])
			{
				if (d == 29 && m == 2)  // 闰年2月29日+8计算
				{
					*month = 3;
					*day = 1;
					*hour = h + TIME_DIFF - 24;
				}
				else
					return -1;
			}
			*day = d + 1;
			*hour = h + TIME_DIFF - 24;
		}
	}
	else
		*hour = h + TIME_DIFF;
}


/*
250712,053921
*/
DVR_BOOL parseTime(char* ymd,char* hms,struct SysTime_t* stime){
	char  d[3];	

	strncpy(d,&ymd[0],2);
	stime->day = atoi(d);
	strncpy(d,&ymd[2],2);
	stime->mon = atoi(d);
	strncpy(d,&ymd[4],2);
	stime->year = atoi(d)+2000;

	strncpy(d,&hms[0],2);
	stime->hour = atoi(d);
	strncpy(d,&hms[2],2);
	stime->min = atoi(d);
	strncpy(d,&hms[4],2);
	stime->sec = atoi(d);
        
      //  char buf[64];	
       // sprintf(buf,"format:(%s,%s) %d-%d-%d %d\n",ymd,hms,stime->year,stime->mon,stime->day,stime->hour);
      //  debug_log(buf);	
        
     GmtPlus8(&stime->year,&stime->mon,&stime->day,&stime->hour);
     //   sprintf(buf,"format:(%s,%s) %d-%d-%d %d\n",ymd,hms,stime->year,stime->mon,stime->day,stime->hour);
      //  debug_log(buf);
    return DVR_TRUE;
}


//发送gps到远端服务器
void  commitGpsToRemote(){
	char buf[128];
	/*
        if(!gAppSettings.isregsvr){
		return ;
	}
        */
	//tick = makeTimeStamp(&gAppSettings.hostime);	
	if( gAppSettings.sys_elapsed - gAppSettings.btime.gps < gAppSettings.gps_freq) {
		return ;
	}
	if( GSM_GPRSTCPSendData != 0){	 //发送忙碌中
		return ;		
	}
	gAppSettings.btime.gps = gAppSettings.sys_elapsed; //记录gps数据包发送时间
	//构建gps传送数据包
	sprintf(buf,"*%04d,%s,BP09,%s#", gAppSettings.seq, gAppSettings.mid,gAppSettings.datbuf);
	strcpy((char*) GSM_GPRSTCPPocketToSend,buf);
	GSM_GPRSTCPSendData = 1;
}

/*
unsigned char Buf_GPS_Rev[100],Count_GPS_Rev,GPS_IsValidStatus,GPS_IsEastStatus,GPS_IsNorthStatus;
unsigned char GPS_LatitudeData[4],GPS_LongitudeData[5],GPS_SpeedData[3],GPS_SpeedAngleData[4];
unsigned char GPS_LatitudeBuf[9],GPS_LongitudeBuf[10],GPS_TimeBuf[6],GPS_DateBuf[6],GPS_SpeedBuf[6],GPS_AngleBuf[7],GPS_DataBuf[7];
*/
void commitGps(){
        char buf32[32];
	char * datbuf = gAppSettings.datbuf;
        datbuf[0]= '\0' ;
	strncat(datbuf,(char*)GPS_DateBuf,6);	strcat(datbuf,",");
        strncat(datbuf,(char*)GPS_TimeBuf,6);	strcat(datbuf,",");
	strncat(datbuf,(char*)GPS_LongitudeBuf,10);	strcat(datbuf,",");
	strncat(datbuf,(char*)GPS_LatitudeBuf,9);	strcat(datbuf,",");
	strncat(datbuf,(char*)GPS_SpeedBuf,6);	strcat(datbuf,",");
	strncat(datbuf,(char*)GPS_AngleBuf,7);	strcat(datbuf,",");
        sprintf(buf32,"%02d",gAppSettings.sdslot);
	strcat(datbuf,buf32);  // strcat(datbuf,"\n");


	//分解lon,lat       121233070,31104617
	strncpy(buf32,(char*)&GPS_LongitudeBuf[3],6);
	FP32 x,y;
	x = atof( buf32) /10000.00;
	GPS_LongitudeBuf[3]='\0';
        //FP32 t;
        //x = atof(GPS_LongitudeBuf);
	x = x/60. + atof((char*)GPS_LongitudeBuf);

	strncpy( buf32,(char*)&GPS_LatitudeBuf[2],6);	
	y = atof( buf32) /10000.00;
	GPS_LatitudeBuf[2]=0;
	y = y/60. + atof((char*)GPS_LatitudeBuf);

        if( x<70 || x >130 || y<10 || y>70){
          return ;
        }
        
	gAppSettings.lon = x;
	gAppSettings.lat = y;

	parseTime( (char*)GPS_DateBuf,(char*)GPS_TimeBuf,&gAppSettings.hostime);	
	
	commitGpsToFile();
	commitGpsToRemote();
}


/*****************************************************************************
** 函数名称:		App_TaskGPS
**
** 函数功能:		提取GPS坐标时间等数据
**
** 输入参数:		
**
** 输出参数:		None
**
** 返回参数：   None
*****************************************************************************/
static  void  App_TaskGPS (void *p_arg)
{
	CPU_INT08U  *msg;
	CPU_INT08U   err;


	(void)p_arg;


	

        Count_GPS_Rev = 0;
	while (DEF_TRUE) 
	{
		msg = OSQPend(App_GPS_Rev_Q,0,&err);
		if(err == OS_NO_ERR)
		{
			Buf_GPS_Rev[Count_GPS_Rev++] = *msg;
			
			if(Count_GPS_Rev >= 100)
			{
				Count_GPS_Rev = 0;				
			}

			if(Buf_GPS_Rev[Count_GPS_Rev - 1]  == '\r')	//结束符**
			{
				//USART1_SendBytes( Buf_GPS_Rev,Count_GPS_Rev);
                                Count_GPS_Rev = 0;
				
				
				App_GPSDataProcess();
				/* 
				1.将gps接收数据置于发送缓冲区
				2.将gps数据写入本地tf卡
				3.有效gps数据读取设置本地主机时间
				*/
				if( GPS_IsValidStatus ==  1){
					commitGps();
				}
				
			}			
		}       

	}
}


/*****************************************************************************
** 函数名称:		App_TaskLED
**
** 函数功能:		LED 进程，用以指示系统运行状态
**
** 输入参数:		
**
** 输出参数:		None
**
** 返回参数：   None
*****************************************************************************/
static  void  App_TaskLED (void *p_arg)
{
    //CPU_INT08U  *msg;
    //CPU_INT08U   err;
    //CPU_INT08U   nstate;
    unsigned char i;

    (void)p_arg;

	

    while (DEF_TRUE) {
	BSP_LED_On(1);
	OSTimeDlyHMSM(0, 0, 0, 200);
	BSP_LED_Off(1); 	
	OSTimeDlyHMSM(0, 0, 2, 0);  
	if(BSP_Get_ExtPwrSta())
	{	
		i = 0;
		for( i = 100 ; i < 25; i++)
		{
			BSP_LED_On(1);
			OSTimeDlyHMSM(0, 0, 0, 200);
			BSP_LED_Off(1); 	
			OSTimeDlyHMSM(0, 0, 0, 200); 
		}
		BSP_SYSPower_Off();
	}
	//else USART1_SendStr("22222 is ok\r\n");
	//if(BSP_Get_ExtPwrSta())USART1_SendStr("11111 is ok\r\n");
	//else USART1_SendStr("22222 is ok\r\n");	
	
    }
}



/*****************************************************************************
** 函数名称:		App_TaskKbd
**
** 函数功能:		
**
** 输入参数:		
**
** 输出参数:		None
**
** 返回参数：   None
*****************************************************************************/

static  void  App_TaskKbd (void *p_arg)
{

    (void)p_arg;
	


    while (DEF_TRUE) {


		

        OSTimeDlyHMSM(0, 0, 1, 0);

   
    }
}



/*****************************************************************************
** 函数名称:		App_TaskUSB
**
** 函数功能:		
**
** 输入参数:		
**
** 输出参数:		None
**
** 返回参数：   None
*****************************************************************************/
/*
static  void  App_TaskUSB (void *p_arg)
{

	UINT16 done;
	(void)p_arg;


	while (DEF_TRUE) 
	{				
		//debug_log("task usb cycle...");
		if(CH376DiskMount()==USB_INT_SUCCESS)
		{
			BSP_LED_On(2);
			OSTimeDlyHMSM(0, 0, 2, 0);		
			strcpy( (char*) USB_DataBuf, "Abc.TXT" );	
				
			CH376SetFileName(USB_DataBuf);
			if(CH376FileCreate(USB_DataBuf)==USB_INT_SUCCESS)
			{	
				CH376ByteWrite(USB_DataBuf,strlen(USB_DataBuf),&done);
				CH376FileClose( TRUE );
			}
			BSP_LED_Off(2);
		}
						

		OSTimeDlyHMSM(0, 0, 4, 200);


	}
}
*/

/*
static  void  App_TaskUSB (void *p_arg)
{

    int i,j,k;
    
    (void)p_arg;
    
    
    while (DEF_TRUE) 
    { 
        if(CH376DiskMount()==USB_INT_SUCCESS)
        {
        BSP_LED_On(2);
        OSTimeDlyHMSM(0, 0, 2, 0); 
        //strcpy( USB_DataBuf, "/123ab47.TXT" ); 
        
        //CH376SetFileName(USB_DataBuf);
        if(CH376FileCreate("/123AB47.TXT")==USB_INT_SUCCESS)
        { 
        CH376ByteWrite("USB_DataBufabcddd",13,0);        
        CH376FileClose( TRUE );
        }
        
        if(CH376FileCreate("/ab12345.TXT")==USB_INT_SUCCESS)
        { 
        CH376ByteWrite("USB_DataBufabcddd",13,0);        
        CH376FileClose( TRUE );
        }

        if(CH376FileCreate("/_ab12345.TXT")==USB_INT_SUCCESS)
        { 
        CH376ByteWrite("USB_DataBufabcddd",13,0);        
        CH376FileClose( TRUE );
        }

        if(CH376FileCreate("/ab1_2345.TXT")==USB_INT_SUCCESS)
        { 
        CH376ByteWrite("USB_DataBufabcddd",13,0);        
        CH376FileClose( TRUE );
        }
        
        BSP_LED_Off(2);
    }
    
    
    OSTimeDlyHMSM(0, 0, 20, 200);
    
    
    }
}

*/

DVR_BOOL  IsHostTimeValid(){
	if( gAppSettings.hostime.year == 0){
		return DVR_FALSE;					
	}
	return DVR_TRUE;
}


static  void  App_Main (void *p_arg)
{
//	UINT16 done;	
        memset(&gAppSettings,0,sizeof(gAppSettings) );
	gAppSettings.gps_freq = 10;				//10秒上传一次gps信息
	gAppSettings.policy_freq = 1 * 20;// 60;	//5分钟获取一次策略
	strncpy(gAppSettings.mid,"A001-0123456789",MODULE_ID_SIZE); // mid 长度15
	char buf[128];
	strcpy(GSM_ServerIP , "114.80.244.85");
	strcpy(GSM_ServerPort , "15800");
	
	while (DEF_TRUE) {				
		
		if ( DVR_FALSE == IsHostTimeValid()){
			SLEEP_SEC(4);
			continue;
		}		
			//准备获取策略
		 if( gAppSettings.sys_elapsed  - gAppSettings.btime.policy > gAppSettings.policy_freq){
			sprintf(buf,"*%04d,%s,BP06,%s#",gAppSettings.seq,gAppSettings.mid,gAppSettings.datbuf);
			if ( DVR_TRUE == sendTcpData(buf) ){
				gAppSettings.btime.policy = gAppSettings.sys_elapsed;
			}			
			debug_log("poligy get..\n");
		 }
		 if( gAppSettings.policy.ok == DVR_TRUE){
		 	
			if( gAppSettings.lon >= gAppSettings.policy.x && gAppSettings.lon <= gAppSettings.policy.x + gAppSettings.policy.width
					&& gAppSettings.lat >= gAppSettings.policy.y && gAppSettings.lat <= gAppSettings.policy.y + gAppSettings.policy.height
					&& gAppSettings.hostime.hour >= gAppSettings.policy.hour1 && gAppSettings.hostime.hour < gAppSettings.policy.hour2){
					if( gAppSettings.sdslot != gAppSettings.policy.sd_slot){
						BSP_DVRPower_Off();
						gAppSettings.sdslot = gAppSettings.policy.sd_slot;
						SLEEP_SEC(1);
						SD_Select(gAppSettings.sdslot);
						debug_log("switched slot:%d\n",gAppSettings.sdslot);
						SLEEP_SEC(1);
					}
					BSP_DVRPower_On();
					debug_log3("dvr power on..\n");
			}
					
			
		 }else{
		 	BSP_DVRPower_Off();
           gAppSettings.sdslot = 0;
			debug_log3("dvr power off..\n");
		 }
		 
       
		SLEEP_SEC(4);
	}
}



/*
*********************************************************************************************************
*********************************************************************************************************
*                                          uC/OS-II APP HOOKS
*********************************************************************************************************
*********************************************************************************************************
*/

#if (OS_APP_HOOKS_EN > 0)
/*
*********************************************************************************************************
*                                      TASK CREATION HOOK (APPLICATION)
*
* Description : This function is called when a task is created.
*
* Argument(s) : ptcb   is a pointer to the task control block of the task being created.
*
* Note(s)     : (1) Interrupts are disabled during this call.
*********************************************************************************************************
*/

void  App_TaskCreateHook (OS_TCB *ptcb)
{

}

/*
*********************************************************************************************************
*                                    TASK DELETION HOOK (APPLICATION)
*
* Description : This function is called when a task is deleted.
*
* Argument(s) : ptcb   is a pointer to the task control block of the task being deleted.
*
* Note(s)     : (1) Interrupts are disabled during this call.
*********************************************************************************************************
*/

void  App_TaskDelHook (OS_TCB *ptcb)
{
    (void)ptcb;
}

/*
*********************************************************************************************************
*                                      IDLE TASK HOOK (APPLICATION)
*
* Description : This function is called by OSTaskIdleHook(), which is called by the idle task.  This hook
*               has been added to allow you to do such things as STOP the CPU to conserve power.
*
* Argument(s) : none.
*
* Note(s)     : (1) Interrupts are enabled during this call.
*********************************************************************************************************
*/

#if OS_VERSION >= 251
void  App_TaskIdleHook (void)
{
}
#endif

/*
*********************************************************************************************************
*                                        STATISTIC TASK HOOK (APPLICATION)
*
* Description : This function is called by OSTaskStatHook(), which is called every second by uC/OS-II's
*               statistics task.  This allows your application to add functionality to the statistics task.
*
* Argument(s) : none.
*********************************************************************************************************
*/

void  App_TaskStatHook (void)
{
}

/*
*********************************************************************************************************
*                                        TASK SWITCH HOOK (APPLICATION)
*
* Description : This function is called when a task switch is performed.  This allows you to perform other
*               operations during a context switch.
*
* Argument(s) : none.
*
* Note(s)     : (1) Interrupts are disabled during this call.
*
*               (2) It is assumed that the global pointer 'OSTCBHighRdy' points to the TCB of the task that
*                   will be 'switched in' (i.e. the highest priority task) and, 'OSTCBCur' points to the
*                  task being switched out (i.e. the preempted task).
*********************************************************************************************************
*/

#if OS_TASK_SW_HOOK_EN > 0
void  App_TaskSwHook (void)
{

}
#endif

/*
*********************************************************************************************************
*                                     OS_TCBInit() HOOK (APPLICATION)
*
* Description : This function is called by OSTCBInitHook(), which is called by OS_TCBInit() after setting
*               up most of the TCB.
*
* Argument(s) : ptcb    is a pointer to the TCB of the task being created.
*
* Note(s)     : (1) Interrupts may or may not be ENABLED during this call.
*********************************************************************************************************
*/

#if OS_VERSION >= 204
void  App_TCBInitHook (OS_TCB *ptcb)
{
    (void)ptcb;
}
#endif

/*
*********************************************************************************************************
*                                        TICK HOOK (APPLICATION)
*
* Description : This function is called every tick.
*
* Argument(s) : none.
*
* Note(s)     : (1) Interrupts may or may not be ENABLED during this call.
*********************************************************************************************************
*/

#if OS_TIME_TICK_HOOK_EN > 0
void  App_TimeTickHook (void)
{

}
#endif
#endif
