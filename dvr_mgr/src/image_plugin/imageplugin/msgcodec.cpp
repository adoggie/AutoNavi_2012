#include <windows.h>

// #include "../../../lib/qjson-0.7.1/qjson/src/parser.h"
// #include "../../../lib/qjson-0.7.1/qjson/src/serializer.h"

#include "msgcodec.h"
#include <QThread>
#include <QDataStream>
#include <vector>
#include <list>
#include <map>
#include "cJSON.h"

#pragma comment(lib,"ws2_32.lib")

// #ifdef _DEBUG
// #pragma comment(lib,"../lib/qjsond.lib")
// #else
// #pragma comment(lib,"../lib/qjson.lib")
// 
// #endif


void log(PluginContext_t* ctx,const char * msg,int err=0){
	if(ctx->callbacks.log)
		ctx->callbacks.log(msg,err);
}

MessageCodec::MessageCodec(PluginContext_t* ctx){
	_ctx = ctx;
	_status = 0; 
// 	connect(&_sock,SIGNAL(connected()),this,SLOT(connected()) );
// 	connect(&_sock,SIGNAL(disconnected()),this,SLOT(disconnected()) );
// 	connect(&_sock,SIGNAL(error(QAbstractSocket::SocketError )),this,SLOT(error ( QAbstractSocket::SocketError )) );
// 	connect(&_sock,SIGNAL(readyRead()),this,SLOT(readyRead()) );
	//_fd = socket(AF_INET,SOCK_STREAM,0);
	//connect(&_thread,SIGNAL(started()),this,SLOT(thread_recv()));
	_threadstatus = 0;

	static int initflag=0;
	if(!initflag){
		WSADATA wsaData; 
		WSAStartup(MAKEWORD(2,2),&wsaData);
		initflag = 1;
	}
	_fd =-1;
}

void MessageCodec::do_recv(){
	int len;
	char buff[1024*200];

	while(true){
		int r;
		r = ::recv(_fd,buff,sizeof(buff),0);
		if(r<=0){
			closesocket(_fd);
			_fd = NULL;
			disconnected();
			break;			
		}

		_decbytes.append(buff,r);
		while(true){
			uint size;
			if( _decbytes.size()<4){
				break;
			}
			QByteArray h = _decbytes.left(4);
			QDataStream ds(h); ds.setByteOrder(QDataStream::BigEndian);
			ds>>size;
			if(_decbytes.size() < size + 4){
				break;  // too small
			}
			QByteArray data( _decbytes.constData()+4,size);
			_decbytes = _decbytes.right( _decbytes.size() - size - 4);
			QByteArray rr;
			//rr = qUncompress(data) ;//  zlib uncompress
			parseMessage(data);
		}// end while
	}	
}

void MessageCodec::thread_recv(void * p){
	MessageCodec* owner = (MessageCodec*)p;
	owner->_threadstatus = 1;
	owner->do_recv();
	owner->_threadstatus = 0;
	owner->_fd = -1;
}

void	MessageCodec::thread_keepalive (void* p ){
	MessageCodec* owner = (MessageCodec*)p;
	while(owner->_status){
		if(owner->_fd == -1){
			owner->connect_imagesvc();
		}
		::Sleep(1000*2);
	}
}

void	MessageCodec::connected (){
	_leftbytes = 0;
	_decbytes.clear();

	log(_ctx,"connected to imagectrl",0);
}

void	MessageCodec::disconnected (){
	log(_ctx,"lost connection with imagectrl",0);
	_decbytes.clear();
}

void	MessageCodec::error ( QAbstractSocket::SocketError socketError ){
	if(_status == 0){
		return;
	}
	::Sleep(2*1000);
	if(_status == 0){
		return;
	}
	log(_ctx,"socket on error ,reconect imagectrl!",0);
	_sock.connectToHost(_svcaddr.first,_svcaddr.second);
}


bool MessageCodec::connect_imagesvc(){
//_sock = QTcpSocket();
// 	_sock.connectToHost(_svcaddr.first,_svcaddr.second);
//  	if( !_sock.waitForConnected(5*1000)){
//  		log(_ctx,"connect to server error!",0);
//  		return false;
//  	}
	log(_ctx,"ready to connect server..");
	while(_threadstatus){
		Sleep(1000);
	}
	_fd = socket(AF_INET,SOCK_STREAM,0);
	sockaddr_in addr;
	addr.sin_addr.s_addr = inet_addr(_svcaddr.first.toStdString().c_str());
	addr.sin_family = AF_INET;
	addr.sin_port = htons(_svcaddr.second);
	int r=::connect(_fd,(sockaddr*)&addr,sizeof(addr));
	if(r){
		closesocket(_fd);
		_fd  =-1;
		log(_ctx,"connect to server error!",0);
		return false;
	}
	connected();

	DWORD tid;
	CreateThread(NULL,NULL,(LPTHREAD_START_ROUTINE)MessageCodec::thread_recv,(void*)this,NULL,&tid);
	return true;
}

