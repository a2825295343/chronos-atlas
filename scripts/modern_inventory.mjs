import{readFileSync,writeFileSync}from'node:fs';
import{activePolities}from'../src/temporal.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const raw=read('public/data/temporal/20.geojson'),curated=read('public/data/curated-facts.json');
const special={'Mujahideen':'原始资料中的叙利亚武装势力分组，不构成具有单一国家元首的主权国家','Gaza/Hamas':'战时地方政府与武装组织记录，不能由国家总统或单一组织领导人代替全部实际权力结构','Russian-occupied territories':'军事占领区域，不能把控制方元首自动认定为该领土主权国家元首'};
const rows=activePolities(raw,2024).features.map(f=>{const p=f.properties;return{name:p.NAME,qid:curated.identities[p.NAME]||p.qid,label:p.displayName,sourceQid:p.sourceQid,sovereign:p.sovereignName,sovereignQid:p.sovereignQid,control:p.controlArea,from:p.validFrom,to:p.validTo,category:special[p.NAME]?'non-state':p.sovereignName?'territory':'state',exception:special[p.NAME]};});
writeFileSync(new URL('../.local/modern-polities.json',import.meta.url),JSON.stringify(rows,null,2));
console.log(JSON.stringify({polities:rows.length,states:rows.filter(r=>r.category==='state').length,territories:rows.filter(r=>r.category==='territory').length,nonState:rows.filter(r=>r.category==='non-state').length}));
