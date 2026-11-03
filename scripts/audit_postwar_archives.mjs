import{readFileSync,writeFileSync,existsSync}from'node:fs';
import{activePolities}from'../src/temporal.mjs';
import{leadershipFor,selectFlag}from'../src/archive-rules.mjs';
const read=p=>JSON.parse(readFileSync(new URL('../'+p,import.meta.url),'utf8'));
const atlas=read('public/data/temporal/19.geojson'),facts=read('public/data/polity-facts.json').entities,flags=read('public/data/flags.json').entities,portraits=read('public/data/portraits.json').people,curated=read('public/data/curated-facts.json');
const years=[];
for(let year=1945;year<=1955;year++){
 const rows=activePolities(atlas,year).features.map(f=>{
  const p=f.properties,qid=curated.identities[p.NAME]||p.qid,parentId=p.controlArea?p.controllerQid:p.sovereignQid,parent=facts[parentId];
  const lead=leadershipFor(facts[qid],parent,year),manual=(curated.polities[qid]?.rulers||[]).filter(r=>r[0]<=year&&year<=r[1]);
  const flag=selectFlag(flags[qid]||[],year).flag||selectFlag(flags[parentId]||[],year).flag;
  return{name:p.NAME,label:p.displayName||facts[qid]?.label||p.NAME,qid,parentId,parentName:facts[parentId]?.label||(p.controlArea?p.controller:p.sovereignName),fromSovereign:lead.fromSovereign,headAvailable:!!(lead.rows.length||manual.length),heads:manual.length?[]:lead.rows.map(r=>({qid:r.value,label:r.label,from:r.from,to:r.to,kind:r.kind,role:r.roleLabel,citation:r.citation||[],portrait:!!portraits[r.value]})),manualHeads:manual.length?manual.map(r=>r[2]):[],government:lead.governmentRows.map(r=>({label:r.label,from:r.from,to:r.to,role:r.roleLabel})),flagAvailable:!!flag&&existsSync(new URL('../public'+flag.path,import.meta.url)),flag:flag?.path,accuracy:p.accuracy};
 });
 const summary={records:rows.length,headRecords:rows.filter(r=>r.headAvailable).length,ownHeadRecords:rows.filter(r=>r.headAvailable&&!r.fromSovereign).length,centralHeadRecords:rows.filter(r=>r.fromSovereign).length,missingHeads:rows.filter(r=>!r.headAvailable).map(r=>r.name)};
 years.push({year,summary,rows});console.log(year,JSON.stringify(summary));
}
const report={reviewedAt:'2026-10-31',scope:'1945—1955年当前地图有效记录的字段完整度核查；不等于全球所有国家与每条战线均已逐条史学审定。',policy:['个人、摄政、集体机构和管理方中央领导人分别标注。','殖民地继承中央任期不等于已补齐当地历任总督。','任期按准确职务及有界起止年份匹配；不使用出生／去世年份推定执政。','年度视图包含年内交接，不能把所有人物理解为全年同时任职。'],years};
writeFileSync(new URL('../public/data/postwar-archive-audit.json',import.meta.url),JSON.stringify(report));
