#ifndef IMAGEPLUGIN_H
#define IMAGEPLUGIN_H


/*
author: bin.zhang@autonavi.com
date:

revision: 
	2012.8.20  bin.zhang
	1.增加 MARKER_ID类型,GpsMarker_t结构增加id成员
	2. 增加 CallBack_DelMarker 回调通知函数

*/
//#include "imageplugin_global.h"

typedef int Boolean;

typedef const char* IMAGE_ID;

typedef unsigned int MARKER_ID;

#define True 1
#define False 0 


//描述一个地理坐标点
struct GeoPoint_t{
	double x;
	double y;
};

//描述一个地理矩形
struct GeoRect_t{
	float x;
	float y;
	float width;
	float height;
};

//描述一个gps轨迹点信息
struct GpsPoint_t {
	GeoPoint_t	gpt;
	unsigned int 		timetick; //Unix timestamp 1970 ~ 秒为单位
	float 		speed;  //速度 也许并不能获取
	float 		angle;  //角度 也许并不能获取
	void *		delta;  //用户层私有数据作为上下文传递	(Fileoffset Gps时间对应影像文件偏移量)
};

//表述一个gps轨迹标记点
struct GpsMarker_t{
	GeoPoint_t	gpt;
	int 		timetick;
	int 		type;	//标记类型
	void* 		delta; 
	MARKER_ID			id;		// 2012.8.17 added by scott
};

//描述gps轨迹线段
struct GpsLine_t{
	GpsPoint_t first;
	GpsPoint_t second;
};

//描述gps轨迹
struct GpsPath_t{
	IMAGE_ID	id;			//影像轨迹编号(uniqued)
	GpsPoint_t	* points;	
	unsigned int pointsize;	
	GpsLine_t*	lines;		//轨迹线段集合
	unsigned int	linesize; 	//lines的数量
	GpsMarker_t* markers;		//标记点集合
	unsigned int 	markersize;	//标记点数量
};

struct PluginContext_t;
//!*= 在服务器端的影像轨迹被连续点存储，返回到地图时经过稀释处理，为了便于点选路段，故path由若干line集合而成

//函数: void (*)(IMAGE_ID* ids, size_t size)
//功能: 清除图上影像轨迹, 
//参数:  IF ids == NULL,清除图上所有影像轨迹
//返回: 
typedef void ( *CallBack_ClearImagePath)(PluginContext_t* ctx, IMAGE_ID* ids, size_t size);

//函数: void (*)(GpsPoint_t gpt)
//功能: 影像控制端在回放视频时，计算出当前车辆轨迹点，发送到地图要求作业软件显示当前作业车辆的位置信息
//参数: 
//返回: 
typedef void ( *CallBack_ShowSymbol)(PluginContext_t* ctx, GpsPoint_t gpt);


//函数: void (*)(IMAGE_ID id)
//功能: 影像控制端选择影像记录，通知作业软件在图上高亮选择影像轨迹
//参数: 
//返回: 
typedef void ( *CallBack_ImagePathSelected)(PluginContext_t* ctx, IMAGE_ID id);

//函数: void (*)(GpsPath_t  path)
//功能: 影像控制端刷选出轨迹之后，发送到作业地图上显示
//参数: path – 影像轨迹，由若干line组成，这些line已经被预先处理，便于实现时间跳跃
//返回: 
typedef void  ( *CallBack_ImagePathShow)(PluginContext_t* ctx,  GpsPath_t  path);


//函数: void (*)( IMAGE_ID id,	GpsMarker_t* markers,size_t size)
//功能: 作业时在gps轨迹上打上标记，地图上显示标记即可
//参数: 
//返回: 
typedef void  ( *CallBack_AddMarkers)(PluginContext_t* ctx,  IMAGE_ID id,GpsMarker_t* markers,size_t size);

//函数: void (*)( IMAGE_ID id,	int markerid)
//功能: 发送请求作业软件删除出轨迹上的marker   2012.8.17
//参数: 
//返回: 
typedef void  ( *CallBack_DelMarker)(PluginContext_t* ctx,  IMAGE_ID id,MARKER_ID markerid);

//////////////////////////////////////////////////////////////////////////


//函数: GeoSightChanged
//功能: 作业软件改变视野区域后，需通知影像控制端，以便进行对当前视野区域的影像轨迹检索
//参数: rect - 待查询的地理视界，默认为当前地图视界
//返回: 
typedef void ( * GeoSightChanged_t) (PluginContext_t* ctx,GeoRect_t  rect);


//函数: ImagePathClicked
//功能: 地图上选择影像轨迹之后通知影像控制端进行影像回放,影像将直接跳跃到指定的时间点回放
//参数: id – 轨迹的编号; timetick – 点击轨迹上最接近的gps时间( unix  timestamp 1970~)
//返回: 
typedef void ( *ImagePathClicked_t) (PluginContext_t* ctx, IMAGE_ID  id, unsigned int timetick);


struct CallBackFuns_t{
	CallBack_ClearImagePath	 	ClearImagePath;
	CallBack_ShowSymbol			ShowSymbol;
	CallBack_ImagePathSelected	ImagePathSelected;
	CallBack_ImagePathShow		ImagePathShow;
	CallBack_AddMarkers			AddMarkers;
	CallBack_DelMarker			DelMarker;
	void (*log)(const char* logmsg,int err); //日志输出
};

struct CallFuns_t{
	GeoSightChanged_t GeoSightChanged;
	ImagePathClicked_t	ImagePathClicked;
};


//插件库上下文
struct PluginContext_t{
	char* host;					//影像服务主机 localhost (default)
	unsigned short port;		//影像服务端口 12016
	CallBackFuns_t	callbacks;	//客户初始回调函数接口集
	CallFuns_t		calls;		//库初始
	void * user;
	void * delta;
};


#define IMAGEPLUG_API  extern "C"  __declspec(dllexport)

//extern "C"{

	//函数: init_plugin
	//功能: 初始化插件库
	//参数: 
	//返回: 
IMAGEPLUG_API	Boolean  init_plugin(PluginContext_t* ctx);

	//函数: deinit_plugin
	//功能: 清除
	//参数: 
	//返回: 
IMAGEPLUG_API	void 	 deinit_plugin(PluginContext_t* ctx);

	

//}


#endif // IMAGEPLUGIN_H
