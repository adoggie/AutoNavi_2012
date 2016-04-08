package com.sw2us.newgis
{
	import com.sw2us.newgis.util.HashMap;
	
	import flash.system.Security;
	import flash.system.SecurityDomain;
	import flash.system.System;
	
	import mx.managers.BrowserManager;
	import mx.managers.IBrowserManager;
	import mx.utils.URLUtil;
	
	import org.openscales.core.Util;
	import org.openscales.geometry.basetypes.Unit;
	
	public class AppCore
	{
		private var default_hostbase:String = "http://192.168.14.203:8520";				//这两个东东根据部署情况改一下
		private var default_wms_url:String = "http://192.168.14.203:8002/wms";
		
		public function AppCore()
		{
			Security.allowDomain("sw2us.com");
			if(1){
				default_hostbase= "http://sw2us.com:8520";				//这两个东东根据部署情况改一下
				default_wms_url= "http://sw2us.com:9001/wms";
				_hostbase = default_hostbase;
			}
		}
		
		private var _hostbase:String ="" ; // "http://192.168.14.3:9099";
		private var _amfserver:String ="";
		private var _datacolletors:HashMap= new HashMap();
		private var _sysprops:Object  = null;	//系统属性
		
		public  function getHostBaseUrl():String{
			if( _hostbase != ""){
				return _hostbase;
			}
			
			var bm:IBrowserManager = BrowserManager.getInstance();
			bm.init();
			var url:String = bm.url;				
			var port:String = String(URLUtil.getPort(url));
			var protocol:String = URLUtil.getProtocol(url);
			var serverName:String  = URLUtil.getServerName(url);			
			if (protocol.toLowerCase() =="http"){
				_hostbase = protocol+"://"+serverName+":"+port;
			}else{
				_hostbase=default_hostbase;
			}
			return _hostbase;
		}	
		
		public function setAmfServerUrl(url:String):void{
			_amfserver = url;
		}
		
		public function getAmfServerUrl():String{
			if(_amfserver==""){
				_amfserver = getHostBaseUrl()+"/gateway/";
			}
			return _amfserver;
		}
		
		
		public function init():Boolean{
			org.openscales.geometry.basetypes.Unit.DOTS_PER_INCH = 92;
			//AoCollector.instance();
			_datacolletors.put(AoCollector.COLLECTOR_DEFAULT ,new AoCollector() );
			_datacolletors.put(AoCollector.COLLECTOR_REPLAY,new AoCollector())
			AppResource.instance();
			return true;
		}
		
		public function getAoCollector(type:int = 1):AoCollector{
			var o:AoCollector = _datacolletors.getValue(type) as AoCollector; 
			return o;
		}
		
		public function getMapServerUrl():String{
			return default_wms_url;
		}
		
		public function set systemProps(props:Object):void{
			_sysprops = props;
		}
		
		public function get systemProps():Object{
			return _sysprops;
		}
		
		//private var _aochannel:ActiveObjectChannel = new ActiveObjectChannel();
		
		//public function getAoChannel():ActiveObjectChannel{
		//	return _aochannel;
		//}
		
		private static var _handle:AppCore = null;
		public static function instance():AppCore{
			if( _handle == null){
				_handle = new AppCore();
				_handle.init();
			}
			return _handle;
		}
		
		
	}
}