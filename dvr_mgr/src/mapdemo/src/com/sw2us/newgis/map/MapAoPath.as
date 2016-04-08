/**
 * 
 *  MapAoPath - ao对象运动轨迹
 *   单线 , 考虑应用的负责可以修改为MultiLineStringFeature
 * 
 * 
 * */
package com.sw2us.newgis.map
{	
	import com.sw2us.newgis.ActiveObjectData;
	
	import flash.display.Sprite;
	import flash.geom.Point;
	import flash.geom.Rectangle;
	import flash.text.TextField;
	import flash.text.TextFormat;
	import flash.text.TextFormatAlign;
	
	import org.openscales.core.StringUtils;
	import org.openscales.core.basetypes.maps.HashMap;
	import org.openscales.core.events.MapEvent;
	import org.openscales.core.feature.*;
	import org.openscales.core.layer.FeatureLayer;
	import org.openscales.core.layer.Layer;
	import org.openscales.core.style.*;
	import org.openscales.core.style.stroke.*;
	import org.openscales.core.style.symbolizer.*;
	import org.openscales.geometry.*;
	import org.openscales.geometry.basetypes.Location;
	import org.openscales.geometry.basetypes.Pixel;
	
	public class MapAoPath extends LineStringFeature
	{
		private var _mao:MapAo;
		//private var _ticks:Array; //时间标签
		private var _tickgap:int;	//时间间隔 
		//private var _visible:Boolean = false;
		private var _tickvisible:Boolean = false;
		private var _markers:Array= new Array(); //路径时间标记
		private var _tickshowmode:int = MapAoPathMarker.SHOWMODE_DEFAULT;
		private var _pathlinevisible:Boolean = true;	//是否显示行驶轨迹线
		
		private static const LOSTPATH_DISTANCE:Number = 1/50;	// degree 
		
		
		public function MapAoPath(mao:MapAo,layer:MapAoLayer)
		{
			super(new LineString(new Vector.<Number>() ),null,this.getDefaultStyle());
			_mao = mao;
			//var flayer:FeatureLayer = layer as FeatureLayer;
			layer.addFeature(this);			
			_tickgap = 60;	//默认间隔5分钟			
			setVisible(false);
			//_tickvisible = true;
		}
		
		public function get mao():MapAo{
			return _mao;
		}
		//设置时钟标签时间间隔
		public function setTickTimeGap(gap:int):void{
				_tickgap = gap;
				if(this._tickvisible){
					reload();
				}
		}
		
		public function getTickTimeGap():int{
			return _tickgap;
		}
		
		public function setPathLineVisible(v:Boolean):void{
			_pathlinevisible = v;
			reload();
		}
		
		public function pathLineVisible():Boolean{
			return _pathlinevisible;
		}
		
		public  function setVisible(v:Boolean):void{
			var t:Boolean = super.visible;			
			super.visible = v;
			if( v == false){
				setTicksVisible(v);
			}
			if(v){
				//绑定地图缩放事件
				this.layer.map.addEventListener(MapEvent.MOVE_END,onMapMoveEnd);
				reload();
			}else{
				this.layer.map.removeEventListener(MapEvent.MOVE_END,onMapMoveEnd);
			}			
		}
	
		
		private function onMapMoveEnd(event:MapEvent):void{
			if( event.newZoom == event.oldZoom){
				return;  //不是缩放不处理
			}
			reload();
		}
		
		
		public function getVisible():Boolean{
			return this.visible;
		}
		
		
		//设置时间标签可见
		public function setTicksVisible(b:Boolean):void{
			/*
			var f:Feature;
			var layer:FeatureLayer = this.layer as FeatureLayer;			
			if( _tickvisible == false){
				for(var n:int=0;n<this._markers.length;n++){
					f = _markers[n] as Feature;
					layer.removeFeature(f);				
				}
				_markers.splice(0);				
				if(b == true){
					_tickvisible = b;								
					reload();
				}
			}	*/
			_tickvisible = b;		
			reload();
		}
		//
		public function ticksVisible():Boolean{
			if(this.visible == false){
				return false;
			}			
			return _tickvisible ;
		}
		
		//显示方向标记还是时间
		public function setTickShowMode(mode:int):void{
			var n:int;
			for(n=0;n<_markers.length;n++){
				var m:MapAoPathMarker =_markers[n]  as MapAoPathMarker;
				m.setShowMode(mode);
			}
			_tickshowmode = mode;
		}
		
		public function tickShowMode():int{
			return _tickshowmode;
		}
		
		
		//public function load
		//读取ao路径
		/*
			1. 要检测中间无效gps定位信息并过滤
			2. 对于两点之间大区域的跳跃，只选择跳跃之后的连续gps信息
		*/
		public function reload():void{
			/*
			if( this.visible == false){
				return;
			}*/
			var ptset:Vector.<Number> = new Vector.<Number>();
			var gpsdata:Array = _mao.getActiveObject().getDataQueue().getDataList(ActiveObjectData.GPS);
			var lastloc:Location = null;
			
			var lstr:LineString = this.geometry as LineString;			
			//lstr.components = new LineString(new Vector.<Number>());
			lstr.components = null;
			
			var ticks:Array = new Array(); //路径标签 
			
			for(var n:int=gpsdata.length-1;n>=0;n--){
				if( gpsdata[n].lon == 0 || gpsdata[n].lat ==0){
					continue; //无效gps信息过滤
				}
				if( lastloc != null){
					var p1:org.openscales.geometry.Point = new  org.openscales.geometry.Point(lastloc.x,lastloc.y);
					var p2:org.openscales.geometry.Point = new org.openscales.geometry.Point(gpsdata[n].lon,gpsdata[n].lat);
					var dist:Number = p1.distanceTo(p2);
										
					if( p1.distanceTo(p2) > LOSTPATH_DISTANCE){
						trace(dist);
						break;
					}				
				}				
				lastloc = new Location( gpsdata[n].lon,gpsdata[n].lat );				
				ptset.push(gpsdata[n].lat);
				ptset.push(gpsdata[n].lon);				
				
				//创建时间标签轨迹, 这个遍历是倒序的所以要将gps数据插入队列头部
				if( this._tickvisible ){					
					ticks.splice(0,0,gpsdata[n]);					
				}				
			}
			
			//if( this._tickvisible  && ticks.length ){
			createTickMarkers(ticks);
			//}
			
			if(ptset.length<4){								
				this.draw();
				return;
			}
			ptset = ptset.reverse();			
			trace("ptset size:",ptset.length);
			//var lstr:LineString = this.geometry as LineString;
			if( pathLineVisible() ){
				lstr.components = ptset;
			}
			this.draw();
			this.layer.setChildIndex(this,0); // 道路必须设置在mao下面
		}	
	
		public function deleteThis():void{
			var flayer:FeatureLayer = this.layer as FeatureLayer;
			for(var n:int=0;n<this._markers.length;n++){
				var f:MapAoPathMarker = _markers[n] as MapAoPathMarker;
				f.clear();				
				flayer.removeFeature(f);						
			}			
			flayer.removeFeature(this);
		}
		//显示时间标记 
		private function createTickMarkers(ticks:Array):void{
			var f:MapAoPathMarker ;
			var n:int;
			var layer:FeatureLayer = this.layer as FeatureLayer;
			
			for(n=0;n<this._markers.length;n++){
				f = _markers[n] as MapAoPathMarker;
				f.clear();
				layer.removeFeature(f);				
			}
			_markers.splice(0);
			
			var d:Object;
			var lasttick:Object = null;
			for(n=0;n<ticks.length;n++){				
				d = ticks[n];
				if( lasttick != null){
					if( d.time - lasttick.time < this._tickgap){
						continue;  //时间间隔过小直接忽略
					}
				}
				lasttick = d;

				//检查两个 marker是否相碰撞
				var rc1:Rectangle ;
				var rc2:Rectangle;
				var rc3:Rectangle;

				var m:MapAoPathMarker;
				m = new MapAoPathMarker(this);
				m.setData(d);
				rc1 = m.getBounds(this.layer.map);
				rc3 = this._mao.getMarker().getBounds(this.layer.map);
				
				if( rc1.intersects(rc3) ){
					layer.removeFeature(m);
					m = null;					
					continue;
				}
				
				if( _markers.length == 0){					
					_markers.push(m);
					continue;
				}
								
				
				var m2:MapAoPathMarker;
				m2 = _markers[_markers.length-1]  as MapAoPathMarker;
				rc2 =  m2.getBounds(this.layer.map);
				
				
				if(rc1.intersects(rc2)    ){ //timetick 不能相交 ，而且不能与mao's marker 相交 					
					layer.removeFeature(m);
					m = null;					
					continue;
				}
				_markers.push(m); //不与相邻marker相交则显示				
			}
			//trace("markers size",_markers.length);
		}
		
		private  function getDefaultStyle():Style {
			
			var rule:Rule = new Rule();
			rule.name = "Default rule";
			rule.symbolizers.push(new LineSymbolizer(new Stroke(0xff0000, 5,0.3)));
			//rule.symbolizers.push(new LineSymbolizer(new Stroke(0x40A6D9, 1)));
			
			var style:Style = new Style();
			style.name = "Default line style";
			style.rules.push(rule);
			return style;
		}
		
		
	}
}