bool MessageCodec::open(const QString& host ,const short port){
	_status = 1;
	_svcaddr.first = host;
	_svcaddr.second = port;
	//connect_imagesvc();
	DWORD tid;
	CreateThread(NULL,NULL,(LPTHREAD_START_ROUTINE)MessageCodec::thread_keepalive,(void*)this,NULL,&tid);
	return true;
}

void MessageCodec::close(){
	closesocket(_fd);
	_status = 0;
}

void MessageCodec::parseMessage(QByteArray & bytes){
	//QJson::Parser parser;
	bool ok; 
	int i;
	cJSON * root,*n1,*n2;
	bytes+='\0';

	root = cJSON_Parse(bytes.constData());
	if(!root){
		log(_ctx,"parse json error!",0);
		return;
	}
 
	
	n1 = cJSON_GetObjectItem(root,"msg");
	//////////////////////////////////////////////////////////////////////////
	// first message..
	//////////////////////////////////////////////////////////////////////////
	// 清除地图上路段影像轨迹
	if( !strcmp(n1->valuestring,"plugin_clearimagepath_2") ){
		std::vector<IMAGE_ID> result;
		n1 = cJSON_GetObjectItem(root,"ids");
		
		for(i=0;i<cJSON_GetArraySize(n1);i++){
			cJSON *subitem = cJSON_GetArrayItem(n1,i);
			result.push_back(subitem->valuestring);
		}

		if(_ctx->callbacks.ClearImagePath){
			if( result.size() == 0){
				_ctx->callbacks.ClearImagePath(_ctx,NULL,NULL);
			}else{
				_ctx->callbacks.ClearImagePath(_ctx,&result[0],result.size());
			}
		}
		
	}else if( !strcmp( n1->valuestring, "plugin_showsymbol_2") ){
		GpsPoint_t gpt;
		n1 = cJSON_GetObjectItem(root,"pos");		
		gpt.gpt.x = (float)cJSON_GetObjectItem(n1,"lon")->valuedouble;
		gpt.gpt.y = (float)cJSON_GetObjectItem(n1,"lat")->valuedouble;
		gpt.angle = (float)cJSON_GetObjectItem(n1,"angle")->valuedouble;
		gpt.speed = (float)cJSON_GetObjectItem(n1,"speed")->valuedouble;
		gpt.timetick = (int)cJSON_GetObjectItem(n1,"time")->valueint;
		if(_ctx->callbacks.ShowSymbol){
			_ctx->callbacks.ShowSymbol(_ctx,gpt);
		}
		
	}else if( !strcmp( n1->valuestring,"plugin_imagepathselected_2") ){
		IMAGE_ID id;
		id = cJSON_GetObjectItem(root,"id")->valuestring;
		if(_ctx->callbacks.ImagePathSelected){
			_ctx->callbacks.ImagePathSelected(_ctx,id);
		}
		
	}else if( !strcmp( n1->valuestring,"plugin_showimagepathonmap_2") ){
		QList<QVariant> items ;
		std::vector<GpsLine_t> lines;
		std::vector<GpsMarker_t> markers;
		std::vector<GpsPoint_t> points;

		GpsPath_t path;
		memset(&path,0,sizeof(path));


		//std::string id = r["id"].toString().toStdString();
		path.id =  cJSON_GetObjectItem(root,"id")->valuestring;
		
		n1 = cJSON_GetObjectItem(root,"lines");
		lines.resize(cJSON_GetArraySize(n1));
		for(i=0;i<cJSON_GetArraySize(n1);i++ ){
			cJSON *item=cJSON_GetArrayItem(n1,i);
			n2 = cJSON_GetObjectItem(item,"first");
			lines[i].first.gpt.x =(float)cJSON_GetObjectItem(n2,"lon")->valuedouble;
			lines[i].first.gpt.x = (float)cJSON_GetObjectItem(n2,"lat")->valuedouble; 
			lines[i].first.speed =(float)cJSON_GetObjectItem(n2,"speed")->valuedouble; 
			lines[i].first.angle =(float)cJSON_GetObjectItem(n2,"angle")->valuedouble;
			lines[i].first.timetick =cJSON_GetObjectItem(n2,"time")->valueint;
			n2 = cJSON_GetObjectItem(item,"second");
			lines[i].second.gpt.x =(float)cJSON_GetObjectItem(n2,"lon")->valuedouble;
			lines[i].second.gpt.x = (float)cJSON_GetObjectItem(n2,"lat")->valuedouble; 
			lines[i].second.speed =(float)cJSON_GetObjectItem(n2,"speed")->valuedouble; 
			lines[i].second.angle =(float)cJSON_GetObjectItem(n2,"angle")->valuedouble;
			lines[i].second.timetick =cJSON_GetObjectItem(n2,"time")->valueint;
		}

		n1 = cJSON_GetObjectItem(root,"markers");
		markers.resize(cJSON_GetArraySize(n1));

		for(i=0;i<cJSON_GetArraySize(n1);i++ ){
			cJSON *n2=cJSON_GetArrayItem(n1,i);
			markers[i].gpt.x = (float)cJSON_GetObjectItem(n2,"lon")->valuedouble;
			markers[i].gpt.y = (float)cJSON_GetObjectItem(n2,"lat")->valuedouble; 
			markers[i].timetick = cJSON_GetObjectItem(n2,"time")->valueint;
			markers[i].type = cJSON_GetObjectItem(n2,"type")->valueint;

		}
		///////////////////////////////////////////////
		// points
		n1 = cJSON_GetObjectItem(root,"points");
		points.resize(cJSON_GetArraySize(n1));
		
		for(i=0;i<cJSON_GetArraySize(n1);i++ ){
			cJSON *n2=cJSON_GetArrayItem(n1,i);
			points[i].gpt.x = (float)cJSON_GetObjectItem(n2,"lon")->valuedouble;
			points[i].gpt.y = (float)cJSON_GetObjectItem(n2,"lat")->valuedouble;
			points[i].timetick = cJSON_GetObjectItem(n2,"time")->valueint;
			points[i].speed = (float)cJSON_GetObjectItem(n2,"speed")->valuedouble;
			points[i].angle = (float)cJSON_GetObjectItem(n2,"angle")->valuedouble;
		}

		if(points.size()){
			path.points = &points[0];
			path.pointsize = points.size();
		}
		if(lines.size()){
			path.lines= &lines[0];
			path.linesize = lines.size();
		}
		if(markers.size()){
			path.markers = &markers[0];
			path.markersize = markers.size();
		}
		if(_ctx->callbacks.ImagePathShow){
			_ctx->callbacks.ImagePathShow(_ctx,path);
		}
		
	}else if( !strcmp( n1->valuestring,"plugin_addmarker_2") ){
		IMAGE_ID id;
		MARKER_ID mid;

		std::vector<GpsMarker_t> markers;

		
		id =  cJSON_GetObjectItem(root,"id")->valuestring;
		n1 = cJSON_GetObjectItem(root,"markers");
		markers.resize(cJSON_GetArraySize(n1));
		
		for(i=0;i<cJSON_GetArraySize(n1);i++ ){
			n2=cJSON_GetArrayItem(n1,i);
			markers[i].gpt.x = (float)cJSON_GetObjectItem(n2,"lon")->valuedouble;
			markers[i].gpt.y = (float)cJSON_GetObjectItem(n2,"lat")->valuedouble;
			markers[i].timetick = cJSON_GetObjectItem(n2,"time")->valueint;
			markers[i].type = cJSON_GetObjectItem(n2,"type")->valueint;
			markers[i].id = (MARKER_ID)cJSON_GetObjectItem(n2,"id")->valueint; 
		}

		if(_ctx->callbacks.AddMarkers){
			if( !markers.size()){
				_ctx->callbacks.AddMarkers(_ctx,id,NULL,NULL);
			}else{
				_ctx->callbacks.AddMarkers(_ctx,id,&markers[0],markers.size());
			}
		}
		
	}else if( !strcmp( n1->valuestring,"plugin_delmarker_2") ){ // 2012.8.17
			IMAGE_ID id;
			MARKER_ID mid;

			id =  cJSON_GetObjectItem(root,"id")->valuestring;						
			mid = (MARKER_ID)cJSON_GetObjectItem(root,"markerid")->valueint;
			if(_ctx->callbacks.DelMarker){
				_ctx->callbacks.DelMarker(_ctx,id,mid);
			}
	}
	cJSON_Delete(root);
}

