import polygonClipping from 'polygon-clipping';
import {pointInGeometry} from './history.mjs';

/** Build an outline for the parts actually visible through the paint order.
 * Original features still drive territories, selection and archive data.
 */
export function visiblePoliticalFootprints(collection){
 const parts=[];
 for(const f of collection.features){
  if(f.properties?.controlArea||!f.geometry)continue;
  const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.type==='MultiPolygon'?f.geometry.coordinates:[];
  for(const polygon of polygons){
   const bounds=[Infinity,Infinity,-Infinity,-Infinity];
   for(const [x,y] of polygon[0]){
    bounds[0]=Math.min(bounds[0],x);bounds[1]=Math.min(bounds[1],y);
    bounds[2]=Math.max(bounds[2],x);bounds[3]=Math.max(bounds[3],y);
   }
   parts.push({f,polygon,bounds,order:parts.length,covers:[],weight:polygon.reduce((n,ring)=>n+ring.length,0)});
  }
 }
 const sorted=[...parts].sort((a,b)=>a.bounds[0]-b.bounds[0]);
 for(let i=0;i<sorted.length;i++){
  const a=sorted[i];
  for(let j=i+1;j<sorted.length;j++){
   const b=sorted[j];
   if(b.bounds[0]>=a.bounds[2])break;
   if(a.f===b.f||a.bounds[1]>=b.bounds[3]||b.bounds[1]>=a.bounds[3])continue;
   const [below,above]=a.order<b.order?[a,b]:[b,a];
   if(below.f.properties?.boundaryGeometry&&above.f.properties?.boundaryGeometry)continue;
   // An enclosed polygon adds its own outline. It cannot hide the lower
   // outer stroke unless it reaches that stroke.
   const [w,s,e,n]=above.bounds;
   const ring=below.polygon[0],stride=Math.max(1,Math.floor(ring.length/20));
   let hidesOutline=false;
   for(let k=0;k<ring.length;k+=stride){
    const [x,y]=ring[k];
    if(x<=w||x>=e||y<=s||y>=n)continue;
    if(pointInGeometry(ring[k],{type:'Polygon',coordinates:above.polygon})){
     hidesOutline=true;
     break;
    }
   }
   if(hidesOutline)below.covers.push(above);
  }
 }
 const updated=new Map();
 let clipBudget=9000;
 for(const part of parts){
  const {f,polygon,covers}=part;
  let coordinates=[polygon];
  const cost=part.weight+covers.reduce((total,cover)=>total+cover.weight,0);
  if(covers.length&&cost<=clipBudget){
   clipBudget-=cost;
   try{
    coordinates=polygonClipping.difference(polygon,...covers.map(cover=>cover.polygon));
    if(!updated.has(f))updated.set(f,new Map());
    updated.get(f).set(polygon,coordinates);
   }catch{/* Keep this footprint when a source ring cannot be clipped. */}
  }
 }
 const features=collection.features.flatMap(f=>{
  const replacements=updated.get(f);
  if(!replacements)return [f];
  const polygons=f.geometry.type==='Polygon'?[f.geometry.coordinates]:f.geometry.coordinates;
  const coordinates=polygons.flatMap(p=>replacements.get(p)??[p]);
  return coordinates.length?[{...f,geometry:{type:'MultiPolygon',coordinates}}]:[];
 });
 return {...collection,features};
}


// Use the same quantization for border topology and for stitching drawing paths.
const SCALE=1e5;
const key=([x,y])=>x+','+y;
const quantize=p=>[Math.round(p[0]*SCALE),Math.round(p[1]*SCALE)];
let geometryEdges=new WeakMap();
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
   const first=active.values().next().value;
   let sameSide=true,sameOwner=true;
   for(const edge of active){
    if(edge.owner!==first.owner)sameOwner=false;
    if(edge.forward!==first.forward)sameSide=false;
   }
   if(!sameOwner||sameSide)segments.push([previous,event.point]);
  }
  for(const edge of event.ends)active.delete(edge);
  for(const edge of event.starts)active.add(edge);
  previous=event.point;
 }
 return segments;
}

function edgesFor(geometry){
 let edges=geometryEdges.get(geometry);
 if(edges)return edges;
 edges=[];
 const polygons=geometry.type==='Polygon'?[geometry.coordinates]:geometry.type==='MultiPolygon'?geometry.coordinates:[];
 for(const polygon of polygons)for(const [ringIndex,points] of polygon.entries()){
  if(points.length<2)continue;
  const ring=points.map(quantize);
  let signedArea=0;
  for(let i=1;i<ring.length;i++)signedArea+=ring[i-1][0]*ring[i][1]-ring[i][0]*ring[i-1][1];
  const reverse=(signedArea<0)===(ringIndex===0);
  for(let i=1;i<ring.length;i++){
   const previous=ring[i-1],end=ring[i];
   if(atDateLine(previous)&&atDateLine(end))continue;
   const dx=end[0]-previous[0],dy=end[1]-previous[1];
   if(!dx&&!dy)continue;
   const unit=gcd(Math.abs(dx),Math.abs(dy))*((dx||dy)<0?-1:1);
   const x=dx/unit,y=dy/unit;
   const id=[x,y,x*previous[1]-y*previous[0]].join(',');
   const [start,stop]=unit>0?[previous,end]:[end,previous];
   edges.push({id,start,end:stop,vertical:!x,forward:(unit>0)!==reverse});
  }
 }
 return edges;
}

export function politicalBorders(data){
 const collinear=new Map(),nextGeometryEdges=new WeakMap();
 for(const f of data.features){
  const owner=f.properties?.SUBJECTO?.trim()||f.properties?.NAME?.trim();
  if(!owner||!f.geometry||f.properties?.controlArea)continue;
  const edges=edgesFor(f.geometry);
  nextGeometryEdges.set(f.geometry,edges);
  for(const edge of edges){
   if(!collinear.has(edge.id))collinear.set(edge.id,[]);
   collinear.get(edge.id).push({...edge,owner});
  }
 }

 geometryEdges=nextGeometryEdges;

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
