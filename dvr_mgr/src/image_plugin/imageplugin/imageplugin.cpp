#include "imageplugin.h"
#include "msgcodec.h"


void GeoSightChanged (PluginContext_t* ctx,GeoRect_t  rect){
	MessageCodec* codec = (MessageCodec*)ctx->delta;
	codec->GeoSightChanged(rect);
}

void ImagePathClicked (PluginContext_t* ctx,IMAGE_ID  id, unsigned int timetick){
	MessageCodec* codec = (MessageCodec*)ctx->delta;
	codec->ImagePathClicked(id,timetick);
}

IMAGEPLUG_API 
Boolean  __declspec(dllexport) init_plugin(PluginContext_t* ctx){
	QByteArray bytes("afdsakdjfkdsaljfasfd");
	QByteArray r;
	r = qCompress(bytes);
	MessageCodec* codec = new MessageCodec(ctx);
	ctx->delta = codec;
	ctx->calls.GeoSightChanged = GeoSightChanged;
	ctx->calls.ImagePathClicked = ImagePathClicked;
	codec->open(ctx->host,ctx->port);
	return True;
}


IMAGEPLUG_API 
void 	 deinit_plugin(PluginContext_t* ctx){
	MessageCodec* codec = (MessageCodec*)ctx->delta;
	codec->close();
	//delete codec;
}