/*
void MessageCodec::parseMessage_qjson(QByteArray & bytes){
	QJson::Parser parser;
	bool ok; 
	QVariantMap r = parser.parse (bytes, &ok).toMap();
	if(!ok){
		log(_ctx,"parse json error!",0);
		return;
	}

	//////////////////////////////////////////////////////////////////////////
	// first message..
	//////////////////////////////////////////////////////////////////////////
	// 清除地图上路段影像轨迹
	if(r["msg"] == "plugin_clearimagepath_2"){
		std::vector<IMAGE_ID> result;
		std::vector<std::string> set;

		QList<QVariant> ids = r["ids"].toList();
		foreach(QVariant e,ids){
			std::string id = e.toString().toStdString();			
			set.push_back(id);
			result.push_back( set[set.size()-1].c_str());
		}
		if(_ctx->callbacks.ClearImagePath){
			if( result.size() == 0){
				_ctx->callbacks.ClearImagePath(NULL,NULL);
			}else{
				_ctx->callbacks.ClearImagePath(&result[0],result.size());
			}
		}
	}
	//////////////////////////////////////////////////////////////////////////
	// 图上显示车辆图标
	if( r["msg"] == "plugin_showsymbol_2"){
		QVariantMap g = r["pos"].toMap();
		GpsPoint_t gpt;
		gpt.gpt.x = g["lon"].toFloat();
		gpt.gpt.y = g["lat"].toFloat();
		gpt.angle = g["angle"].toFloat();
		gpt.speed = g["speed"].toFloat();
		gpt.timetick = g["time"].toUInt();
		if(_ctx->callbacks.ShowSymbol){
			_ctx->callbacks.ShowSymbol(gpt);
		}
	}
	//图上显示高亮轨迹
	if( r["msg"] =="plugin_imagepathselected_2"){
		std::string  sid = r["id"].toString().toStdString();
		IMAGE_ID id = sid.c_str();
		if(_ctx->callbacks.ImagePathSelected){
			_ctx->callbacks.ImagePathSelected(id);
		}
	}
	//# 选择影像记录在图上显示出影像的轨迹
	if( r["msg"] == "plugin_showimagepathonmap_2"){
		QList<QVariant> items ;
		std::vector<GpsLine_t> lines;
		std::vector<GpsMarker_t> markers;
		std::vector<GpsPoint_t> points;

		GpsPath_t path;
		memset(&path,0,sizeof(path));
		std::string id = r["id"].toString().toStdString();
		path.id =  id.c_str();

		items = r["lines"].toList();
		lines.resize(items.size());

		int c=0;
		foreach(QVariant v,items){
			QVariantMap f,s;
			QVariantMap attrs = v.toMap();
			f = attrs["first"].toMap();
			s = attrs["second"].toMap();
			lines[c].first.gpt.x = f["lon"].toFloat();
			lines[c].first.gpt.x = f["lat"].toFloat();
			lines[c].first.speed = f["speed"].toFloat();
			lines[c].first.angle = f["angle"].toFloat();
			lines[c].first.timetick = f["time"].toUInt();
			c++;
		}

		items = r["markers"].toList();
		markers.resize(items.size());
		c=0;
		foreach(QVariant v,items){
			QVariantMap attrs = v.toMap();
			markers[c].gpt.x = attrs["lon"].toFloat();
			markers[c].gpt.y = attrs["lat"].toFloat();
			markers[c].timetick = attrs["time"].toUInt();
			markers[c].type = attrs["type"].toInt();

			c++;
		}

		//////////////////////////////////////////////////////////////////////////
		// points
		items = r["points"].toList();
		points.resize(items.size());
		c=0;
		foreach(QVariant v,items){
			QVariantMap attrs = v.toMap();
			points[c].gpt.x = attrs["lon"].toFloat();
			points[c].gpt.y = attrs["lat"].toFloat();
			points[c].timetick = attrs["time"].toUInt();
			points[c].speed = attrs["speed"].toFloat();
			points[c].angle = attrs["angle"].toFloat();
			c++;
		}

		if(points.size()){
			path.points = &points[0];
			path.pointsize = points.size();
		}
		if(lines.size()){
			path.lines= &lines[0];
			path.linesize = lines.size();
		}
		if(markers.size()){
			path.markers = &markers[0];
			path.markersize = markers.size();
		}
		if(_ctx->callbacks.ImagePathShow){
			_ctx->callbacks.ImagePathShow(path);
		}
	}
	//////////////////////////////////////////////////////////////////////////
	//
	if( r["msg"]=="plugin_addmarker_2"){
		IMAGE_ID id;

		std::vector<GpsMarker_t> markers;
		std::string sid = r["id"].toString().toStdString();
		id = sid.c_str();
		QList<QVariant> items = r["markers"].toList();
		markers.resize(items.size());
		int c=0;
		foreach(QVariant v,items){
			QVariantMap attrs = v.toMap();
			markers[c].gpt.x = attrs["lon"].toFloat();
			markers[c].gpt.y = attrs["lat"].toFloat();
			markers[c].timetick = attrs["time"].toUInt();
			markers[c].type = attrs["type"].toInt();
			c++;
		}
		if(_ctx->callbacks.AddMarkers){
			if( !markers.size()){
				_ctx->callbacks.AddMarkers(id,NULL,NULL);
			}else{
				_ctx->callbacks.AddMarkers(id,&markers[0],markers.size());
			}
		}
	}

}
*/

