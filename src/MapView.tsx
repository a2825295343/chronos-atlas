import {politicalBorders} from './cartography.mjs';
import {useEffect,useRef} from 'react';
import * as maplibregl from 'maplibre-gl';
import workerUrl from 'maplibre-gl/dist/maplibre-gl-worker.mjs?url';
import type {Feature,FeatureCollection,Geometry,Polygon} from 'geojson';
import {colorForName,featureCenter,pointInGeometry,areaKm2,territoryBounds} from './history.mjs';
import {events,localName,occupations,places,placeName} from './data';
import {buildAtlasFrame} from './atlas-render.mjs';
import {mapName} from './map-names.mjs';
import {polygonRenderParts} from './polygon-render.mjs';
import {installOceanRipples} from './ocean';
import {updateTerrainScale} from './terrain.mjs';
import {perspectiveForZoom} from './temporal.mjs';
import {referenceSitesAtYear} from './reference-sites.mjs';
import {capitalsAtYear} from './capitals.mjs';
import {curatedData} from './archive';
import capitalIndex from '../public/data/map-capitals.json';
import {paleogeographyAt} from './paleogeography.mjs';

export type AtlasFeature=Feature<Geometry,Record<string,any>>;
export type Selection={kind:'country'|'province'|'place'|'occupation'|'site';feature?:AtlasFeature;id?:string;name:string;position?:[number,number]};
export type Layers={terrain:boolean;labels:boolean;events:boolean;provinces:boolean;occupation:boolean;autoView:boolean};
export type MapHandle={fly:(position:[number,number],zoom?:number)=>void;flyToPolity:(name:string)=>void;zoom:(delta:number)=>void;reset:()=>void;tilt:()=>void;globe:()=>void;screenshot:()=>void};
type Props={regionSelection?:Selection|null;data:FeatureCollection|null;year:number;layers:Layers;selected:string|null;onSelect:(s:Selection|null)=>void;onZoom:(z:number)=>void;onReady:(h:MapHandle)=>void;onError:(message:string)=>void};
const empty:FeatureCollection={type:'FeatureCollection',features:[]};
maplibregl.setWorkerUrl(workerUrl);
export function prepare(data:FeatureCollection):FeatureCollection {
 return {...data,features:data.features.filter(f=>f.geometry&&f.properties?.NAME?.trim()).map((f,i)=>({...f,id:i,properties:{...f.properties,id:i,owner:f.properties?.SUBJECTO?.trim()||f.properties?.NAME,label:mapName(f.properties,localName),ownerLabel:f.properties?.displayName||localName(f.properties?.SUBJECTO?.trim()||f.properties?.NAME),color:f.properties?.thematicColor||colorForName(f.properties?.SUBJECTO?.trim()||f.properties?.NAME)}}))};
}
export default function MapView(props:Props){
 const container=useRef<HTMLDivElement>(null),mapRef=useRef<maplibregl.Map|null>(null),ready=useRef(false),latest=useRef(props),generation=useRef(0),lastData=useRef<FeatureCollection|null>(null),lastTerrain=useRef<string|null>(null),provinceData=useRef(new Map<string,AtlasFeature>()),hdReady=useRef(false),viewFrame=useRef<number|null>(null),terrainScale=useRef(0);
 const lastSelectionFrame=useRef<{data:FeatureCollection|null;owner:string|null}|null>(null);
 const lastCapitalFrame=useRef<{data:FeatureCollection|null;year:number}|null>(null);
 const regionTimer=useRef<ReturnType<typeof setTimeout>|null>(null);
 const regionWorker=useRef<Worker|null>(null),regionRequest=useRef(0);
 const referenceSites=useRef<FeatureCollection>(empty),siteFeatures=useRef(new Map<string,AtlasFeature>());
 const paleoIndex=useRef<any>(null),paleoKey=useRef('modern'),paleoGeneration=useRef(0);
 const paleoCache=useRef(new Map<string,[FeatureCollection,FeatureCollection]>());
 const modernRegions=useRef<FeatureCollection>(empty),historicalRegions=useRef<FeatureCollection>(empty),lastRegionYear=useRef<number|null>(null),lastRegionWorld=useRef<FeatureCollection|null>(null);
 const viewportLabelsKey=useRef(''),viewportView=useRef(''),viewportWorld=useRef<FeatureCollection|null>(null);
 latest.current=props;
 function refreshViewportLabels(){
  const map=mapRef.current;if(!map||!ready.current||!map.getLayer('country-label'))return;
  const source=map.getSource('viewport-labels') as maplibregl.GeoJSONSource|undefined;if(!source)return;
  if(!map.isSourceLoaded('countries')||!map.isSourceLoaded('country-labels'))return;
  const center=map.getCenter(),view=[center.lng.toFixed(3),center.lat.toFixed(3),map.getZoom().toFixed(2),map.getBearing().toFixed(1),map.getPitch().toFixed(1),latest.current.layers.labels].join('|');
  if(view===viewportView.current&&viewportWorld.current===latest.current.data)return;
  viewportView.current=view;viewportWorld.current=latest.current.data;
  const visible=new Map<string,Set<string>>(),compact=new Set<string>();
  for(const f of map.queryRenderedFeatures({layers:['country-label']})){
   const name=f.properties.owner;if(f.properties.compact)compact.add(name);
   if(!visible.has(name))visible.set(name,new Set());visible.get(name)!.add(f.properties.name);
  }
  const anchors=new Map<string,{position:[number,number];name:string;score:number}>(),canvas=map.getCanvas(),w=canvas.clientWidth,h=canvas.clientHeight;
  if(map.getZoom()<5.7)for(const x of [.14,.35,.55,.76,.9])for(const y of [.12,.34,.56,.78]){
   const screen:[number,number]=[w*x,h*y],feature=map.queryRenderedFeatures(screen,{layers:['country-fill']})[0];if(!feature)continue;
   const name=feature.properties.NAME,label=feature.properties.label;
   if(compact.has(name)||(visible.get(name)?.size||0)>=Math.min(2,Array.from(label).length))continue;
   const score=1-Math.hypot(x-.5,y-.5),old=anchors.get(name);
   if(!old||score>old.score){const ll=map.unproject(screen);anchors.set(name,{position:[Math.round(ll.lng*10)/10,Math.round(ll.lat*10)/10],name:label,score});}
  }
  const features=[...anchors.entries()].map(([owner,row])=>({type:'Feature' as const,properties:{owner,name:row.name},geometry:{type:'Point' as const,coordinates:row.position}}));
  const key=JSON.stringify(features);if(key!==viewportLabelsKey.current){viewportLabelsKey.current=key;source.setData({type:'FeatureCollection',features});}
 }
 function updateRegions(){
  const map=mapRef.current,p=latest.current;
  if(!map||!ready.current||(map.getZoom()<4.2&&!p.regionSelection)||!modernRegions.current.features.length||(lastRegionYear.current===p.year&&lastRegionWorld.current===p.data))return;
  if(!regionWorker.current)return;
  lastRegionYear.current=p.year;lastRegionWorld.current=p.data;
  regionWorker.current.postMessage({id:++regionRequest.current,world:p.data,year:p.year});
 }
 function applyRegions(collection:FeatureCollection){
  const map=mapRef.current,p=latest.current;if(!map||!ready.current)return;
  provinceData.current=new Map(collection.features.map(f=>[f.properties?.id,f as AtlasFeature]));
  void (map.getSource('provinces') as maplibregl.GeoJSONSource).setData({...collection,features:collection.features.filter(f=>!f.properties?.locatorOnly)});
  void (map.getSource('province-labels') as maplibregl.GeoJSONSource).setData({type:'FeatureCollection',features:collection.features.map(f=>({type:'Feature',properties:f.properties,geometry:{type:'Point',coordinates:f.geometry.type==='Point'?f.geometry.coordinates:(f.properties?.labelPosition??featureCenter(f.geometry))}}))});
  if(p.regionSelection?.position){
   const point=p.regionSelection.position;
   const locator=p.regionSelection.feature?.properties.locatorOnly
    ?collection.features.find(f=>f.properties?.locatorOnly&&f.geometry.type==='Point'&&f.geometry.coordinates.every((value,i)=>value===point[i])):undefined;
   const feature=locator||collection.features.find(f=>pointInGeometry(point,f.geometry));
   p.onSelect(feature?{kind:'province',feature:feature as AtlasFeature,name:feature.properties?.label,position:point}:null);
  }
 }
 function update(){
  const map=mapRef.current,p=latest.current;if(!map||!ready.current)return;
  updatePaleogeography();
  if(p.data!==lastData.current){
  const frame=p.data?((p.data as any).atlas?p.data:buildAtlasFrame(p.data,localName)):empty;
  void (map.getSource('countries') as maplibregl.GeoJSONSource).setData((frame as any).atlas?.fills||empty);
  void (map.getSource('borders') as maplibregl.GeoJSONSource).setData((frame as any).atlas?.borders||empty);
  void (map.getSource('country-labels') as maplibregl.GeoJSONSource).setData((frame as any).atlas?.labels||empty);
  lastData.current=p.data;
  }
  if(lastCapitalFrame.current?.data!==p.data||lastCapitalFrame.current?.year!==p.year){
   const capitals=capitalsAtYear(p.data,p.year,capitalIndex,curatedData.identities);
   void (map.getSource('capitals') as maplibregl.GeoJSONSource).setData(capitals);
   const ordinaryPlaces=places.filter(place=>!capitals.features.some(({geometry})=>
    Math.abs(place.position[0]-geometry.coordinates[0])<0.09&&Math.abs(place.position[1]-geometry.coordinates[1])<0.09));
   void (map.getSource('places') as maplibregl.GeoJSONSource).setData({
    type:'FeatureCollection',features:ordinaryPlaces.map(place=>({type:'Feature',geometry:{type:'Point',coordinates:place.position},properties:{id:place.id,name:placeName(place,p.year)}}))
   });
   lastCapitalFrame.current={data:p.data,year:p.year};
  }
  (map.getSource('events') as maplibregl.GeoJSONSource).setData({type:'FeatureCollection',features:events.filter(e=>e.year===p.year).map(e=>({type:'Feature',geometry:{type:'Point',coordinates:e.location},properties:{name:e.title}}))});
  const sites=referenceSitesAtYear(referenceSites.current,p.year);
  siteFeatures.current=new Map(sites.features.map(f=>[f.properties?.id,f as AtlasFeature]));
  (map.getSource('reference-sites') as maplibregl.GeoJSONSource).setData(sites);
  const controllerColor=(name:string)=>{const parent=p.data?.features.find(f=>!f.properties?.controlArea&&(f.properties?.NAME===name||(name==='Germany'&&['Nazi Germany','German Empire','Weimar Republic'].includes(f.properties?.NAME))));return parent?.properties?.thematicColor||colorForName(name);};
  const activeControls=(p.data?.features||[]).filter(f=>f.properties?.controlArea&&f.properties.validFrom<=p.year&&p.year<=f.properties.validTo);
  const active=occupations.filter(o=>p.year>=o.from&&p.year<=o.to&&!activeControls.some(f=>f.properties?.sovereignName?.includes('France')&&o.sovereign.includes('France')));
  const control=activeControls.map(f=>({type:'Feature' as const,geometry:f.geometry,properties:{...f.properties,id:f.properties?.controlId||f.properties?.id,name:f.properties?.displayName,color:controllerColor(f.properties?.controller)}}));
  const occupationFeatures=[...active.map(o=>({type:'Feature' as const,geometry:{type:'Polygon',coordinates:[o.coordinates]} as Polygon,properties:{id:o.id,name:o.title,color:controllerColor(o.occupier),pattern:''}})),...control];
  for(const f of occupationFeatures){
   const color=f.properties.color,id='hatch-'+color.replace('#','');
   if(!map.hasImage(id)){const canvas=document.createElement('canvas');canvas.width=16;canvas.height=16;const ctx=canvas.getContext('2d')!;ctx.strokeStyle=color;ctx.lineWidth=3;for(let x=-16;x<=32;x+=16){ctx.beginPath();ctx.moveTo(x,16);ctx.lineTo(x+16,0);ctx.stroke();}map.addImage(id,ctx.getImageData(0,0,16,16));}
   (f.properties as any).pattern=id;
  }
  (map.getSource('occupations') as maplibregl.GeoJSONSource).setData(polygonRenderParts({type:'FeatureCollection',features:occupationFeatures}));
  if(lastSelectionFrame.current?.data!==p.data||lastSelectionFrame.current?.owner!==p.selected){
   const selectedParts=p.selected?(p.data?.features||[]).filter(f=>!f.properties?.controlArea&&
    (f.properties?.SUBJECTO?.trim()||f.properties?.NAME)===p.selected):[];
   void (map.getSource('selection-borders') as maplibregl.GeoJSONSource).setData(politicalBorders({type:'FeatureCollection',features:selectedParts}));
   lastSelectionFrame.current={data:p.data,owner:p.selected};
  }
  const selectedRegion=p.regionSelection?.feature?.properties;
  map.setFilter('province-selection',['==',['get','id'],selectedRegion&&!selectedRegion.locatorOnly?(selectedRegion.id??''):'']);
  for(const id of ['country-label','country-label-viewport','ocean-label','place-label','reference-site-label','capital-label']) map.setLayoutProperty(id,'visibility',p.layers.labels?'visible':'none');
  for(const id of ['province-line','province-reference-line','province-selection'])map.setLayoutProperty(id,'visibility',p.layers.provinces?'visible':'none');
  map.setLayoutProperty('province-label','visibility',p.layers.provinces&&p.layers.labels?'visible':'none');
  for(const id of ['event-dot','event-label'])map.setLayoutProperty(id,'visibility',p.layers.events?'visible':'none');
  for(const id of ['occupation-base','occupation-pattern','occupation-line'])map.setLayoutProperty(id,'visibility',p.layers.occupation?'visible':'none');
  map.setLayoutProperty('hillshade','visibility',p.layers.terrain&&!hdReady.current?'visible':'none');
  if(map.getLayer('hillshade-hd'))map.setLayoutProperty('hillshade-hd','visibility',p.layers.terrain&&hdReady.current?'visible':'none');
  if(regionTimer.current)clearTimeout(regionTimer.current);regionTimer.current=setTimeout(updateRegions,260);
  syncPerspective();
 }
 function syncPerspective(){
  const map=mapRef.current;if(!map||!ready.current)return;
  const layer=latest.current.layers,view=perspectiveForZoom(map.getZoom());

  const terrain=layer.terrain&&latest.current.year>=-4000;
  const source=hdReady.current?'elevation-hd':'elevation',key=terrain?source:'none';
  if(lastTerrain.current!==key||Math.abs(terrainScale.current-view.exaggeration)>.045){
   if(lastTerrain.current!==key||!terrain||!updateTerrainScale(map,view.exaggeration))map.setTerrain(terrain?{source,exaggeration:view.exaggeration}:null);
   lastTerrain.current=key;terrainScale.current=view.exaggeration;
  }
 }
 function updatePaleogeography(){
  const map=mapRef.current;if(!map||!ready.current)return;
  const slice=paleogeographyAt(paleoIndex.current,latest.current.year),key=slice?.key||'modern';
  for(const id of ['lakes','rivers'])map.setLayoutProperty(id,'visibility',slice?'none':'visible');
  map.setLayoutProperty('aral-historical-water','visibility',!slice&&latest.current.year<1992?'visible':'none');
  if(key===paleoKey.current)return;
  paleoKey.current=key;const token=++paleoGeneration.current;
  const apply=(land:FeatureCollection,ocean:FeatureCollection)=>{
   if(token!==paleoGeneration.current||map!==mapRef.current)return;
   (map.getSource('land') as maplibregl.GeoJSONSource).setData(polygonRenderParts(land));
   (map.getSource('ocean-mask') as maplibregl.GeoJSONSource).setData(ocean);
  };
  const cached=paleoCache.current.get(key);if(cached){apply(...cached);return;}
  const paths=slice?[`/data/paleogeography/land-${key}.geojson`,`/data/paleogeography/ocean-render-${key}.geojson`]:['/data/ne_10m_land.geojson','/data/ocean-mask-render.geojson'];
  Promise.all(paths.map(url=>fetch(url).then(r=>{if(!r.ok)throw Error('古地理图层');return r.json();}))).then(([land,ocean])=>{
   paleoCache.current.set(key,[land,ocean]);if(paleoCache.current.size>4)paleoCache.current.delete(paleoCache.current.keys().next().value!);apply(land,ocean);
  }).catch(()=>{if(token===paleoGeneration.current){paleoKey.current='retry';latest.current.onError('古海岸线读取失败，请刷新重试。');}});
 }
 useEffect(()=>{
  if(!container.current)return;
  let map:maplibregl.Map;
  try{map=new maplibregl.Map({container:container.current,center:[47,25],zoom:1.9,minZoom:-0.5,maxZoom:10,pitch:0,pixelRatio:Math.min(2.5,Math.max(2,window.devicePixelRatio||1)),maxPitch:75,transformCameraUpdate:transform=>latest.current.layers.autoView?{pitch:perspectiveForZoom(transform.zoom).pitch}:{},attributionControl:false,canvasContextAttributes:{preserveDrawingBuffer:true,antialias:true},localIdeographFontFamily:'Noto Serif SC, SimSun, serif',style:{version:8,'font-faces':{'Atlas Sans':[{url:'/data/atlas-cjk.ttf','unicode-range':['U+0000-FFFF']}],'Atlas Serif':[{url:'/data/atlas-serif.ttf','unicode-range':['U+0000-FFFF']}]},projection:{type:['interpolate',['linear'],['zoom'],1,'vertical-perspective',1.85,'mercator']},sky:{'sky-color':'#071220','horizon-color':'#385f78','fog-color':'#93a9af','sky-horizon-blend':.65,'horizon-fog-blend':.25,'fog-ground-blend':.8,'atmosphere-blend':['interpolate',['linear'],['zoom'],0,1,2,0]},sources:{},layers:[{id:'sea',type:'background',paint:{'background-color':'#071220'}}]}});}catch(error){latest.current.onError('地图无法初始化：请启用浏览器硬件加速或使用支持 WebGL 的浏览器。');return;}
  mapRef.current=map;
  map.addControl(new maplibregl.AttributionControl({compact:true,customAttribution:'Cliopatria / Seshat · Historical Basemaps · Natural Earth · AWS Terrain Tiles'}),'bottom-left');
  map.on('load',()=>{
   if(!mapRef.current)return;
   map.addSource('land',{type:'geojson',data:'/data/ne_10m_land.geojson',tolerance:0.08,maxzoom:12});
   map.addLayer({id:'land',type:'fill',source:'land',paint:{'fill-color':'#5b665f'}});
   map.addSource('elevation',{type:'raster-dem',tiles:[location.origin+'/data/dem/{z}/{x}/{y}.png'],tileSize:256,maxzoom:5,encoding:'terrarium'});
   map.addSource('shade-dem',{type:'raster-dem',tiles:[location.origin+'/data/dem/{z}/{x}/{y}.png'],tileSize:256,maxzoom:5,encoding:'terrarium'});
   map.addSource('countries',{type:'geojson',data:empty,promoteId:'id',tolerance:0.002,maxzoom:14});
   map.addSource('borders',{type:'geojson',data:empty,tolerance:0.002,maxzoom:14});
   map.addSource('country-labels',{type:'geojson',data:empty});
   map.addSource('viewport-labels',{type:'geojson',data:empty});
   map.addSource('capitals',{type:'geojson',data:empty});
   map.addSource('places',{type:'geojson',data:empty});
   map.addSource('reference-sites',{type:'geojson',data:empty});
   fetch('/data/colonial-reference-sites.geojson',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('sites');return r.json();}).then(collection=>{if(mapRef.current!==map)return;referenceSites.current=collection;update();}).catch(()=>latest.current.onError('殖民据点参考资料读取失败。'));
   map.addSource('events',{type:'geojson',data:empty});
   map.addSource('occupations',{type:'geojson',data:empty});
   map.addSource('provinces',{type:'geojson',data:empty,tolerance:0.002,maxzoom:14});
   map.addSource('province-labels',{type:'geojson',data:empty});
   const currentGeneration=generation.current;
   Promise.all(['/data/provinces.geojson','/data/historical-provinces.geojson'].map(url=>fetch(url,{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error(url);return r.json();}))).then(([modern,historical])=>{if(generation.current!==currentGeneration||mapRef.current!==map)return;modernRegions.current=modern;historicalRegions.current=historical;const worker=new Worker(new URL('./regions.worker.ts',import.meta.url),{type:'module'});regionWorker.current=worker;worker.onmessage=({data})=>{if(generation.current!==currentGeneration||data.id!==regionRequest.current||data.year!==latest.current.year||lastRegionWorld.current!==latest.current.data)return;if(data.collection)applyRegions(data.collection);else if(data.error)latest.current.onError('该年份分区未能生成，请切换年份重试。');};worker.postMessage({type:'init',modern,historical});lastRegionYear.current=null;updateRegions();}).catch(()=>latest.current.onError('分区资料读取失败。'));
   const graticule:FeatureCollection={type:'FeatureCollection',features:[]};
   for(let lng=-180;lng<=180;lng+=30)graticule.features.push({type:'Feature',properties:{},geometry:{type:'LineString',coordinates:Array.from({length:171},(_,i)=>[lng,i-85])}});
   for(let lat=-60;lat<=60;lat+=30)graticule.features.push({type:'Feature',properties:{},geometry:{type:'LineString',coordinates:Array.from({length:361},(_,i)=>[i-180,lat])}});
   map.addSource('graticule',{type:'geojson',data:graticule});
   map.addLayer({id:'grid',type:'line',source:'graticule',paint:{'line-color':'#bac5bb','line-opacity':0.08,'line-width':0.6}});
   map.addLayer({id:'country-fill',type:'fill',source:'countries',layout:{'fill-sort-key':['get','fillOrder']},paint:{'fill-color':['get','color'],'fill-opacity':0.96,'fill-antialias':false,'fill-opacity-transition':{duration:500}}});
   map.addLayer({id:'hillshade',type:'hillshade',source:'shade-dem',paint:{'hillshade-exaggeration':0.27,'hillshade-shadow-color':'#354b3c','hillshade-highlight-color':'#f4efd7','hillshade-accent-color':'#7f8d6e','hillshade-illumination-direction':315}});
   map.addSource('ocean-mask',{type:'geojson',data:'/data/ocean-mask-render.geojson',tolerance:0,maxzoom:12});
   map.addLayer({id:'ocean-mask',type:'fill',source:'ocean-mask',paint:{'fill-color':'#183647','fill-opacity':1,'fill-antialias':false}});
   installOceanRipples(map);
   map.addLayer({id:'coastline',type:'line',source:'land',layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':'#b8cfbc','line-width':['interpolate',['linear'],['zoom'],0,0.35,5,0.65,9,0.95],'line-opacity':0.42}});
   map.addSource('lakes',{type:'geojson',data:'/data/ne_10m_lakes.geojson',tolerance:0.08,maxzoom:12});
   map.addLayer({id:'lakes',type:'fill',source:'lakes',paint:{'fill-color':'#244c5d','fill-opacity':0.9}});
   map.addSource('aral-historical-water',{type:'geojson',data:'/data/aral-historical-water.geojson',tolerance:0.005});
   map.addLayer({id:'aral-historical-water',type:'fill',source:'aral-historical-water',layout:{visibility:'none'},
    paint:{'fill-color':'#244c5d','fill-antialias':false}});
   map.addSource('rivers',{type:'geojson',data:'/data/ne_10m_rivers_lake_centerlines.geojson',tolerance:0.08,maxzoom:12});
   map.addLayer({id:'rivers',type:'line',source:'rivers',minzoom:2.5,filter:['<=',['get','scalerank'],4],layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':'#426f7b','line-width':['interpolate',['linear'],['zoom'],2.5,0.45,6,0.9,10,1.5],'line-opacity':0.6}});
   fetch('/data/paleogeography/index.json').then(r=>{if(!r.ok)throw Error();return r.json();}).then(index=>{if(mapRef.current===map){paleoIndex.current=index;update();}}).catch(()=>{});
   map.addLayer({id:'country-line-casing',type:'line',source:'borders',layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':'#405449','line-width':['interpolate',['linear'],['zoom'],0,0.8,4,1.15,8,1.45],'line-opacity':0.55}},'ocean-mask');
   map.addLayer({id:'country-line',type:'line',source:'borders',layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':'#e2dbc0','line-width':['interpolate',['linear'],['zoom'],0,0.28,4,0.45,8,0.65],'line-opacity':0.8}},'ocean-mask');
   map.addLayer({id:'province-line',type:'line',source:'provinces',minzoom:4.5,layout:{'line-join':'round','line-cap':'round'},paint:{'line-color':'#516a59','line-width':['interpolate',['linear'],['zoom'],4.5,0.3,8,0.7],'line-opacity':['interpolate',['linear'],['zoom'],4.5,0,6,['case',['==',['get','boundaryVisible'],false],0,0.42]]}});
   map.addLayer({id:'province-reference-line',type:'line',source:'provinces',minzoom:4.5,
    filter:['all',['==',['get','country'],'United Kingdom'],['==',['get','geographicReference'],true],['==',['get','boundaryVisible'],false]],
    paint:{'line-color':'#485a50','line-width':['interpolate',['linear'],['zoom'],4.5,0.35,8,0.75],
     'line-opacity':['interpolate',['linear'],['zoom'],4.5,0,6,0.30],'line-dasharray':[2,2]}},'ocean-mask');
   map.addLayer({id:'province-hit',type:'fill',source:'provinces',minzoom:4.7,paint:{'fill-color':'#ffffff','fill-opacity':0}});
   map.addLayer({id:'province-selection',type:'line',source:'provinces',filter:['==',['get','id'],''],paint:{'line-color':'#f6e4ac','line-width':1.5}});
   // Transparent repeating tile: a separate tint beneath it carries the occupier's color.
   const canvas=document.createElement('canvas');canvas.width=16;canvas.height=16;const ctx=canvas.getContext('2d')!;
   ctx.strokeStyle=colorForName('Germany');ctx.lineWidth=4;for(let x=-16;x<=32;x+=16){ctx.beginPath();ctx.moveTo(x,16);ctx.lineTo(x+16,0);ctx.stroke();}
   map.addImage('occupation-hatch',ctx.getImageData(0,0,16,16));
   map.addLayer({id:'occupation-base',type:'fill',source:'occupations',paint:{'fill-color':['get','color'],'fill-opacity':0.12}});
   map.addLayer({id:'occupation-pattern',type:'fill',source:'occupations',paint:{'fill-pattern':['get','pattern'],'fill-opacity':0.85}});
   map.addLayer({id:'occupation-line',type:'line',source:'occupations',paint:{'line-color':['get','color'],'line-width':2,'line-dasharray':[4,2]}});
   map.addSource('selection-borders',{type:'geojson',data:empty,tolerance:0.002,maxzoom:14});
   map.addLayer({id:'selection-outline',type:'line',source:'selection-borders',paint:{'line-color':'#f7e4b0','line-width':1.1,'line-opacity':0.85}},'ocean-mask');
   const text={ 'text-font':['Atlas Serif'],'text-anchor':'center' as const,'text-allow-overlap':false };
   const waterNames: [string,number,number,number][]=[
    ['太平洋',-151,13,0],['北太平洋',154,34,2],['南太平洋',-126,-31,2],
    ['大西洋',-37,3,0],['北大西洋',-36,43,2],['南大西洋',-18,-29,2],
    ['印度洋',79,-23,0],['北冰洋',25,81,0],['南冰洋',67,-58,0],
    ['白令海',-174,58,3],['北海',3,56,3],['波罗的海',20,58,3],
    ['地中海',18,35,3],['加勒比海',-75,15,3],['红海',38.8,20,4],
    ['阿拉伯海',64,14,3],['孟加拉湾',88,13,3],['南海',114,14,3],
    ['珊瑚海',155,-18,3],['塔斯曼海',161,-39,3],
    ['咸海',60.1,45.5,4],['里海',51,41.8,2],['黑海',34,43.2,2],['东海',126,28.6,2],['日本海',135,41,2],
    ['黄海',123.7,35.2,3],['渤海',119.8,39.1,4],['鄂霍次克海',149,54,2],
    ['挪威海',1,68,3],['格陵兰海',-8,76,3],['巴伦支海',37,74,3],
    ['拉布拉多海',-52,57,3],['墨西哥湾',-90,24.5,3],['亚得里亚海',16,43,4],
    ['爱琴海',25,38,4],['波斯湾',51,26.8,4],['爪哇海',112,-5.5,4],
   ];
   const waterLabels:FeatureCollection={type:'FeatureCollection',features:waterNames.map(([name,x,y,zoom])=>({
    type:'Feature',geometry:{type:'Point',coordinates:[x,y]},properties:{name,zoom}
   }))};
   map.addSource('ocean-labels',{type:'geojson',data:waterLabels});
   map.addLayer({id:'ocean-label',type:'symbol',source:'ocean-labels',
    filter:['step',['zoom'],['<=',['get','zoom'],2],2.7,['<=',['get','zoom'],3],3.5,true],
    layout:{...text,'text-field':['get','name'],'text-letter-spacing':0.14,'text-padding':2,'text-ignore-placement':true,'symbol-sort-key':['get','zoom'],
     'text-size':['interpolate',['linear'],['zoom'],0,8,2,12,4,16,6,19]},
    paint:{'text-color':'#a6c8d0','text-halo-color':'#183647','text-halo-width':1.1,
     'text-opacity':['interpolate',['linear'],['zoom'],0,0.86,4.8,0.92,9,0.80]}});
   map.addLayer({id:'country-label',type:'symbol',source:'country-labels',layout:{...text,'symbol-placement':'point','text-rotate':['get','angle'],'text-rotation-alignment':'map','text-pitch-alignment':'map','text-field':['get','name'],'text-allow-overlap':true,'text-ignore-placement':true,'text-padding':0,'text-size':['interpolate',['exponential',2],['zoom'],0,['case',['==',['get','compact'],true],8,['max',1.4,['get','size']]],6,['case',['==',['get','compact'],true],28,['max',16,['*',64,['get','size']]]]]},paint:{'text-color':'#23322e','text-halo-color':'#f5e9cf','text-halo-width':.65,'text-opacity':['interpolate',['linear'],['zoom'],4.7,1,6.3,0]}});
   map.addLayer({id:'country-label-viewport',type:'symbol',source:'viewport-labels',layout:{...text,'text-field':['get','name'],'text-allow-overlap':true,'text-ignore-placement':true,'text-font':['Atlas Serif'],'text-letter-spacing':.3,'text-size':['interpolate',['linear'],['zoom'],0,10,4,22],'text-rotation-alignment':'map','text-pitch-alignment':'map'},paint:{'text-color':'#23322e','text-halo-color':'#f5e9cf','text-halo-width':.8,'text-opacity':['interpolate',['linear'],['zoom'],4.7,1,6.3,0]}});
   map.addLayer({id:'province-label',type:'symbol',source:'province-labels',filter:['!=',['get','suppressLabel'],true],minzoom:4.7,layout:{...text,'text-field':['case',['any',['==',['get','locatorOnly'],true],['has','locatorLabel']],['concat',['get','label'],'（',['coalesce',['get','locatorLabel'],'省治'],'）'],['get','label']],'text-size':['interpolate',['exponential',1.2],['zoom'],4.7,12,8,23],'text-padding':14,'text-letter-spacing':0.04},paint:{'text-color':'#3b5144','text-halo-color':'#eee8d2','text-halo-width':0.6,'text-opacity':['interpolate',['linear'],['zoom'],4.9,0,6.3,0.95]}});
   map.addLayer({id:'place-dot',type:'circle',source:'places',minzoom:3.3,paint:{'circle-radius':3,'circle-color':'#f6e7bd','circle-stroke-color':'#36443a','circle-stroke-width':1.5,'circle-opacity':['interpolate',['linear'],['zoom'],3.3,0,4.5,1]}});
   map.addLayer({id:'place-label',type:'symbol',source:'places',minzoom:3.3,layout:{...text,'text-field':['get','name'],'text-size':13,'text-offset':[0,1.3],'text-anchor':'top'},paint:{'text-color':'#253d35','text-halo-color':'#f7edd3','text-halo-width':0.9,'text-opacity':['interpolate',['linear'],['zoom'],3.3,0,4.8,1]}});
   const symbol=document.createElement('canvas');
   symbol.width=32;symbol.height=32;
   const brush=symbol.getContext('2d')!;
   brush.beginPath();
   for(let i=0;i<10;i++){
    const angle=i*Math.PI/5-Math.PI/2,radius=i%2?6:14;
    brush.lineTo(16+Math.cos(angle)*radius,16+Math.sin(angle)*radius);
   }
   brush.closePath();brush.fillStyle='#ffdf94';brush.fill();
   brush.strokeStyle='#233c40';brush.lineWidth=3;brush.stroke();
   map.addImage('capital-star',brush.getImageData(0,0,32,32),{pixelRatio:2});
   map.addLayer({id:'capital-star',type:'symbol',source:'capitals',
    layout:{'icon-image':'capital-star','icon-size':['interpolate',['linear'],['zoom'],0,0.5,3,0.8,7,1.15],
     'icon-allow-overlap':true,'icon-ignore-placement':true}});
   map.addLayer({id:'capital-label',type:'symbol',source:'capitals',minzoom:2.7,
    layout:{...text,'text-field':['get','label'],'text-size':['interpolate',['linear'],['zoom'],2.7,11,7,15],
     'text-anchor':'top','text-offset':[0,0.85]},
    paint:{'text-color':'#fff0bf','text-halo-color':'#203436','text-halo-width':1.2}});
   map.addLayer({id:'reference-site-dot',type:'circle',source:'reference-sites',minzoom:3.4,paint:{'circle-radius':['interpolate',['linear'],['zoom'],3.4,2,6,4],'circle-color':['get','color'],'circle-stroke-color':'#f7e6b7','circle-stroke-width':1.2,'circle-opacity':0.9}});
   map.addLayer({id:'reference-site-label',type:'symbol',source:'reference-sites',minzoom:5.5,layout:{...text,'text-field':['get','label'],'text-size':11,'text-offset':[0,1.2],'text-anchor':'top','text-padding':12},paint:{'text-color':'#263b34','text-halo-color':'#f7edd3','text-halo-width':1}});
   map.addLayer({id:'event-dot',type:'circle',source:'events',paint:{'circle-radius':7,'circle-color':'#d9b16a','circle-stroke-color':'#fff2cf','circle-stroke-width':2}});
   map.addLayer({id:'event-label',type:'symbol',source:'events',layout:{...text,'text-field':['get','name'],'text-size':12,'text-offset':[0,1.5],'text-anchor':'top'},paint:{'text-color':'#fff1bf','text-halo-color':'#354a3c','text-halo-width':1}});
   ready.current=true;update();
   fetch('/api/map-capabilities').then(r=>r.ok?r.json():null).then(capabilities=>{
    if(!capabilities?.terrainProxy||mapRef.current!==map)return;
    for(const id of ['elevation-hd','shade-hd'])map.addSource(id,{type:'raster-dem',tiles:[location.origin+'/terrain/{z}/{x}/{y}.png'],tileSize:256,maxzoom:12,encoding:'terrarium'});
    map.addLayer({id:'hillshade-hd',type:'hillshade',source:'shade-hd',paint:{'hillshade-exaggeration':0.27,'hillshade-shadow-color':'#354b3c','hillshade-highlight-color':'#f4efd7','hillshade-accent-color':'#7f8d6e','hillshade-illumination-direction':315}},'ocean-mask');
    hdReady.current=true;lastTerrain.current=null;update();
   }).catch(()=>{});
   const flyToPolity=(name:string)=>{
    const territories=(latest.current.data?.features||[]).filter(f=>
     f.geometry&&!f.properties?.controlArea&&(f.properties?.SUBJECTO?.trim()||f.properties?.NAME)===name);
    const bounds=territoryBounds(territories.map(f=>f.geometry));
    if(!bounds)return;
    const canvas=map.getContainer();
    const padding=Math.min(72,Math.round(Math.min(canvas.clientWidth,canvas.clientHeight)*0.12));
    map.fitBounds(bounds,{padding,bearing:0,pitch:0,maxZoom:8,duration:1400});
   };
   latest.current.onReady({flyToPolity,fly:(position,zoom=4.4)=>map.flyTo({center:position,zoom,duration:1500,essential:true}),zoom:delta=>map.easeTo({zoom:map.getZoom()+delta,duration:600}),reset:()=>map.flyTo({center:[47,25],zoom:1.9,pitch:0,bearing:0,duration:1400}),tilt:()=>latest.current.layers.autoView?map.flyTo({zoom:map.getZoom()>5?2.8:6.7,duration:1800}):map.easeTo({pitch:map.getPitch()>20?0:55,zoom:Math.max(4,map.getZoom()),duration:1200}),globe:()=>map.flyTo({zoom:0.95,pitch:0,duration:1600}),screenshot:()=>{map.once('render',()=>{const a=document.createElement('a');a.href=map.getCanvas().toDataURL('image/png');a.download=`观澜-${latest.current.year}.png`;a.click();});map.triggerRepaint();}});
   latest.current.onZoom(map.getZoom());
  });
  map.on('zoomend',()=>updateRegions());
  map.on('idle',refreshViewportLabels);map.on('moveend',refreshViewportLabels);
  map.on('zoom',()=>{latest.current.onZoom(Math.round(map.getZoom()*20)/20);if(viewFrame.current===null)viewFrame.current=requestAnimationFrame(()=>{viewFrame.current=null;syncPerspective();});});
  const selectCountryAt=(e:maplibregl.MapMouseEvent)=>{
   const p=latest.current;
   const label=map.getZoom()<=4.7&&p.layers.labels
    ?map.queryRenderedFeatures(e.point,{layers:['country-label','country-label-viewport']})[0]:undefined;
   const labeled=label&&p.data?.features.find(f=>!f.properties?.controlArea&&f.properties?.NAME===label.properties.owner);
   if(labeled){
    p.onSelect({kind:'country',feature:labeled as AtlasFeature,name:labeled.properties!.NAME,position:e.lngLat.toArray()});
    return;
   }
   const country=map.queryRenderedFeatures(e.point,{layers:['country-fill']})[0];
   if(!country)return;
   const original=p.data?.features.find(f=>f.properties?.NAME===country.properties.NAME);
   p.onSelect({kind:'country',feature:(original||country) as AtlasFeature,name:country.properties.owner,position:e.lngLat.toArray()});
  };
  map.on('contextmenu',e=>{
   if(!ready.current||e.originalEvent.button!==2)return;
   e.originalEvent.preventDefault();
   selectCountryAt(e);
  });
  map.on('click',e=>{
   if(!ready.current)return;
   const p=latest.current;
   const check=(id:string)=>map.queryRenderedFeatures(e.point,{layers:[id]})[0];
   const site=check('reference-site-dot');if(site){p.onSelect({kind:'site',id:site.properties.id,name:site.properties.label,feature:siteFeatures.current.get(site.properties.id),position:e.lngLat.toArray()});return;}
   const occupation=p.layers.occupation&&(!p.layers.provinces||map.getZoom()<=4.7)?check('occupation-base'):null;
   if(occupation){const original=p.data?.features.find(f=>f.properties?.controlArea&&(f.properties.controlId||f.properties.id)===occupation.properties.id);p.onSelect({kind:'occupation',id:occupation.properties.id,name:occupation.properties.name,feature:original as AtlasFeature|undefined,position:e.lngLat.toArray()});return;}
   const capital=(!p.layers.provinces||map.getZoom()<=4.7)?check('capital-star'):null;
   if(capital){
    const owner=capital.properties.owner;
    const feature=p.data?.features.find(f=>!f.properties?.controlArea&&(f.properties?.SUBJECTO?.trim()||f.properties?.NAME)===owner);
    if(feature){p.onSelect({kind:'country',feature:feature as AtlasFeature,name:owner,position:e.lngLat.toArray()});return;}
   }
   if(p.layers.provinces&&map.getZoom()>4.7){
    const locator=map.queryRenderedFeatures(e.point,{layers:['province-label'],filter:['any',['==',['get','locatorOnly'],true],['has','labelPosition']]})[0];
    const feature=locator&&provinceData.current.get(locator.properties.id);
    if(feature){
     const position=feature.geometry.type==='Point'?feature.geometry.coordinates:feature.properties.labelPosition;
     p.onSelect({kind:'province',feature,name:feature.properties.label,position:position as [number,number]});
     return;
    }
   }
   const place=check('place-dot');if(place){p.onSelect({kind:'place',id:place.properties.id,name:place.properties.name,position:e.lngLat.toArray()});return;}
   const province=p.layers.provinces?check('province-hit'):null;
   if(province&&map.getZoom()>4.7){p.onSelect({kind:'province',feature:provinceData.current.get(province.properties.id)||province as AtlasFeature,name:province.properties.label,position:e.lngLat.toArray()});return;}
   selectCountryAt(e);
  });
  const capitalPopup=new maplibregl.Popup({closeButton:false,closeOnClick:false,offset:10,className:'capital-tooltip'});
  map.on('mousemove','capital-star',e=>{
   const p=e.features?.[0]?.properties;
   if(!p)return;
   capitalPopup.setLngLat(e.lngLat).setText(p.ownerLabel+' · '+p.label+(p.federationLabel?'（地图采用'+p.federationLabel+'轮廓）':p.reference?'（时期参考）':''));
   if(!capitalPopup.isOpen())capitalPopup.addTo(map);
  });
  map.on('mouseleave','capital-star',()=>capitalPopup.remove());
  map.on('mousemove',e=>{if(ready.current)map.getCanvas().style.cursor=map.queryRenderedFeatures(e.point,{layers:['country-fill','capital-star','place-dot','reference-site-dot','occupation-base']}).length?'pointer':'grab';});
  let reported=false;map.on('error',e=>{console.warn('Map resource unavailable',e.error?.message||'');if(!reported){reported=true;latest.current.onError(`部分地图素材加载失败，可刷新重试。${e.error?.message?.includes('WebGL')?' 请检查浏览器 WebGL 支持。':''}`);}});
  return()=>{if(regionTimer.current)clearTimeout(regionTimer.current);regionWorker.current?.terminate();regionWorker.current=null;generation.current++;if(viewFrame.current!==null)cancelAnimationFrame(viewFrame.current);viewFrame.current=null;ready.current=false;lastData.current=null;lastCapitalFrame.current=null;lastSelectionFrame.current=null;lastTerrain.current=null;hdReady.current=false;capitalPopup.remove();map.remove();mapRef.current=null;};
 },[]);
 useEffect(()=>{update();},[props.data,props.year,props.layers,props.selected,props.regionSelection]);
 return <div className="map-canvas" ref={container} aria-label="可拖动缩放的历史世界地图"/>;
}
export function ownerAt(position:[number,number],data:FeatureCollection|null){
 const features=data?.features||[];
 const controller=features.find(f=>f.properties?.controlArea&&f.properties.controller&&pointInGeometry(position,f.geometry));
 if(controller)return controller.properties?.controller;
 const polity=features.find(f=>!f.properties?.controlArea&&f.properties?.NAME&&pointInGeometry(position,f.geometry));
 return polity?.properties?.SUBJECTO?.trim()||polity?.properties?.NAME;
}
