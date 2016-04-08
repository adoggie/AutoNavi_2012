#ifndef IMAGEPLUGIN_H
#define IMAGEPLUGIN_H


/*
author: bin.zhang@autonavi.com
date:

revision: 
	2012.8.20  bin.zhang
	1.���� MARKER_ID����,GpsMarker_t�ṹ����id��Ա
	2. ���� CallBack_DelMarker �ص�֪ͨ����

*/
//#include "imageplugin_global.h"

typedef int Boolean;

typedef const char* IMAGE_ID;

typedef unsigned int MARKER_ID;

#define True 1
#define False 0 


//����һ�����������
struct GeoPoint_t{
	double x;
	double y;
};

//����һ���������
struct GeoRect_t{
	float x;
	float y;
	float width;
	float height;
};

//����һ��gps�켣����Ϣ
struct GpsPoint_t {
	GeoPoint_t	gpt;
	unsigned int 		timetick; //Unix timestamp 1970 ~ ��Ϊ��λ
	float 		speed;  //�ٶ� Ҳ�����ܻ�ȡ
	float 		angle;  //�Ƕ� Ҳ�����ܻ�ȡ
	void *		delta;  //�û���˽��������Ϊ�����Ĵ���	(Fileoffset Gpsʱ���ӦӰ���ļ�ƫ����)
};

//����һ��gps�켣��ǵ�
struct GpsMarker_t{
	GeoPoint_t	gpt;
	int 		timetick;
	int 		type;	//�������
	void* 		delta; 
	MARKER_ID			id;		// 2012.8.17 added by scott
};

//����gps�켣�߶�
struct GpsLine_t{
	GpsPoint_t first;
	GpsPoint_t second;
};

//����gps�켣
struct GpsPath_t{
	IMAGE_ID	id;			//Ӱ��켣���(uniqued)
	GpsPoint_t	* points;	
	unsigned int pointsize;	
	GpsLine_t*	lines;		//�켣�߶μ���
	unsigned int	linesize; 	//lines������
	GpsMarker_t* markers;		//��ǵ㼯��
	unsigned int 	markersize;	//��ǵ�����
};

struct PluginContext_t;
//!*= �ڷ������˵�Ӱ��켣��������洢�����ص���ͼʱ����ϡ�ʹ���Ϊ�˱��ڵ�ѡ·�Σ���path������line���϶���

//����: void (*)(IMAGE_ID* ids, size_t size)
//����: ���ͼ��Ӱ��켣, 
//����:  IF ids == NULL,���ͼ������Ӱ��켣
//����: 
typedef void ( *CallBack_ClearImagePath)(PluginContext_t* ctx, IMAGE_ID* ids, size_t size);

//����: void (*)(GpsPoint_t gpt)
//����: Ӱ����ƶ��ڻط���Ƶʱ���������ǰ�����켣�㣬���͵���ͼҪ����ҵ�����ʾ��ǰ��ҵ������λ����Ϣ
//����: 
//����: 
typedef void ( *CallBack_ShowSymbol)(PluginContext_t* ctx, GpsPoint_t gpt);


//����: void (*)(IMAGE_ID id)
//����: Ӱ����ƶ�ѡ��Ӱ���¼��֪ͨ��ҵ�����ͼ�ϸ���ѡ��Ӱ��켣
//����: 
//����: 
typedef void ( *CallBack_ImagePathSelected)(PluginContext_t* ctx, IMAGE_ID id);

//����: void (*)(GpsPath_t  path)
//����: Ӱ����ƶ�ˢѡ���켣֮�󣬷��͵���ҵ��ͼ����ʾ
//����: path �C Ӱ��켣��������line��ɣ���Щline�Ѿ���Ԥ�ȴ�������ʵ��ʱ����Ծ
//����: 
typedef void  ( *CallBack_ImagePathShow)(PluginContext_t* ctx,  GpsPath_t  path);


//����: void (*)( IMAGE_ID id,	GpsMarker_t* markers,size_t size)
//����: ��ҵʱ��gps�켣�ϴ��ϱ�ǣ���ͼ����ʾ��Ǽ���
//����: 
//����: 
typedef void  ( *CallBack_AddMarkers)(PluginContext_t* ctx,  IMAGE_ID id,GpsMarker_t* markers,size_t size);

//����: void (*)( IMAGE_ID id,	int markerid)
//����: ����������ҵ���ɾ�����켣�ϵ�marker   2012.8.17
//����: 
//����: 
typedef void  ( *CallBack_DelMarker)(PluginContext_t* ctx,  IMAGE_ID id,MARKER_ID markerid);

//////////////////////////////////////////////////////////////////////////


//����: GeoSightChanged
//����: ��ҵ����ı���Ұ�������֪ͨӰ����ƶˣ��Ա���жԵ�ǰ��Ұ�����Ӱ��켣����
//����: rect - ����ѯ�ĵ����ӽ磬Ĭ��Ϊ��ǰ��ͼ�ӽ�
//����: 
typedef void ( * GeoSightChanged_t) (PluginContext_t* ctx,GeoRect_t  rect);


//����: ImagePathClicked
//����: ��ͼ��ѡ��Ӱ��켣֮��֪ͨӰ����ƶ˽���Ӱ��ط�,Ӱ��ֱ����Ծ��ָ����ʱ���ط�
//����: id �C �켣�ı��; timetick �C ����켣����ӽ���gpsʱ��( unix  timestamp 1970~)
//����: 
typedef void ( *ImagePathClicked_t) (PluginContext_t* ctx, IMAGE_ID  id, unsigned int timetick);


struct CallBackFuns_t{
	CallBack_ClearImagePath	 	ClearImagePath;
	CallBack_ShowSymbol			ShowSymbol;
	CallBack_ImagePathSelected	ImagePathSelected;
	CallBack_ImagePathShow		ImagePathShow;
	CallBack_AddMarkers			AddMarkers;
	CallBack_DelMarker			DelMarker;
	void (*log)(const char* logmsg,int err); //��־���
};

struct CallFuns_t{
	GeoSightChanged_t GeoSightChanged;
	ImagePathClicked_t	ImagePathClicked;
};


//�����������
struct PluginContext_t{
	char* host;					//Ӱ��������� localhost (default)
	unsigned short port;		//Ӱ�����˿� 12016
	CallBackFuns_t	callbacks;	//�ͻ���ʼ�ص������ӿڼ�
	CallFuns_t		calls;		//���ʼ
	void * user;
	void * delta;
};


#define IMAGEPLUG_API  extern "C"  __declspec(dllexport)

//extern "C"{

	//����: init_plugin
	//����: ��ʼ�������
	//����: 
	//����: 
IMAGEPLUG_API	Boolean  init_plugin(PluginContext_t* ctx);

	//����: deinit_plugin
	//����: ���
	//����: 
	//����: 
IMAGEPLUG_API	void 	 deinit_plugin(PluginContext_t* ctx);

	

//}


#endif // IMAGEPLUGIN_H
