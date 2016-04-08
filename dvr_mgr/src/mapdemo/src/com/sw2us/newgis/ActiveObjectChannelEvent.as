package com.sw2us.newgis
{
	import flash.events.Event;
	public class ActiveObjectChannelEvent extends Event
	{
		public function ActiveObjectChannelEvent(event:String)
		{
			super(event);			
			_event =event;
		}
		private var _event:String;
		public static const CHANNEL_OPENED:String ="channelOpened";
		public static const CHANNEL_CLOSED:String ="channelClosed";
		public static const CHANNEL_DATA:String ="channelData";
		
	}
}