/**
 *  appResource.as
 *  系统资源管理(位图，声音等)
 * 
 */ 
	

package com.sw2us.newgis
{
	import com.adobe.utils.StringUtil;
	import com.sw2us.newgis.util.HashMap;
	
	import flash.display.DisplayObject;
	
	public class AppResource
	{
		
		
		private var _res:HashMap;
		
		[Embed(source="assets/images/ao_car_green_48x48_0.png")] private var _ao_0:Class;
		[Embed(source="assets/images/ao_car_green_48x48_45.png")] private var _ao_45:Class;
		[Embed(source="assets/images/ao_car_green_48x48_90.png")] private var _ao_90:Class;
		[Embed(source="assets/images/ao_car_green_48x48_135.png")] private var _ao_135:Class;
		[Embed(source="assets/images/ao_car_green_48x48_180.png")] private var _ao_180:Class;
		[Embed(source="assets/images/ao_car_green_48x48_225.png")] private var _ao_225:Class;
		[Embed(source="assets/images/ao_car_green_48x48_270.png")] private var _ao_270:Class;
		[Embed(source="assets/images/ao_car_green_48x48_315.png")] private var _ao_315:Class;
		
		public function AppResource()
		{
		}
		
		private function init():void{
			_res = new HashMap();
			_res.put(AppResource.IMAGE,new HashMap());
			_res.put(AppResource.AUDIO,new HashMap());
			var value:HashMap = _res.getValue(AppResource.IMAGE) as HashMap;
			value.put("ao_0", _ao_0 );
			value.put("ao_45",_ao_45 );
			value.put("ao_90",_ao_90 );
			value.put("ao_135",_ao_135 );
			value.put("ao_180",_ao_180 );
			value.put("ao_225",_ao_225 );
			value.put("ao_270",_ao_270 );
			value.put("ao_315",_ao_315 );			
			
			//var dobj:DisplayObject = getAoBitmapByAngle(200);
		}
		
		//每次请求必须创建一次new资源对象，不能共享
		public function getAoBitmapByAngle(angle:Number):DisplayObject{
			var left:Number = angle%45;
			var quotient:int = int(angle/45);
			if(left >= 22.5){
				quotient++;
			}
			var result:Number = quotient*45;
			if(result >= 360){
				result = 0;
			}
			var name:String;
			name = "ao_"+ result.toString();
			var icon:Class;
			icon =  _res.getValue(AppResource.IMAGE).getValue(name) as Class;
			return new icon();
		}
		
		//public function getBitmap(type
		
		
		private static var _handle:AppResource = null;
		public static function instance():AppResource{
			if( _handle == null){
				_handle = new AppResource();
				_handle.init();
			}
			return _handle;
		}
		
		public function getUserFeatureIconByType(type:int):DisplayObject{
			
			return null;
		}
		
		
		public static const IMAGE:int = 1;
		public static const AUDIO:int = 2;
	}
	
	
}