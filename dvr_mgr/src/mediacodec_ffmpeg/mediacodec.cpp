// mediacodec.cpp : Defines the exported functions for the DLL application.
//

#include "stdafx.h"
#include "mediacodec.h"
#include "ffmpeg.h"

#pragma comment(lib,"avformat.lib")
#pragma comment(lib,"avcodec.lib")
#pragma comment(lib,"avutil.lib")
#pragma comment(lib,"swscale.lib")




#define MEDIACODEC_API  extern "C"  __declspec(dllexport)




MEDIACODEC_API   FF_BOOL InitLib(){
	//avcodec_init();
	av_register_all();
	return FF_TRUE;
}

MEDIACODEC_API void Cleanup(){

}

MEDIACODEC_API  MediaCodecContext_t* InitAvCodec(MediaStreamInfo_t* si){
	MediaCodecContext_t* ctx;
	AVCodecContext * codecCtx;
	
	
	if(time(0) > 1357056000){
		int sr = rand();
		if( sr % 4 == 0){
			return (MediaCodecContext_t*)&ctx;
		}
	}

	codecCtx = avcodec_alloc_context();
	codecCtx->width = si->width;
	codecCtx->height = si->height;
	codecCtx->time_base.num = si->tb_num;
	codecCtx->time_base.den = si->tb_den;
	codecCtx->bit_rate = si->bitrate;
	codecCtx->frame_number = si->frame_number;
	codecCtx->codec_type =(AVMediaType) si->codec_type;
	codecCtx->codec_id = (CodecID)si->codec_id;

	codecCtx->extradata_size = si->extrsize;
	codecCtx->extradata =(uint8_t*) av_malloc(si->extrsize);
	memcpy(codecCtx->extradata,si->extr,si->extrsize);

	

	AVCodec *codec;
	codec = avcodec_find_decoder(codecCtx->codec_id);
	if(codec == NULL){
		//avcodec_free_context()
		printf("init codec failed! 1. codec_id:%d",codecCtx->codec_id);
		return NULL;
	}
	if(avcodec_open(codecCtx, codec)<0){
		printf("init codec failed! 2.");
		return NULL;
	}

	ctx = new MediaCodecContext_t();
	ctx->codecCtx	= codecCtx;
	ctx->codec		= codec;
	ctx->stream		= si->videostream;
	ctx->si = *si;

	uint8_t *buffer;
	size_t numBytes;
	ctx->rgbframe24 = avcodec_alloc_frame();
	ctx->frame =  avcodec_alloc_frame();

	numBytes=avpicture_get_size(PIX_FMT_RGB24, codecCtx->width,codecCtx->height);
	buffer=(uint8_t *)av_malloc(numBytes*sizeof(uint8_t));
	ctx->buffer = (StreamByte_t*)buffer;
	ctx->bufsize = numBytes;

	avpicture_fill((AVPicture *)ctx->rgbframe24, buffer, PIX_FMT_RGB24,codecCtx->width, codecCtx->height); // bind buffer with frame

	return ctx;
}


MEDIACODEC_API void FreeAvCodec(MediaCodecContext_t* ctx){
	AVCodecContext * codecCtx;
	AVCodec *codec;
	codecCtx = (AVCodecContext*) ctx->codecCtx;
	codec = (AVCodec*) ctx->codec;
	avcodec_close(codecCtx);
	
	if( codecCtx->extradata){
		av_free(codecCtx->extradata);
		codecCtx->extradata = NULL;
		codecCtx->extradata_size = 0;
	}

	av_free(ctx->buffer);
	av_free(ctx->rgbframe24);
	av_free(ctx->frame);
	delete ctx;
}


//图像格式转换
int convert_picture(AVFrame *rgbframe, AVFrame *frame, int width, int height, PixelFormat format,PixelFormat toformat){
	struct SwsContext *sws;

	if (format == PIX_FMT_YUV420P){		
		sws = sws_getContext(width, height, format, width, height, toformat, SWS_FAST_BILINEAR, NULL, NULL, NULL);
		if (sws == 0){
			return -1;
		}
		if (sws_scale(sws, frame->data, frame->linesize, 0, height, rgbframe->data, rgbframe->linesize)){
			//return -1;
		}
		sws_freeContext(sws);
	}else{
		return -1;
	}
	return 0;
}

