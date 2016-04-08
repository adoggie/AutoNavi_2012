package autonavi.dvr
{
	import mx.controls.Alert;
	
	import org.openscales.core.events.FeatureEvent;
	import org.openscales.core.feature.LineStringFeature;
	import org.openscales.core.layer.FeatureLayer;
	import org.openscales.core.style.Rule;
	import org.openscales.core.style.Style;
	import org.openscales.core.style.stroke.Stroke;
	import org.openscales.core.style.symbolizer.LineSymbolizer;
	import org.openscales.geometry.LineString;

	public class ImagePath
	{
		private var _id:String;
		private var _lines:Array = new Array();
		private var _layer:FeatureLayer;
		
		
		public function getId():String{
			return _id;
		}
		
		public function ImagePath(layer:FeatureLayer, id:String,lines:Array){
			
			var ftr:LineStringFeature ;
			_layer = layer;
			_id = id;
			for( var n:uint=0;n<lines.length;n++){
				var line:Object = lines[n] as Object;
				var d:ImagePathLineData = new ImagePathLineData();
				d.path = this;
				d.gpsdata = line;
				var g:LineString = new LineString(new Vector.<Number>());
				g.addPoint( line.first.lon,line.first.lat);
				g.addPoint(line.second.lon,line.second.lat);
				ftr = new LineStringFeature(g,d,null,true);
				_lines.push(ftr);
				ftr.addEventListener(FeatureEvent.FEATURE_CLICK,this.onFeatureLineClicked);
				_layer.addFeature(ftr);
				trace(line.first.lon,line.first.lat,line.second.lon,line.second.lat);
			}
			setPathSelected(false);
		}
		
		/**
		 *  点击单条线段，令整个path的线段全部被选定
		 **/
		private function onFeatureLineClicked(evt:FeatureEvent):void{
		//	this.setPathSelected(true);
			//Alert.show("abc");
		}	
		/*
		var fill:SolidFill = new SolidFill(0xff0000, 0.4);
		var stroke:Stroke = new Stroke(0xE7FF33, 3);
		
		var rule:Rule = new Rule();
		rule.symbolizers.push( new PolygonSymbolizer(fill, stroke) );
		
		var style:Style = new Style();
		style.name = "Draw surface style_1";
		style.rules.push(rule);
		event.feature.style = style;
		event.feature.draw();					
		*/
		
		
		
		public  function setPathSelected(selected:Boolean=true):void{
			//var fill:SolidFill = new SolidFill(0xff0000, 0.4);
			
			trace("lines:",_lines.length);
			for(var n:uint=0;n<_lines.length;n++){
					var line:LineStringFeature = _lines[n] as LineStringFeature;
					
					var stroke:Stroke;
					if( selected == false){
						stroke = new Stroke(0x0000ff, 3);
					}else{
						stroke = new Stroke(0xff0000, 3);
					}
					var rule:Rule = new Rule();
					rule.symbolizers.push( new LineSymbolizer(stroke) );
					var style:Style = new Style()
					style.name = "Draw surface style_1";
					style.rules.push(rule);
					
					line.style = style;
					line.draw();
					
				}
		}
		
		public function destroy():void{
			for(var n:uint=0;n<_lines.length;n++){
				var line:LineStringFeature = _lines[n] as LineStringFeature;
				line.destroy();
				this._layer.removeFeature( line);
				//line.destroy();
				//delete line;
			}
		}
		////////
		
	}
	
}