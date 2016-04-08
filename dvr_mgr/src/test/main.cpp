
#include <QtCore/QCoreApplication>

#include "../../libs/roadmatch/Api/include/MatchRoadApi.h"
#ifdef _DEBUG
//#pragma comment(lib,"../../libs/roadmatch/Api/lib/debug/MatchRoadApi.lib")
//#pragma comment(lib,"../../libs/roadmatch/Api/lib/debug/XLong.lib")
#else
#pragma comment(lib,"../../libs/roadmatch/Api/lib/release/MatchRoadApi.lib")
#pragma comment(lib,"../../libs/roadmatch/Api/lib/release/XLong.lib")
#endif

#include <stdio.h>

using namespace  MathchRoadApi;

void cbPointFixed(GpsPoint_t* pts, size_t size){
	if(pts){
		printf("%f,%f\n",pts->lon,pts->lat);
	}
}
extern "C" void _gpsfix_begin(CallBack_PointFixed user);
extern "C" void _gpsfix_end();
extern "C" void _gpsfix_data(GpsPoint_t* pt,size_t ptsize);

int main(int argc, char *argv[])
{
	QCoreApplication a(argc, argv);

	_gpsfix_begin(cbPointFixed);
	GpsPoint_t pt;
	memset(&pt,0,sizeof pt);
	pt.lon = 121.30234;
	pt.lat = 31.12345;
	_gpsfix_data(&pt,1);
	_gpsfix_end();
	//return a.exec();
	return 0;
}
