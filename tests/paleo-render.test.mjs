import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {GeoJSONVT} from '@maplibre/geojson-vt';
import {classifyRings} from '@maplibre/maplibre-gl-style-spec';
import earcut,{flatten} from 'earcut';
import {pointInGeometry} from '../src/history.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../public/data/'+p,import.meta.url)));
const probes=[['不列颠',[-2,54]],['苏格兰',[-4,57]],['爱尔兰',[-7,53]],['冰岛',[-19,65]],['爪哇',[110,-7]],['婆罗洲',[114,.5]],['菲律宾',[121,16]],['澳大利亚',[134,-25]],['悉尼',[151,-33]],['塔斯马尼亚',[147,-42]],['新西兰北岛',[175.5,-39.5]],['新西兰南岛',[170,-44]],['古巴',[-79.5,22]],['牙买加',[-77.3,18.2]],['波多黎各',[-66.5,18.2]]];
const cross=(a,b,p)=>(b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0]);
function renderer(collection){
 const index=new GeoJSONVT(collection,{maxZoom:12,extent:8192,tolerance:.03*16,buffer:128*16}),meshes=new Map();
 return(point,z)=>{
  const n=2**z,x=(point[0]+180)/360*n,y=(1-Math.asinh(Math.tan(point[1]*Math.PI/180))/Math.PI)/2*n,tx=Math.floor(x),ty=Math.floor(y),p=[(x-tx)*8192,(y-ty)*8192],key=[z,tx,ty].join('/');
  if(!meshes.has(key)){
   const triangles=[];
   for(const feature of index.getTile(z,tx,ty)?.features||[])for(const poly of classifyRings(feature.geometry.map(r=>r.map(([x,y])=>({x,y}))),500)){
    const rings=poly.map(r=>r.map(p=>[p.x,p.y])),flat=flatten(rings),indices=earcut(flat.vertices,flat.holes,2);
    for(let i=0;i<indices.length;i+=3)triangles.push(indices.slice(i,i+3).map(j=>flat.vertices.slice(j*2,j*2+2)));
   }
   meshes.set(key,triangles);
  }
  return meshes.get(key).some(([a,b,c])=>{const s=[cross(a,b,p),cross(b,c,p),cross(c,a,p)];return s.every(v=>v>=-1e-8)||s.every(v=>v<=1e-8);});
 };
}
for(const key of ['m10','m50','m120','p5','modern'])test(`ocean triangles preserve islands and Mexico at low and high zoom: ${key}`,()=>{
 const raw=read(key==='modern'?'ocean-mask-hd.geojson':`paleogeography/ocean-${key}.geojson`),mesh=read(key==='modern'?'ocean-mask-render.geojson':`paleogeography/ocean-render-${key}.geojson`),covers=renderer(mesh);
 assert.ok(mesh.features.every(f=>f.geometry.type==='Polygon'&&f.geometry.coordinates.length===1));
 for(const z of [0,1,2,3,4,5,6]){
  for(const [name,p]of probes){assert.ok(!raw.features.some(f=>pointInGeometry(p,f.geometry)),name+' is in source land');assert.equal(covers(p,z),false,`${name} zoom ${z} must not be painted as ocean`);}
  // A horizontal strip was incorrectly triangulated across southern Mexico.
  for(const lat of [17,17.5,18,18.5,19])for(const lon of [-102,-100,-98,-96,-94,-92,-90]){
   const p=[lon,lat],expected=raw.features.some(f=>pointInGeometry(p,f.geometry));
   // At zoom 0 one integer tile unit spans several kilometres. Exclude
   // coast-adjacent samples; the reported stripe crossed the inland core.
   if([[-.1,0],[.1,0],[0,-.1],[0,.1]].some(([dx,dy])=>raw.features.some(f=>pointInGeometry([lon+dx,lat+dy],f.geometry))!==expected))continue;
   assert.equal(covers(p,z),expected,`Mexico ${p} zoom ${z}`);
  }
  for(const p of [[-140,0],[-30,30],[160,-15]])assert.equal(covers(p,z),true,`deep ocean ${p} zoom ${z}`);
 }
});
test('all coastline slices have independently drawable ocean masks',()=>{
 const index=read('paleogeography/index.json'),report=read('ocean-render-review.json');
 assert.equal(report.sources.length,index.levels.length+1);
 for(const row of report.sources){assert.equal(row.holes,0);assert.ok(Math.abs(row.areaDifferenceDegrees2)<1e-6);assert.ok(row.features>0);}
});