/*
数据消息定义: 
[size(4),contents(json)(zlib)]
*/
void  MessageCodec::readyRead(){
	_decbytes+= _sock.readAll();
	while(true){
		uint size;
		if( _decbytes.size()<4){
			break;
		}
		QByteArray h = _decbytes.left(4);
		QDataStream ds(h); ds.setByteOrder(QDataStream::BigEndian);
		ds>>size;
		if(_decbytes.size() < size + 4){
			break;  // too small
		}
		
		//QByteArray data( _decbytes.constData()+4,size);
		//_decbytes = _decbytes.right( _decbytes.size() - size - 4);

		QByteArray data( _decbytes.constData(),size+4);
		_decbytes = _decbytes.right( _decbytes.size() - size - 4);

		QByteArray rr;
		rr = qUncompress(data) ;//  zlib uncompress
		//unmarshall ( json )
		parseMessage(rr);
	}// end while
}

//////////////////////////////////////////////////////////////////////////
// 注意: QVariant 保存float变量时必须将float转换为double类型，因为QVariant没有内部float类型，只有double类型
void MessageCodec::GeoSightChanged (GeoRect_t  rect){
	
	cJSON * r,*attrs;
	r = cJSON_CreateObject();	
	attrs = cJSON_CreateArray();	
	cJSON_AddStringToObject(r,"msg","plugin_geosightchanged_1");
	cJSON_AddItemToObject(r,"rect",attrs);

	cJSON_AddItemToArray(attrs,cJSON_CreateNumber(rect.x));
	cJSON_AddItemToArray(attrs,cJSON_CreateNumber(rect.y));
	cJSON_AddItemToArray(attrs,cJSON_CreateNumber(rect.width));
	cJSON_AddItemToArray(attrs,cJSON_CreateNumber(rect.height));

	sendMessage(r);
	cJSON_Delete(r);
}

