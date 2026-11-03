const $=id=>document.getElementById(id);
const el=(tag,text,className)=>{const node=document.createElement(tag);node.textContent=text;if(className)node.className=className;return node;};
try{
 const data=await fetch('/data/postwar-archive-audit.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('核查资料未打包');return r.json();});
 $('scope').textContent=data.scope;
 for(const entry of data.years){const option=el('option',`${entry.year} 年`);option.value=String(entry.year);$('year').append(option);}
 const requested=new URL(location.href).searchParams.get('year');$('year').value=data.years.some(r=>String(r.year)===requested)?requested:'1950';
 function render(){
  const selected=data.years.find(r=>String(r.year)===$('year').value),s=selected.summary,q=$('search').value.trim().toLocaleLowerCase();
  for(const [id,key]of [['records','records'],['heads','headRecords'],['own','ownHeadRecords'],['central','centralHeadRecords']])$(id).textContent=s[key];
  $('map-link').href=`/?year=${selected.year}`;$('map-link').textContent=`返回${selected.year}年地图 ↗`;
  const rows=selected.rows.filter(r=>(!$('missing').checked||!r.headAvailable)&&(!q||[r.label,r.name,...r.heads.map(h=>h.label),...r.government.map(h=>h.label)].some(x=>String(x).toLocaleLowerCase().includes(q)))).sort((a,b)=>a.label.localeCompare(b.label,'zh-CN'));
  const fragment=document.createDocumentFragment();
  for(const r of rows){
   const tr=document.createElement('tr'),country=document.createElement('td'),heads=document.createElement('td'),government=document.createElement('td');
   country.append(el('strong',r.label));country.append(el('small',r.name));
   if(r.fromSovereign)country.append(el('span','上层／管理方中央任期 · '+(r.parentName||r.parentId),'parent'));
   for(const h of r.heads){const box=el('div',h.label,'person');box.append(el('small',`${h.from??'起年待核定'}—${h.to??'止年待核定'} · ${h.role||'有年代的任期记录'}`));if(h.citation?.[0]){const source=el('a','任期出处 ↗');source.href=h.citation[0];source.target='_blank';source.rel='noreferrer';box.append(source);}heads.append(box);}
   for(const name of r.manualHeads)heads.append(el('div',name,'person'));
   if(!r.headAvailable)heads.append(el('small','该年字段仍待补充'));
   for(const h of r.government){const box=el('div',h.label,'person');box.append(el('small',`${h.from??'起年待核定'}—${h.to??'止年待核定'} · ${h.role||'政府首脑'}`));government.append(box);}
   if(!r.government.length)government.append(el('small','未另收录独立政府首脑任期；不推断其不存在'));
   tr.append(country,heads,government);fragment.append(tr);
  }
  $('rows').replaceChildren(fragment);$('footer').textContent=`显示 ${rows.length} 条 · 核查日期 ${data.reviewedAt} · 详细方法与来源见各条任期及地图资料页`;
 }
 for(const id of ['year','search','missing'])$(id).addEventListener(id==='search'?'input':'change',render);render();
}catch(error){$('scope').textContent='读取失败：'+error.message+'。请重新构建项目并刷新。';}
