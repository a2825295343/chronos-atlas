import {areaKm2,featureCenter,pointInGeometry,colorForName} from './history.mjs';
import {politicalBorders} from './cartography.mjs';
import {polygonRenderParts} from './polygon-render.mjs';
import {mapName} from './map-names.mjs';
const merc=lat=>Math.log(Math.tan(Math.PI/4+Math.max(-84,Math.min(84,lat))*Math.PI/360))*180/Math.PI;
const unmerc=y=>(2*Math.atan(Math.exp(y*Math.PI/180))-Math.PI/2)*180/Math.PI;
/** Interior paths, split into individually placed glyphs so collision boxes cannot
 * suppress an entire country. Text stretches geographically, rather than hiding
 * when a huge offscreen point-label bounding box collides with a nearby state. */
export function countryGlyphs(features,localize=name=>name){
 const labels=[];
 for(const f of features){
  const p=f.properties,name=mapName(p,localize),chars=Array.from(name),total=p.atlasArea??areaKm2(f.geometry);
  if(!chars.length)continue;
  const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.type==='MultiPolygon'?f.geometry.coordinates:[];
  const parts=polygons.map(coordinates=>({type:'Polygon',coordinates})).map(g=>({g,area:areaKm2(g)})).sort((a,b)=>b.area-a.area);
  for(const [partIndex,part] of parts.entries()){
   if(partIndex>0&&(part.area<Math.max(18000,parts[0].area*.13)||partIndex>3))continue;
   let center=featureCenter(part.g),path=partIndex===0?p.labelPath?.coordinates:null;
   if(path&&!pointInGeometry(path[Math.floor(path.length/2)],part.g))path=null;
   if(!path){
    if(!pointInGeometry(center,part.g)){
     const ring=part.g.coordinates[0];let best=ring[0];
     for(const v of ring.filter((_,i)=>i%Math.max(1,Math.floor(ring.length/32))===0))for(const t of [.15,.4,.7]){const q=[v[0]*(1-t)+center[0]*t,v[1]*(1-t)+center[1]*t];if(pointInGeometry(q,part.g)){best=q;break;}}
     center=best;
    }
    // Find the longest in-country chord, including diagonal directions.
    let best=[center,center],length=0;
    for(const slope of [0,.25,-.25,.55,-.55,1,-1]){
     const a=[...center],b=[...center],step=Math.max(.025,Math.sqrt(part.area)/6371*180/Math.PI/70),dy=step*slope;
     for(const sign of [-1,1])for(let i=1;i<=160;i++){
      const q=[center[0]+step*i*sign,unmerc(merc(center[1])+dy*i*sign)];
      if(!pointInGeometry(q,part.g))break;
      if(sign<0){a[0]=q[0];a[1]=q[1];}else{b[0]=q[0];b[1]=q[1];}
     }
     const span=Math.hypot(b[0]-a[0],merc(b[1])-merc(a[1]));if(span>length){length=span;best=[a,b];}
    }
    path=best;
   }
   let a=[...path[0]],b=[...path.at(-1)];if(a[0]>b[0])[a,b]=[b,a];
   const dx=b[0]-a[0],dy=merc(b[1])-merc(a[1]),span=Math.hypot(dx,dy),unit=Math.max(.25,Math.min(8,span*512/360/(chars.length*1.8)));
   if(part.area<80000){
    const point=path[Math.floor(path.length/2)];
    labels.push({type:'Feature',geometry:{type:'Point',coordinates:point},properties:{name,fullName:name,owner:p.NAME,size:1.2,compact:true,area:total,angle:Math.atan2(-dy,dx)*180/Math.PI,part:partIndex}});
    continue;
   }
   const bend=span*.045;
   for(let i=0;i<chars.length;i++){
    const t=chars.length===1?.5:.12+.76*(i+.5)/chars.length;
    let x=a[0]+dx*t,y=merc(a[1])+dy*t+Math.sin(t*Math.PI)*bend;
    if(!pointInGeometry([x,unmerc(y)],part.g))y=merc(a[1])+dy*t;
    const tangent=dy+Math.cos(t*Math.PI)*bend*Math.PI;
    labels.push({type:'Feature',geometry:{type:'Point',coordinates:[x,unmerc(y)]},properties:{name:chars[i],fullName:name,owner:p.NAME,size:unit,area:total,angle:Math.atan2(-tangent,dx)*180/Math.PI,part:partIndex}});
   }
  }
 }
 return {type:'FeatureCollection',features:labels};
}
export function buildAtlasFrame(data,localize=name=>name){
 const features=data.features.filter(f=>f.geometry&&f.properties?.NAME?.trim()).map((f,id)=>{
  const p=f.properties,owner=p.SUBJECTO?.trim()||p.NAME;
  return {...f,id,properties:{...p,controlId:p.controlArea?p.id:undefined,id,owner,label:mapName(p,localize),ownerLabel:p.displayName||localize(owner),color:p.controlArea?colorForName(p.sovereignName||owner):p.thematicColor||colorForName(owner),atlasArea:areaKm2(f.geometry),atlasCenter:featureCenter(f.geometry)}};
 });
 const collection={type:'FeatureCollection',features};
 const fills=polygonRenderParts(collection,p=>({id:p.id,NAME:p.NAME,owner:p.owner,label:p.label,color:p.color}));
 return {...collection,atlas:{fills,borders:politicalBorders(collection),labels:countryGlyphs(features,localize)}};
}