void MessageCodec::ImagePathClicked(IMAGE_ID  id, unsigned int timetick){
	cJSON * r,*attrs;
	r = cJSON_CreateObject();	
	
	cJSON_AddStringToObject(r,"msg","plugin_imagepathselected_1");
	cJSON_AddStringToObject(r,"id",id);

	cJSON_AddNumberToObject(r,"timestamp",timetick);

	sendMessage(r);
	cJSON_Delete(r);
	
}


/*
//发送socket消息到imagectrl端
void MessageCodec::sendMessage_json(const QVariant& m){
	QJson::Serializer  ser;
	QByteArray bytes,rr;

	bytes = ser.serialize(m);
	printf("serializing:%s\n",(bytes+'\0').constData());
	rr = bytes;
	//rr = qCompress(bytes);
	quint32 size;
	size = rr.size();
	size = htonl(size);
	int r;

	//if( _sock.state() != QAbstractSocket::ConnectedState){
	//	connect_imagesvc();
	//}
	//qCompress 压缩的数据已经添加了4个字节表示大小
	//r = _sock.write((char*)&size,4);
	if(_fd == -1){
		connect_imagesvc();
	}
	r = sendall(_fd,(const char*)&size,4);
	r = sendall(_fd,rr.constData(),rr.size());
	// 	if( !r){
	// 		log(_ctx,"socket::send failed!",0);
	// 		this->close();
	// 		
	// 	}
}*/

//发送socket消息到imagectrl端
void MessageCodec::sendMessage(cJSON* m){
	
	char * bytes;
	bytes = cJSON_Print(m);
	
	
	printf("serializing:%s\n",bytes);
	
	
	quint32 size,size2;
	size2 = size = strlen(bytes);
	size = htonl(size);
	int r;

	if(_fd == -1){
		connect_imagesvc();
	}
	r = sendall(_fd,(const char*)&size,4);
	r = sendall(_fd,bytes,size2);
	free(bytes);
}

bool MessageCodec::sendall(int sock,const char * bytes,size_t size){
	int r;
	char * pb =(char*) bytes;
	while(size){		
		r = ::send(sock,pb,size,0);
		if( r<0){
			return false;
		}
		size -= r;
		pb+=r;
	}
	return true;
}