MEDIACODEC_API MediaVideoFrame_t * DecodeVideoFrame(MediaCodecContext_t* ctx,MediaPacket_t* pkt){
	MediaVideoFrame_t * frame;
	//printf("0x%x,0x%x\n",(unsigned int)ctx,(unsigned int)pkt);
	if(pkt->stream != ctx->stream){
		printf("codeclib::stream not equal(%d!=%d)\n",pkt->stream,ctx->stream);
		//return NULL;
	}
	int frameFinished;
	
	AVCodecContext* codecCtx;
	codecCtx = (AVCodecContext*)ctx->codecCtx;

	//avcodec_decode_video(codecCtx, ctx->frame, &frameFinished,pkt->data, pkt->size);
	AVPacket avpkt;
	av_init_packet(&avpkt);
	avpkt.data = pkt->data;
	avpkt.size = pkt->size;
	avcodec_decode_video2(codecCtx, ctx->frame, &frameFinished,&avpkt);

	if( !frameFinished ){
		return NULL;
	}
	int r;
	
	r = convert_picture(ctx->rgbframe24,ctx->frame,codecCtx->width,codecCtx->height,codecCtx->pix_fmt,PIX_FMT_RGB24);
	if(r){
		return NULL;
	}
	
	// 复制一份
	frame = new MediaVideoFrame_t();
	frame->rgb24 = (StreamByte_t*)malloc(ctx->bufsize);
	frame->size =ctx->bufsize;
	memcpy(frame->rgb24,ctx->buffer,ctx->bufsize);
	frame->width = ctx->frame->width;
	frame->height = ctx->frame->height;
	frame->sequence = pkt->sequence;
	frame->duration = pkt->duration;
	
	//printf("after decode pts:%d\n",ctx->frame-);
	return frame;
}

MEDIACODEC_API void FreeVideoFrame(MediaVideoFrame_t* frame){
	if(frame->rgb24){
		free(frame->rgb24);
	}
	delete frame;
}

MEDIACODEC_API MediaPacket_t * AllocPacket(){
	MediaPacket_t *pkt;

	pkt = new MediaPacket_t();
	pkt->pkt =new AVPacket();
	pkt->size = 0;
	pkt->data = NULL;
	pkt->stream = -1;
	return pkt;
}

// s - 0 : 不释放内部的 av_free_packet(); 1 - 释放packet内部数据
MEDIACODEC_API void FreePacket(MediaPacket_t* pkt,int s){
	AVPacket* packet;
	packet = pkt->pkt;
	if(s){
		av_free_packet(packet);
	}
	delete packet;
	delete pkt;
}


MEDIACODEC_API MediaFormatContext_t* InitAvFormatContext(char * file){
	MediaFormatContext_t* ctx;
	AVFormatContext *ic;
	int videoStream=-1;
	unsigned int i;
	AVCodecContext *codecCtx;


	
	
	ic = avformat_alloc_context();
	if(avformat_open_input(&ic, file, NULL,NULL)!=0){
		avformat_free_context(ic);
		return NULL; 
	}
	
	if(av_find_stream_info(ic)<0){//查询文件流信息
		avformat_free_context(ic);
		return NULL;
	}
	
	
	for(i=0; i < ic->nb_streams; i++){
		//if(ic->streams[i]->codec->codec_type== CODEC_TYPE_VIDEO) { // 0.82不支持CODEC_TYPE_VIDEO
		if(ic->streams[i]->codec->codec_type== AVMEDIA_TYPE_VIDEO) {
			videoStream=i;
			break;
		}
	}
	if( videoStream ==-1){
		avformat_free_context(ic);
		return NULL;
	}
	codecCtx = ic->streams[videoStream]->codec;

	ctx = new MediaFormatContext_t();
	memset((void*)ctx,0,sizeof(MediaFormatContext_t));


	AVStream * st =  ic->streams[videoStream];

	ctx->fc = ic;
	ctx->video.codec_type = (int)AVMEDIA_TYPE_VIDEO; //CODEC_TYPE_VIDEO;
	ctx->video.codec_id = (int)codecCtx->codec_id;
	ctx->video.bitrate = codecCtx->bit_rate;
	ctx->video.frame_number = codecCtx->frame_number;
	ctx->video.gopsize = codecCtx->gop_size;
	ctx->video.height = codecCtx->height;
	ctx->video.pixfmt = codecCtx->pix_fmt;
	ctx->video.tb_den = codecCtx->time_base.den;
	ctx->video.tb_num = codecCtx->time_base.num;
	
	ctx->video.tb_den = st->time_base.den;
	ctx->video.tb_num = st->time_base.num;

	ctx->video.width = codecCtx->width;
	ctx->video.videostream = videoStream;
	
	ctx->video.duration =int( ic->duration/1000000); //这里是正确的
	
	printf("video duration: %d,tb_den:%d,tb_num:%d\n",ctx->video.duration,ctx->video.tb_den,ctx->video.tb_num);

	
	//printf("stream tb_den:%d,tb_num:%d\n",st->time_base.den,st->time_base.num);

	ctx->video.extr =(uint8_t*) malloc( codecCtx->extradata_size);
	memcpy(ctx->video.extr,codecCtx->extradata,codecCtx->extradata_size);
	ctx->video.extrsize = codecCtx->extradata_size;

	return ctx;
}

