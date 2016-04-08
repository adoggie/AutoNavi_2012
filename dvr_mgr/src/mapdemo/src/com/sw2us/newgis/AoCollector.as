package com.sw2us.newgis
{
	/**
	 * DataCollecotr
	 * 数据收集器
	 * ao对象的所有从dgw过来的数据都存储在这里
	 * */
	//import com.adobe.utils.ArrayUtil;
	import com.adobe.utils.DictionaryUtil;
	
	import flash.events.EventDispatcher;
	import flash.utils.Dictionary;
	
	import mx.utils.ArrayUtil;
	//import com.adobe.utils.ArrayUtil;
	
	[Event(name="aoData",type="ActiveObjectEvent")]
	
	public class AoCollector extends EventDispatcher
	{
		public static const COLLECTOR_DEFAULT:int =1;
		public static const COLLECTOR_REPLAY:int = 2;
		
		private var _channel:ActiveObjectChannel ;
		
		public function AoCollector()
		{
			_channel = new ActiveObjectChannel(this);
		}
		
		private static var _handle:AoCollector = null;
		private var _aodict:Dictionary = new Dictionary();
		
		//每一个ao根据每一个
	
		public static function instance():AoCollector{
			if( _handle == null){
				_handle = new AoCollector();
			}
			return _handle;
		}
		
		public  function recvData(data:Object):Boolean{
			var evt:ActiveObjectEvent = new ActiveObjectEvent("aoData");
			evt.data = data;
			//触发给接收者
			dispatchEvent(evt);
			return true;
		}
		
		public function getData(aoid:int,module:int):Object{
			var keys:Array  = DictionaryUtil.getKeys(_aodict);
			if( ArrayUtil.getItemIndex(aoid,keys) ==-1){
				return null;		
			}
			//var q:AoDataQueue = _aodict[aoid] as AoDataQueue;
			var ao:ActiveObject = _aodict[aoid];			
			return ao.getModuleData(module);
		}
		
		public function getActiveObject(aoid:int):ActiveObject{
			var keys:Array  = DictionaryUtil.getKeys(_aodict);
			if( ArrayUtil.getItemIndex(aoid,keys) ==-1){
				return null;		
			}
			//var q:AoDataQueue = _aodict[aoid] as AoDataQueue;
			var ao:ActiveObject = _aodict[aoid];			
			return ao;
		}
		
		public function getAcitveObjectList():Array{
			return new Array();
		}
		
		public function addActiveObject(ao:ActiveObject):void{
			_aodict[ao.getId()] = ao;
		}
		
		
		public function removeActiveObject(aoid:int):void{
			var keys:Array = DictionaryUtil.getKeys(_aodict);
			if( ArrayUtil.getItemIndex(aoid,keys) !=-1){
				var ao:ActiveObject = _aodict[aoid] as ActiveObject;
				ao.deleteThis();  //删除所有地图上关联的path，marker等对象
				delete _aodict[aoid];
			}
		}
		
		public function clear():void{
			_aodict = new Dictionary();
		}
		
		public function getAoChannel():ActiveObjectChannel{
			return _channel;	
		}
		
		
		
		
	}
}