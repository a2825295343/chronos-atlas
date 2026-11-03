/** Explicit offline palette planning; never run during timeline playback.
 * Conservative component bounding boxes produce an adjacency graph across all
 * recorded periods, avoiding the old per-year greedy recoloring cascade.
 */
import fs from 'node:fs';
import {colorIdentity} from '../src/color-identity.mjs';
import {POLITY_PALETTE,colorDistance} from '../src/colors.mjs';
const read=path=>JSON.parse(fs.readFileSync(new URL('../'+path,import.meta.url),'utf8'));
const graph=new Map();
const node=key=>{if(!graph.has(key))graph.set(key,new Map());return graph.get(key);};
const overlap=(a,b)=>!(a[2]<b[0]-.18||a[0]>b[2]+.18||a[3]<b[1]-.18||a[1]>b[3]+.18);
function bounds(geometry){
 const polygons=geometry.type==='Polygon'?[geometry.coordinates]:geometry.type==='MultiPolygon'?geometry.coordinates:[];
 return polygons.map(p=>{let w=180,s=90,e=-180,n=-90;for(const [x,y] of p[0]){w=Math.min(w,x);s=Math.min(s,y);e=Math.max(e,x);n=Math.max(n,y);}return [w,s,e,n];}).sort((a,b)=>(b[2]-b[0])*(b[3]-b[1])-(a[2]-a[0])*(a[3]-a[1])).filter((b,i)=>i===0||(b[2]-b[0])*(b[3]-b[1])>.04).slice(0,12);
}
function add(collection,from,to){
 const rows=collection.features.filter(f=>f.properties?.NAME).map(f=>{
  const p=f.properties,key=colorIdentity(p.controlArea?p.sovereignName||p.controller:p.NAME);node(key);
  return {key,from:Math.max(from,p.validFrom??from),to:Math.min(to,p.validTo??to),bounds:bounds(f.geometry)};
 });
 for(let i=0;i<rows.length;i++)for(let j=i+1;j<rows.length;j++){
  const a=rows[i],b=rows[j];if(a.key===b.key||a.from>b.to||b.from>a.to)continue;
  if(!a.bounds.some(x=>b.bounds.some(y=>overlap(x,y))))continue;
  const weight=Math.sqrt(Math.min(a.to,b.to)-Math.max(a.from,b.from)+1);
  node(a.key).set(b.key,(node(a.key).get(b.key)||0)+weight);node(b.key).set(a.key,(node(b.key).get(a.key)||0)+weight);
 }
}
const index=read('public/data/temporal/index.json');
for(const c of index.centuries)add(read(`public/data/temporal/${c}.geojson`),c*100,c*100+99);
for(const entry of read('public/data/manifest.json'))add(read('public/data/'+entry.filename),entry.year,entry.year);
const pinned={'法国':'#65a6ce','德国':'#bd98ce','德国（联邦）':'#bd98ce','德国（民主）':'#cf7a79','英国':'#cf7a79','西班牙':'#d7a641','意大利':'#8057a6','葡萄牙':'#79b08a','苏联':'#a52b48','俄罗斯':'#79b08a','美国':'#3768ac','日本':'#cf7a79','明朝':'#d7a641','清朝':'#dc985e','罗马帝国':'#cf7a79','奥斯曼帝国':'#5da99e'};
Object.assign(pinned,{'盖尔爱尔兰诸领地':'#ac87c9','爱尔兰王权领地':'#d7a641','西亚丁保护诸邦':'#d7a641','东亚丁保护诸邦':'#ac87c9','Colony of Aden':'#cf7a79'});
Object.assign(pinned,{'Suiyuan Chahar Local Authorities':'#3976c9','Inner Mongolian Autonomy Movement Areas':'#247d8f'});
Object.assign(pinned,{"Japanese clan - Oda": "#dc985e", "Japanese clan - Toyotomi": "#b5b35f", "Japanese clan - Uesugi": "#65a6ce", "Japanese clan - Takeda": "#bf7860", "Japanese clan - Mori": "#ac87c9", "Japanese clan - Shimazu": "#5da99e", "Japanese clan - Ouchi": "#d7a641", "Japanese clan - Amago": "#cf7a79", "Japanese clan - Otomo": "#899bd2", "Japanese clan - Go-Hojo": "#d7a641", "Japanese clan - Date": "#c28b45", "Japanese clan - Imagawa": "#77bacc", "Japanese clan - Saito": "#b89870", "Japanese clan - Chosokabe": "#d58cac", "Japanese clan - Hori": "#8caa62", "Japanese clan - Kimotsuki": "#dc985e"});
Object.assign(pinned,{"东喀喇汗国": "#dc985e", "西喀喇汗国": "#65a6ce", "叶尔羌汗国": "#65a6ce", "天山蒙兀儿诸部": "#cdb681", "天山吉尔吉斯诸部": "#cdb681", "吐鲁番汗国": "#79b08a"});
Object.assign(pinned,{'威尼斯共和国':'#367870','奥地利':'#704e9b','基马克汗国':'#dc985e','中华人民共和国':'#ed5141'});
const colors=new Map(Object.entries(pinned)),degree=k=>[...node(k).values()].reduce((s,n)=>s+n,0);
const keys=[...graph.keys()].sort((a,b)=>degree(b)-degree(a)||a.localeCompare(b,'en'));
const loss=(key,color)=>[...node(key)].reduce((sum,[other,weight])=>colors.has(other)?sum+weight*Math.max(0,90-colorDistance(color,colors.get(other)))**2:sum,0);
for(const key of keys){if(colors.has(key))continue;colors.set(key,[...POLITY_PALETTE].sort((a,b)=>loss(key,a)-loss(key,b)||POLITY_PALETTE.indexOf(a)-POLITY_PALETTE.indexOf(b))[0]);}
for(let pass=0;pass<4;pass++)for(const key of keys){if(pinned[key])continue;const current=colors.get(key),best=[...POLITY_PALETTE].sort((a,b)=>loss(key,a)-loss(key,b)||(a===current?-1:b===current?1:POLITY_PALETTE.indexOf(a)-POLITY_PALETTE.indexOf(b)))[0];colors.set(key,best);}
const registry=Object.fromEntries([...colors].sort(([a],[b])=>a.localeCompare(b,'en')));
fs.writeFileSync(new URL('../src/color-registry.mjs',import.meta.url),'// Fixed historical polity colors. Regenerate explicitly with scripts/prepare_stable_colors.mjs.\nexport const polityColors='+JSON.stringify(registry,null,1)+';\n');
fs.writeFileSync(new URL('../public/data/color-policy.json',import.meta.url),JSON.stringify({policy:'固定势力配色；相邻关系仅在离线规划时参与，不在切换年份时重新分配。',identities:colors.size,edges:[...graph.values()].reduce((s,m)=>s+m.size,0)/2,planning:'所有时期的空间邻近关系与共同有效期；有限调色板不能保证每对邻国都有很大色差，深浅双层国界维持可读性。',pinned,unknown:'未收录势力使用固定名称哈希，不随浏览顺序改变。'},null,2));
console.log('Fixed colors:',colors.size,'historical neighbor edges:',[...graph.values()].reduce((s,m)=>s+m.size,0)/2);


