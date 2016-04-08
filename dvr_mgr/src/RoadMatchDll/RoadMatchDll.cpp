// RoadMatchDll.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "RoadMatchDll.h"


// This is an example of an exported variable
ROADMATCHDLL_API int nRoadMatchDll=0;

// This is an example of an exported function.
ROADMATCHDLL_API int fnRoadMatchDll(void)
{
	return 42;
}

// This is the constructor of a class that has been exported.
// see RoadMatchDll.h for the class definition
CRoadMatchDll::CRoadMatchDll()
{
	return;
}

#include "../../lib/roadmatch/Api/include/MatchRoadApi.h"
#ifdef _DEBUG
#pragma comment(lib,"../../lib/roadmatch/Api/lib/debug/MatchRoadApi.lib")
#pragma comment(lib,"../../lib/roadmatch/Api/lib/debug/XLong.lib")
#else
#pragma comment(lib,"../../lib/roadmatch/Api/lib/release/MatchRoadApi.lib")
#pragma comment(lib,"../../lib/roadmatch/Api/lib/release/XLong.lib")
#endif

#include <stdio.h>

using namespace  MathchRoadApi;

extern "C" __declspec(dllexport) void __cdecl _gpsfix_begin(CallBack_PointFixed user){
	//printf("_gpsfix_begin() args:%x",user);
	gpsfix_begin(user);
	GpsPoint_t pt;
	pt.lon = 45;
	pt.lat = 10;
	//user(&pt,1);


}

extern "C" __declspec(dllexport) void _gpsfix_end(){
	printf("gpsfix_end\n");
	//gpsfix_end();
}

extern "C" __declspec(dllexport) void _gpsfix_data(GpsPoint_t* pt,size_t ptsize){
	//printf("%f,%f,%d\n",pt->lon,pt->lat,ptsize);
	gpsfix_data(pt,ptsize);
}

extern "C" __declspec(dllexport) void _nodesplit_begin(CallBack_NodeSplitted user){
	nodesplit_begin(user);
}

extern "C" __declspec(dllexport) void _nodesplit_end(){
	nodesplit_end();
}

extern "C" __declspec(dllexport) void _nodesplit_data(GpsPoint_t* pts, size_t size){
	nodesplit_data(pts,size);
}

struct Packet{
	char * name;
	char * data;
	size_t size;
};



extern "C" __declspec(dllexport) int __cdecl test1(int* a){
	return *a * 10;
}

extern "C" __declspec(dllexport) Packet* __cdecl test2(char *pp,size_t ppsize){
	
	char buf[120];
	strncpy(buf,pp,ppsize);
	printf("%s,size:%d\n",buf,ppsize);
	
	Packet * pkt = new Packet();
	pkt->name = "test";
	pkt->size = 1024*100;
	pkt->data = new char[pkt->size];
	memset(pkt->data,'\G',pkt->size);
	return pkt;

}

extern "C" __declspec(dllexport) Packet* __cdecl test3(Packet* pkt){
	delete[] pkt->data;
	delete pkt;
	printf("deleted ok\n");
	return NULL;
}


extern "C" __declspec(dllexport) void  __cdecl test4(){
	printf("test4\n");
}