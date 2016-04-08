
#ifndef _FFMPEG_LIB_H
#define _FFMPEG_LIB_H

#include <Windows.h>

extern "C" {

#include "libavformat/avformat.h"
#include "libavcodec/avcodec.h"
#include "libavutil/avutil.h"
#include "libswscale/swscale.h"
#include "libavdevice/avdevice.h"
}

#define FF_BOOL int
#define FF_TRUE 1
#define FF_FALSE 0

typedef unsigned char  StreamByte_t;

//��Ƶ����Ϣ
struct MediaStreamInfo_t{
	int codec_type;
	int codec_id;
	int width;
	int height;
	int gopsize;
	int pixfmt;
	int tb_num;
	int tb_den;
	int bitrate;
	int frame_number;
	int videostream; //��Ƶ�����
	int duration;	//ʱ��
	uint8_t *extr ;
	int extrsize;
};

struct MediaVideoFrame_t{
	StreamByte_t *	rgb24;
	size_t			size;
	int				width;
	int				height;
	unsigned int	sequence; //���Ʋ���˳��
	unsigned int	duration; //����ʱ��
};

struct MediaPacket_t{
 	StreamByte_t*	data;
 	size_t			size;
	AVPacket	*	pkt;
	int				stream;	//����� 
	int				dts;
	int				pts;
	size_t			sequence;
	size_t			duration;

};

struct MediaFormatContext_t;

//������
struct MediaCodecContext_t{
	AVCodecContext * codecCtx;	//AVCodecContext*
	AVCodec *		codec;	
	int				stream; //�����
	AVFrame *		rgbframe24; //
	AVFrame*		frame;	//
	StreamByte_t*	buffer;
	size_t			bufsize;
	void *			user;
	MediaStreamInfo_t si;
};

struct MediaFormatContext_t{
	AVFormatContext * fc; //AVFormatContext* 
	MediaStreamInfo_t video;	//��Ƶ��Ϣ
	
};
// 

#ifndef MEDIACODEC_EXPORTS


#ifdef __cplusplus
 extern "C" {  
#endif

FF_BOOL InitLib();
void Cleanup();

MediaCodecContext_t* InitAvCodec(MediaStreamInfo_t* si);
void FreeAvCodec(MediaCodecContext_t* codec);

MediaVideoFrame_t * DecodeVideoFrame(MediaCodecContext_t* ctx,MediaPacket_t* pkt);
void FreeVideoFrame(MediaVideoFrame_t* frame);

MediaPacket_t * AllocPacket();
void FreePacket(MediaPacket_t* pkt);

MediaFormatContext_t* InitAvFormatContext(char * file); //ý���ļ����������ģ�����
void FreeAvFormatContext(MediaFormatContext_t* ctx); //�ͷ�
MediaPacket_t* ReadNextPacket(MediaFormatContext_t* ctx);
void ReadReset(MediaFormatContext_t* ctx) ; //����ý����ʶ�ȡλ��
int SeekToTime(MediaFormatContext_t* fc,int timesec) ; //��Ծ��ָ��ʱ��


#ifdef __cplusplus
}
#endif

#endif




#endif