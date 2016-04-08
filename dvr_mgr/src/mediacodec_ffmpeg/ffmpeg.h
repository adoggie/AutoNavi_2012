
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

//视频流信息
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
	int videostream; //视频流编号
	int duration;	//时长
	uint8_t *extr ;
	int extrsize;
};

struct MediaVideoFrame_t{
	StreamByte_t *	rgb24;
	size_t			size;
	int				width;
	int				height;
	unsigned int	sequence; //控制播放顺序
	unsigned int	duration; //播放时间
};

struct MediaPacket_t{
 	StreamByte_t*	data;
 	size_t			size;
	AVPacket	*	pkt;
	int				stream;	//流编号 
	int				dts;
	int				pts;
	size_t			sequence;
	size_t			duration;

};

struct MediaFormatContext_t;

//解码器
struct MediaCodecContext_t{
	AVCodecContext * codecCtx;	//AVCodecContext*
	AVCodec *		codec;	
	int				stream; //流编号
	AVFrame *		rgbframe24; //
	AVFrame*		frame;	//
	StreamByte_t*	buffer;
	size_t			bufsize;
	void *			user;
	MediaStreamInfo_t si;
};

struct MediaFormatContext_t{
	AVFormatContext * fc; //AVFormatContext* 
	MediaStreamInfo_t video;	//视频信息
	
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

MediaFormatContext_t* InitAvFormatContext(char * file); //媒体文件访问上下文，申请
void FreeAvFormatContext(MediaFormatContext_t* ctx); //释放
MediaPacket_t* ReadNextPacket(MediaFormatContext_t* ctx);
void ReadReset(MediaFormatContext_t* ctx) ; //重置媒体访问读取位置
int SeekToTime(MediaFormatContext_t* fc,int timesec) ; //跳跃到指定时间


#ifdef __cplusplus
}
#endif

#endif




#endif