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

//!*= �ڷ������˵�Ӱ��켣��������洢�����ص���ͼʱ����ϡ�ʹ���Ϊ�˱��ڵ�ѡ·�Σ���path������line���϶���

//����: void (*)(IMAGE_ID* ids, size_t size)
//����: ���ͼ��Ӱ��켣
//����: 
//����:
void ClearImagePath(PluginContext_t*,IMAGE_ID* ids, size_t size){
	printf("ClearImagePath..\n");
	for(size_t n=0;n<size;n++){
		printf("id:%s\n",ids[n]);
	}
}

//����: void (*)(GpsPoint_t gpt)
//����: Ӱ����ƶ��ڻط���Ƶʱ���������ǰ�����켣�㣬���͵���ͼҪ����ҵ�����ʾ��ǰ��ҵ������λ����Ϣ
//����: 
//����: 
void ShowSymbol(PluginContext_t*,GpsPoint_t gpt){
	printf("ShowSymbol..\n");
	
	printf("GpsPoint:{lon:%f,lat:%f,tick:%d,speed:%f,angle:%f}\n",gpt.gpt.x,gpt.gpt.y,gpt.timetick,gpt.speed,gpt.angle);

}


//����: void (*)(IMAGE_ID id)
//����: Ӱ����ƶ�ѡ��Ӱ���¼��֪ͨ��ҵ�����ͼ�ϸ���ѡ��Ӱ��켣
//����: 
//����: 
void ImagePathSelected(PluginContext_t*,IMAGE_ID id){
	printf("ImagePathSelected..\n");
	printf("id:%s\n",id);

}

//����: void (*)(GpsPath_t  path)
//����: Ӱ����ƶ�ˢѡ���켣֮�󣬷��͵���ҵ��ͼ����ʾ
//����: path �C Ӱ��켣��������line��ɣ���Щline�Ѿ���Ԥ�ȴ�������ʵ��ʱ����Ծ
//����: 
void  ImagePathShow(PluginContext_t*, GpsPath_t  path){
	printf("ImagePathShow..\n");
	printf("id:%s,lines:%d,markers:%d\n,gps points:%d\n",path.id,path.linesize,path.markersize,path.pointsize);
}


//����: void (*)( IMAGE_ID id,	GpsMarker_t* markers,size_t size)
//����: ��ҵʱ��gps�켣�ϴ��ϱ�ǣ���ͼ����ʾ��Ǽ���
//����: 
//����: 
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

