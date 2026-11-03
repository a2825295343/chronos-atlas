const $=id=>document.getElementById(id),el=(tag,text)=>{const n=document.createElement(tag);n.textContent=text;return n;};
let report;
const categories={state:'国家记录',territory:'海外领地','non-state':'非国家控制记录'};
function personList(rows){
 const fragment=document.createDocumentFragment();
 if(!rows.length){const n=el('span','尚待完整核定');n.className='gap';fragment.append(n);}
 for(const p of rows){const line=el('div',p.name);if(/^Q\d+$/.test(p.qid)){const a=el('a',' ↗');a.href='https://www.wikidata.org/wiki/'+p.qid;a.target='_blank';a.rel='noreferrer';line.append(a);}fragment.append(line);const dates=el('small',p.at!=null?`${p.at}年来源观测`:`${p.from??'起年未记'}—${p.to??'任期末年未记'}`);fragment.append(dates);if(p.reviewNote){const warning=el('small',p.reviewNote);warning.className='gap';fragment.append(warning);}if(p.derived){const badge=el('div','据对应职务资料补全');badge.className='badge';fragment.append(badge);}}
 return fragment;
}
function render(){
 if(!report)return;const y=report.years.find(y=>y.year===Number($('year').value)),s=y.summary,queries=$('search').value.toLowerCase().trim().split(/[，,;；|\s]+/).filter(Boolean),filter=$('filter').value;
 $('cards').replaceChildren(...[[s.stateFlags+'/'+s.states,'国家记录有可用旗帜'],[s.stateHeadStates+'/'+s.states,'国家记录有元首状态'],[s.governmentHeadRecords+'/'+s.states,'国家记录有政府首脑'],[s.territoryFlags+'/'+s.territories,'领地记录有代表旗']].map(([value,label])=>{const c=el('div','');c.className='card';c.append(el('strong',value),el('span',label));return c;}));
 const rows=y.rows.filter(r=>(filter==='all'||r.category===filter||filter==='missing'&&(!r.flagAvailable||!r.headAvailable||!r.governmentHeads.length||!r.capitalAvailable||!r.governmentTypeAvailable)||filter==='review'&&[...r.heads,...r.governmentHeads].some(p=>p.reviewNote)||filter==='derived'&&[...r.heads,...r.governmentHeads].some(p=>p.derived))&&(!queries.length||queries.some(q=>JSON.stringify(r).toLowerCase().includes(q))));
 $('count').textContent=`${y.year}年 · ${rows.length}条记录 · 核查日期 ${report.reviewedAt} · ${s.termReviewRecords}条国家记录含待复核任期异文`;
 $('rows').replaceChildren(...rows.map(r=>{const tr=document.createElement('tr'),name=document.createElement('td'),flag=document.createElement('td'),head=document.createElement('td'),gov=document.createElement('td'),other=document.createElement('td');name.append(el('strong',r.label),el('small',categories[r.category]),el('small',r.name));
  if(r.flagAvailable){const a=document.createElement('a');a.href=r.flagSource;a.target='_blank';a.rel='noreferrer';const img=document.createElement('img');img.className='flag';img.loading='lazy';img.alt=r.label+'的旗帜';img.src=r.flagPath;a.append(img);flag.append(a,el('small',r.category==='territory'?'领地旗／主权方代表旗':'图像与许可 ↗'));}else flag.append(el('span',r.category==='non-state'?'不统一套用国家旗帜':'待补全'));
  head.append(personList(r.heads));gov.append(personList(r.governmentHeads));other.append(el('div',r.capitalAvailable?'首都：有资料':'首都：待核定'),el('div',r.governmentTypeAvailable?'政体：有资料':'政体：待核定'));if(r.exception)other.append(el('small',r.exception));tr.append(name,flag,head,gov,other);return tr;}));
}
for(const id of ['year','filter','search'])$(id).addEventListener(id==='search'?'input':'change',render);
fetch('/data/modern-archive-audit.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(d=>{report=d;$('scope').textContent=d.scope;$('limits').textContent=d.policy.join(' ');render();}).catch(()=>{$('scope').textContent='核查报告读取失败，请重新构建后刷新。';});