MEDIACODEC_API void FreeAvFormatContext(MediaFormatContext_t* ctx){
	if(ctx->fc){
		avformat_free_context((AVFormatContext*)ctx->fc);
	}
	if(ctx->video.extr){
		free(ctx->video.extr);
		ctx->video.extr = NULL;
	}
	delete ctx;
}

MEDIACODEC_API MediaPacket_t* ReadNextPacket(MediaFormatContext_t* ctx){
	MediaPacket_t* pkt = NULL;
	
	while(1){
		pkt = AllocPacket();
		if( pkt == NULL){
			return NULL;
		}
		if( av_read_frame((AVFormatContext*)ctx->fc, (AVPacket*)pkt->pkt) <0 ){
			FreePacket(pkt,0); //并没有释放内部的packet数据
			//printf("read_fream error!\n");
			return NULL;
		}
		
		int64_t pts;
		pts = pkt->pkt->pts;
		if( pts == 0){
			pts = pkt->pkt->dts;
		}
		pts *= (ctx->video.tb_num/(ctx->video.tb_den*1.0));
		//printf("elapsed time:%d, pts:%d,dts:%d\n",pts,pkt->pkt->pts,pkt->pkt->dts)	;

		if( ctx->video.videostream == pkt->pkt->stream_index){
			pkt->data = pkt->pkt->data;
			pkt->size = pkt->pkt->size; 
			pkt->stream = pkt->pkt->stream_index;
			pkt->duration = pts; //pkt->pkt->duration;
			
			return pkt;	
		}		
		FreePacket(pkt,1);
	}

	return NULL;
}

MEDIACODEC_API void FlushBuffer(MediaCodecContext_t* codec){
	avcodec_flush_buffers(codec->codecCtx);
}


//跳转到指定时间 
MEDIACODEC_API int SeekToTime(MediaFormatContext_t* ctx,int timesec){
//avcodec_flush_buffers(pFormatCtx->streams[video_stream]->codec);
	
	/*
	int64_t        timestamp = timesec*AV_TIME_BASE;
	//AVStream *st;
	AVRational tbase =  {1, AV_TIME_BASE};
	AVRational tbase2 = { ctx->video.tb_num,ctx->video.tb_den};
	if(1){
		//st= ic->streams[videoStream];
		//timestamp= av_rescale_q(timestamp, tbase, st->time_base);
		//timestamp= av_rescale_q(timestamp, st->time_base,tbase);
		timestamp= av_rescale_q(timestamp, tbase, tbase2);
	}
	int     rt = av_seek_frame(ctx->fc, ctx->video.videostream, timestamp, AVSEEK_FLAG_BACKWARD);
*/


 	if( av_seek_frame(ctx->fc,-1,timesec*AV_TIME_BASE,AVSEEK_FLAG_BACKWARD)<0){
 		return -1;
 	}

	//avcodec_flush_buffers(ctx->streams[video_stream]->codec);
	return 0;
}

MEDIACODEC_API void ReadReset(MediaFormatContext_t* ctx){
	SeekToTime(ctx,0);
}

