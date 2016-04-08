#pragma once

#include <QtCore>
#include <QTcpSocket>
#include "imageplugin.h"
#include <map>
 #include <QThread>
#include "cJSON.h"

class MessageCodec:public QObject{
	Q_OBJECT

public:
	MessageCodec(PluginContext_t* ctx);
	bool open(const QString& host="localhost" ,const short port=12016);
	void close();
	void GeoSightChanged (GeoRect_t  rect);
	void ImagePathClicked (IMAGE_ID  id, unsigned int timetick);
public slots:
	void	connected ();
	void	disconnected ();
	void	error ( QAbstractSocket::SocketError socketError );
	void	readyRead() ;
private:	
	static void	thread_recv (void* p );
	static void	thread_keepalive (void* p );
	void do_recv();
private:
	void parseMessage(QByteArray & bytes);
	void sendMessage(cJSON* json);

	//void sendMessage_json(const QVariant& m);

	//void parseMessage_qjson(QByteArray & bytes);
	bool connect_imagesvc();
	bool sendall(int sock,const char * bytes,size_t size);
private:
	int		_status;  // 0 - closed;  1 - openned
	int		_threadstatus;
	QTcpSocket	_sock;
	int _fd;	//socket fd
	QThread _thread;

	PluginContext_t * _ctx;

	std::pair<QString,short> _svcaddr;	

	qint64 _leftbytes ;
	QByteArray _decbytes;
	
};
