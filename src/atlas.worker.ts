import type {FeatureCollection} from 'geojson';
import {activePolities} from './temporal.mjs';
import {buildAtlasFrame} from './atlas-render.mjs';
import {localName} from './data';
import {paleogeographyAt} from './paleogeography.mjs';
const shards=new Map<string,Promise<FeatureCollection>>(),frames=new Map<string,FeatureCollection>();
let latest=0,lastKey='';
let paleoIndex:Promise<any>|undefined;
async function load(path:string){
 let pending=shards.get(path);
 if(!pending){pending=fetch('/data/'+path,{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error(path);return r.json();}).catch(e=>{shards.delete(path);throw e;});shards.set(path,pending);if(shards.size>4)shards.delete(shards.keys().next().value!);}
 return pending;
}
self.onmessage=async({data:request})=>{
 const {id,path,year,primary}=request;latest=id;
 try{
  const shard=await load(path);if(latest!==id)return;
  let paleo:FeatureCollection={type:'FeatureCollection',features:[]},paleoSlice='modern';
  if(year<-4000){
   paleoIndex??=fetch('/data/paleogeography/index.json').then(r=>{if(!r.ok)throw Error('古地理索引');return r.json();}).catch(e=>{paleoIndex=undefined;throw e;});
   const slice=paleogeographyAt(await paleoIndex,year);
   if(slice){paleoSlice=slice.key;const zones=await load(`paleogeography/cultures-${slice.key}.geojson`);paleo={...zones,features:zones.features.filter(f=>f.properties!.validFrom<=year&&year<=f.properties!.validTo)};}
   if(latest!==id)return;
  }
  const active=shard.features.filter(f=>!primary||f.properties?.validFrom<=year&&year<=f.properties?.validTo);
  const identityEra=year<1801?0:year<1881?1:year<1922?2:year<1949?3:year<1974?4:5;
  const key=path+'|'+identityEra+'|'+paleoSlice+'|'+paleo.features.map(f=>f.properties?.sourceRecord).join(',')+'|'+active.map(f=>f.properties?.sourceRecord+':'+f.properties?.NAME+':'+f.properties?.validFrom+':'+f.properties?.validTo).join(',');
  if(key===lastKey){self.postMessage({id,unchanged:true,year:request.displayYear??year,primary});return;}
  let frame=frames.get(key);
  if(!frame){
   const base=primary?activePolities(shard,year):{...shard,features:shard.features.map(f=>({...f,properties:{...f.properties,SUBJECTO:f.properties?.NAME}}))};
   const collection={...base,features:[...base.features,...paleo.features]};
   frame=buildAtlasFrame(collection,localName);frames.set(key,frame);if(frames.size>3)frames.delete(frames.keys().next().value!);
  }
  if(latest===id){lastKey=key;self.postMessage({id,collection:frame,year:request.displayYear??year,primary});}
 }catch(error){if(latest===id)self.postMessage({id,error:String(error)});}
};
