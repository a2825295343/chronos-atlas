// Use the same quantization for border topology and for stitching drawing paths.
const SCALE=1e5;
const key=([x,y])=>x+','+y;
const quantize=p=>[Math.round(p[0]*SCALE),Math.round(p[1]*SCALE)];
const atDateLine=p=>Math.abs(Math.abs(p[0])-180*SCALE)<=1;

function gcd(a,b){
 while(b){const remainder=a%b;a=b;b=remainder;}
 return a;
}

// Split collinear overlaps at every existing vertex. Different source rings
// can describe the same edge with different numbers of intermediate points.
function visibleSegments(edges){
 if(edges.length===1)return [[edges[0].start,edges[0].end]];
 const events=new Map();
 for(const edge of edges){
  for(const [point,side] of [[edge.start,'starts'],[edge.end,'ends']]){
   const t=edge.vertical?point[1]:point[0];
   if(!events.has(t))events.set(t,{point,starts:[],ends:[]});
   events.get(t)[side].push(edge);
  }
 }
 const active=new Set(),segments=[];
 let previous;
 for(const [,event] of [...events].sort(([a],[b])=>a-b)){
  if(previous&&active.size){
   const owners=new Set([...active].map(e=>e.owner));
   if(active.size===1||owners.size>1)segments.push([previous,event.point]);
  }
  for(const edge of event.ends)active.delete(edge);
  for(const edge of event.starts)active.add(edge);
  previous=event.point;
 }
 return segments;
}

export function politicalBorders(data){
 const collinear=new Map();
 for(const f of data.features){
  const owner=f.properties?.SUBJECTO?.trim()||f.properties?.NAME?.trim();
  if(!owner)continue;
  const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.type==='MultiPolygon'?f.geometry.coordinates:[];
  for(const polygon of polygons)for(const points of polygon){
   let start=quantize(points[0]);
   for(const point of points.slice(1)){
    const end=quantize(point),previous=start;
    start=end;
    if(atDateLine(previous)&&atDateLine(end))continue;
    const dx=end[0]-previous[0],dy=end[1]-previous[1];
    if(!dx&&!dy)continue;
    const unit=gcd(Math.abs(dx),Math.abs(dy))*((dx||dy)<0?-1:1);
    const x=dx/unit,y=dy/unit;
    const id=[x,y,x*previous[1]-y*previous[0]].join(',');
    const ordered=unit>0?[previous,end]:[end,previous];
    if(!collinear.has(id))collinear.set(id,[]);
    collinear.get(id).push({owner,start:ordered[0],end:ordered[1],vertical:!x});
   }
  }
 }

 // Connect the visible edges into continuous strokes, preferring the
 // straightest continuation at a junction.
 const vertices=new Map(),segments=[];
 for(const group of collinear.values())for(const [a,b] of visibleSegments(group)){
  const edge={ends:[key(a),key(b)],used:false};
  for(const [id,point] of [[edge.ends[0],a],[edge.ends[1],b]]){
   if(!vertices.has(id))vertices.set(id,{point,edges:[]});
   vertices.get(id).edges.push(edge);
  }
  segments.push(edge);
 }
 const lines=[];
 function trace(id,edge){
  const line=[vertices.get(id).point];
  while(edge&&!edge.used){
   edge.used=true;
   const previous=vertices.get(id).point;
   id=edge.ends[0]===id?edge.ends[1]:edge.ends[0];
   const next=vertices.get(id);
   line.push(next.point);
   let best, bestScore=-Infinity;
   const [x,y]=next.point;
   for(const candidate of next.edges){
    if(candidate.used)continue;
    const [u,v]=vertices.get(candidate.ends[0]===id?candidate.ends[1]:candidate.ends[0]).point;
    const score=((x-previous[0])*(u-x)+(y-previous[1])*(v-y))/Math.hypot(u-x,v-y);
    if(score>bestScore){best=candidate;bestScore=score;}
   }
   edge=best;
  }
  lines.push(line.map(([x,y])=>[x/SCALE,y/SCALE]));
 }
 for(const [id,node] of vertices)if(node.edges.length===1){
  for(const edge of node.edges)if(!edge.used)trace(id,edge);
 }
 for(const edge of segments)if(!edge.used)trace(edge.ends[0],edge);
 return {type:'FeatureCollection',features:[{type:'Feature',properties:{},geometry:{type:'MultiLineString',coordinates:lines}}]};
}
