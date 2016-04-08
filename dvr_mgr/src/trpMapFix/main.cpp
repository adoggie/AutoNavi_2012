
//////////////////////////////////////////////////////////////////////////
/**
Dvr.TrpMapFix @ autonavi.com
-----------------------
1. created scott  2012.3.9   22:00

*/
//////////////////////////////////////////////////////////////////////////
#include "stdafx.h"
#include <QtCore/QCoreApplication>

#include <QFile>
#include <QDir>
#include <QTextStream>
#include <QDateTime>

#include "../../lib/roadmatch/api/include/MatchRoadApi.h"

#ifdef _DEBUG
	#pragma comment(lib,"../../lib/roadmatch/api/lib/debug/MatchRoadApi.lib")
	#pragma comment(lib,"../../lib/roadmatch/api/lib/debug/XLong.lib")
#else
#pragma comment(lib,"../../lib/roadmatch/api/lib/release/MatchRoadApi.lib")
#pragma comment(lib,"../../lib/roadmatch/api/lib/release/XLong.lib")
#endif

using namespace MathchRoadApi;

QFile outputfile;
void cbPointFixed(GpsPoint_t* pts, size_t size)
{
	QFile &file = outputfile;
	if(pts==NULL){
		file.close();		
	}else{
		for(size_t n=0;n<size;n++){
			GpsPoint_t &pt = pts[n];
			QDateTime time;
			time.setTime_t(pt.timetick);
			QString timestr;
			timestr = time.toString("yyyyMMddhhmmss");
			QString line;
			pt.lon*=3600.;
			pt.lat*=3600.;
			line = QString("%1,%2,%3,%4,%5,%6\n").arg(pt.lon,0,'f',6).arg(pt.lat,0,'f',6).arg(timestr).arg(pt.timetick).arg(pt.speed).arg(pt.angle);
			file.write(line.toStdString().c_str());
			file.flush();
		}	
	}
}

//////////////////////////////////////////////////////////////////////////
// Êä³öjson±àÂë
QString GpsPointToStr(GpsPoint_t& pt){
	QString s;
	s = QString("{\"lon\":%1,\"lat\":%2,\"tick\":%3,\"speed\":%4,\"angle\":%5}").arg(pt.lon,0,'f',6).arg(pt.lat,0,'f',6).arg(pt.timetick).arg(pt.speed).arg(pt.angle);
	return s;
}

QString RoadNodeToStr(RoadNode_t& node){
	QString s;
	s = QString("{\"mess\":%1,\"node\":%2}").arg(node.Mesh_id).arg(node.Node_id);
	return s;
}

QString RoadPartToStr(RoadPart_t& part){
	QString s;
	s = QString("{\"firstNode\":%1,\"secondNode\":%2,\"firstPoint\":%3,\"secondPoint\":%4}").arg(RoadNodeToStr(part.first_node)).arg(RoadNodeToStr(part.second_node))
		.arg(GpsPointToStr(part.First_point)).arg(GpsPointToStr(part.Last_point));
	return s;
}


void cbNodeSplitted(RoadPart_t* parts, size_t size){
	QFile &file = outputfile;
	if(!parts){		
		file.close();
		return ;
	}
	//printf("nodesplited..\n");
	for(size_t n=0;n<size;n++){
		RoadPart_t &pt = parts[n];		
		QString line;
		line = RoadPartToStr(pt);
		file.write(line.toStdString().c_str());
		file.write("\n");
		file.flush();			
	}
}



void PointFix(const char* input,const char* output){
	
	{
		bool ret;			
		GpsPoint_t gpt;	
		QByteArray bytes;

		QFile file(input);					
		ret = file.open(QIODevice::ReadOnly);
		if(!ret){
			qFatal("input file open failed!\n");
			return ;
		}
		
		outputfile.setFileName(output);
		ret = outputfile.open(QIODevice::WriteOnly);
		if(!ret){
			qFatal("output file openWrite failed!\n");
			return;
		}

		gpsfix_begin(cbPointFixed);	
		memset(&gpt,0,sizeof gpt);		
		bytes = file.readLine();
		while( bytes.size()){
			QString line = bytes.data();
			QStringList fields = line.split(",");
			if( fields.size()!=6){
				bytes = file.readLine();
				continue;
			}
			float lon = fields[0].toFloat();
			float lat = fields[1].toFloat();
			int timetick = fields[3].toInt();
			float speed = fields[4].toFloat();
			float angle = fields[5].toFloat();
			gpt.lon = lon/3600.;
			gpt.lat = lat/3600.;
			gpt.timetick = timetick;
			gpt.speed = speed;
			gpt.angle = angle;
			gpsfix_data(&gpt,1);			
			bytes = file.readLine();
		}
	}
	gpsfix_end();	
}



void RoadMatch(const char* input,const char* output){
	
	bool ret;			
	GpsPoint_t gpt;	
	QByteArray bytes;

	QFile file(input);					
	ret = file.open(QIODevice::ReadOnly);
	if(!ret){
		qFatal("input file open failed!\n");
		return ;
	}

	outputfile.setFileName(output);
	ret = outputfile.open(QIODevice::WriteOnly);
	if(!ret){
		qFatal("output file openWrite failed!\n");
		return;
	}

	nodesplit_begin(cbNodeSplitted);
	bytes = file.readLine();
	while( bytes.size()){
		QString line = bytes.data();
		QStringList fields = line.split(",");
		if( fields.size()!=6){
			bytes = file.readLine();
			continue;
		}
		float lon = fields[0].toFloat();
		float lat = fields[1].toFloat();
		int timetick = fields[3].toInt();
		float speed = fields[4].toFloat();
		float angle = fields[5].toFloat();
		gpt.lon = lon/3600.;
		gpt.lat = lat/3600.;
		gpt.timetick = timetick;
		gpt.speed = speed;
		gpt.angle = angle;
		//printf("%s\n",GpsPointToStr(gpt).toStdString().c_str());
		nodesplit_data(&gpt,1);			
		bytes = file.readLine();
	}

}




void usage(){
	const char * prompts="usage:\ntrpMapFix.exe [fixpoint|matchroad] input output \n ";
	qDebug(prompts);
}

int main(int argc, char *argv[]){
	if( argc < 4){
		usage();
		return -1;
	}
	QCoreApplication a(argc, argv);	
	const char * cmd;
	cmd = argv[1];
	if( QString(cmd).toLower() == "fixpoint"){
		PointFix(argv[2],argv[3]);
	}else if (QString(cmd).toLower() == "matchroad"){
		RoadMatch(argv[2],argv[3]);
	}else{
		return -1;
	}
	return 0;
}


