// testplugin.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include "../imageplugin/imageplugin.h"
#ifdef _DEBUG
	#pragma comment(lib,"../lib/imageplugind.lib")
#else
	#pragma comment(lib,"../lib/imageplugin.lib")
#endif


PluginContext_t ctx;

//!*= 在服务器端的影像轨迹被连续点存储，返回到地图时经过稀释处理，为了便于点选路段，故path由若干line集合而成

//函数: void (*)(IMAGE_ID* ids, size_t size)
//功能: 清除图上影像轨迹
//参数: 
//返回:
void ClearImagePath(PluginContext_t*,IMAGE_ID* ids, size_t size){
	printf("ClearImagePath..\n");
	for(size_t n=0;n<size;n++){
		printf("id:%s\n",ids[n]);
	}
}

//函数: void (*)(GpsPoint_t gpt)
//功能: 影像控制端在回放视频时，计算出当前车辆轨迹点，发送到地图要求作业软件显示当前作业车辆的位置信息
//参数: 
//返回: 
void ShowSymbol(PluginContext_t*,GpsPoint_t gpt){
	printf("ShowSymbol..\n");
	
	printf("GpsPoint:{lon:%f,lat:%f,tick:%d,speed:%f,angle:%f}\n",gpt.gpt.x,gpt.gpt.y,gpt.timetick,gpt.speed,gpt.angle);

}


//函数: void (*)(IMAGE_ID id)
//功能: 影像控制端选择影像记录，通知作业软件在图上高亮选择影像轨迹
//参数: 
//返回: 
void ImagePathSelected(PluginContext_t*,IMAGE_ID id){
	printf("ImagePathSelected..\n");
	printf("id:%s\n",id);

}

//函数: void (*)(GpsPath_t  path)
//功能: 影像控制端刷选出轨迹之后，发送到作业地图上显示
//参数: path – 影像轨迹，由若干line组成，这些line已经被预先处理，便于实现时间跳跃
//返回: 
void  ImagePathShow(PluginContext_t*, GpsPath_t  path){
	printf("ImagePathShow..\n");
	printf("id:%s,lines:%d,markers:%d\n,gps points:%d\n",path.id,path.linesize,path.markersize,path.pointsize);
}


//函数: void (*)( IMAGE_ID id,	GpsMarker_t* markers,size_t size)
//功能: 作业时在gps轨迹上打上标记，地图上显示标记即可
//参数: 
//返回: 
void  AddMarkers(PluginContext_t*, IMAGE_ID id,GpsMarker_t* markers,size_t size){
	printf("AddMarkers..\n");
	printf("id:%s\n",id);
	for(size_t n=0;n<size;n++){
		printf("Markers:{lon:%f,lat:%f,tick:%d,type:%d}\n",markers[n].gpt.x,markers[n].gpt.y,
			markers[n].timetick,markers[n].type);

	}
}


void  DelMarker(PluginContext_t* ctx,  IMAGE_ID id,MARKER_ID markerid){
	printf("DelMarker image id:%s,marker id:%d \n",id,markerid);

}


void log(const char* msg,int err){
	printf("%s\n",msg);
}

#include <windows.h>
#include <stdlib.h>
#include <conio.h>
#include <stdio.h>
#include <iostream>

void cmdlist(){
	printf("howto:\n1  ->GeoSightChanged()\n2 ->ImagePathClicked()\n");
}


int _tmain(int argc, _TCHAR* argv[]){
	Boolean r ;
	PluginContext_t ctx;
	ctx.callbacks.AddMarkers = AddMarkers;
	ctx.callbacks.ClearImagePath = ClearImagePath;
	ctx.callbacks.ImagePathSelected = ImagePathSelected;
	ctx.callbacks.ImagePathShow = ImagePathShow;
	ctx.callbacks.log = log;
	ctx.callbacks.ShowSymbol = ShowSymbol;
	ctx.callbacks.DelMarker = DelMarker;

	ctx.host="127.0.0.1";
	ctx.port=12016;

// 	ctx.host="baidu.com";
// 	ctx.port=80;

	r = init_plugin(&ctx);
	char cmd[20];
	while(1){
		std::cin>>cmd;
		if(!strcmp(cmd,"exit")){
			printf("exit...\n");
			break;
		}else if(!strcmp(cmd,"1")){
			printf("GeoSightChanged() >>\n");
			GeoRect_t rc;
			rc.x = 121.12;rc.y = 31.21;
			rc.width = 0.5; rc.height= 0.5;
			ctx.calls.GeoSightChanged(&ctx,rc);

		}else if(!strcmp(cmd,"2")){
			printf("ImagePathClicked() >>\n");
			ctx.calls.ImagePathClicked(&ctx,"dsaf",132000000);
		}
		else{
			cmdlist();
		}
	}

	//Sleep(1000*1000);
	deinit_plugin(&ctx);
	return 0;
}

