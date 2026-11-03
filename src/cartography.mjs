// Shared borders are drawn once. Subregions of the same sovereign do not get a
// second, equally heavy national border. Source coordinates remain unchanged.
export function politicalBorders(data){
 const key=p=>`${Math.round(p[0]*1e5)},${Math.round(p[1]*1e5)}`;
 const atDateLine=p=>Math.abs(Math.abs(p[0])-180)<1e-5;
 const edges=new Map();
 const rings=[];
 for(const f of data.features){
  const owner=f.properties?.SUBJECTO?.trim()||f.properties?.NAME?.trim();if(!owner)continue;
  const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.type==='MultiPolygon'?f.geometry.coordinates:[];
  for(const polygon of polygons)for(const points of polygon){
   rings.push({owner,points});
   for(let i=1;i<points.length;i++){const a=key(points[i-1]),b=key(points[i]),id=a<b?a+'|'+b:b+'|'+a,old=edges.get(id);if(old&&old.owner===owner)old.internal=true;else if(!old)edges.set(id,{owner,internal:false});}
  }
 }
 const drawn=new Set(),lines=[];
 for(const {points} of rings){
  let run=[];
  for(let i=1;i<points.length;i++){
   const a=key(points[i-1]),b=key(points[i]),id=a<b?a+'|'+b:b+'|'+a;
   if(!(atDateLine(points[i-1])&&atDateLine(points[i]))&&!edges.get(id)?.internal&&!drawn.has(id)){
    if(!run.length)run.push(points[i-1]);run.push(points[i]);drawn.add(id);
   }else if(run.length>1){lines.push(run);run=[];}
  }
  if(run.length>1)lines.push(run);
 }
 return {type:'FeatureCollection',features:[{type:'Feature',properties:{},geometry:{type:'MultiLineString',coordinates:lines}}]};
}

