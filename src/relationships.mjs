import {applies} from './archive-rules.mjs';
/** Merge identical reciprocal commitments while preserving asymmetric clauses. */
export function groupedAlliances(rows,code,year){
 const groups=new Map();
 for(const row of rows){
  if(!applies(row,year)||(row.fromCode!==code&&row.toCode!==code))continue;
  const outgoing=row.fromCode===code,peer=outgoing?row.toCode:row.fromCode;
  let group=groups.get(peer);
  if(!group){group={peer,peerName:outgoing?row.toName:row.fromName,commitments:new Map()};groups.set(peer,group);}
  const key=[row.from,row.to,[...row.terms].sort().join(','),row.rightCensored?'censored':''].join('|');
  const item=group.commitments.get(key)||{...row,outgoing:false,incoming:false};item.outgoing||=outgoing;item.incoming||=!outgoing;group.commitments.set(key,item);
 }
 return [...groups.values()].map(g=>({...g,commitments:[...g.commitments.values()]}));
}
const clean=name=>String(name||'').replace(/^\(|\)$/g,'').trim();
// Chronological catalogues are not historical alliances or sovereign powers.
const periodCatalogues=new Set(['Spring and Autumn States','Warring States','Warring States of China','Warring States China','Chinese States','Sixteen Kingdoms','Ten Kingdoms','Five Dynasties and Ten Kingdoms','Southern and Northern Dynasties']);
export function dependenciesAt(world,relations,year,curated=[]){
 const result=new Map();
 const add=row=>{if(!row.child||!row.parent||row.child===row.parent)return;const key=[row.kind,row.child,row.parent].join('|');if(!result.has(key))result.set(key,row);};
 for(const feature of world?.features||[]){
  const p=feature.properties;
  if(p?.controlArea)continue; // Military control is not a colonial relationship.
  if(p?.sovereignName&&!p.jointRulers?.length)add({kind:['overseas','protectorate','administration','federation','member'].includes(p.territoryType)?p.territoryType:'colony',child:p.NAME,parent:p.sovereignName,from:p.validFrom,to:p.validTo,source:p.sourceUrl||'Cliopatria · 地理分区',detail:p.partitionBasis||p.accuracy||'殖民统治／属地关系'});
  for(const raw of String(p?.memberOf||'').split(';')){
   const parent=clean(raw);
   if(!parent||periodCatalogues.has(parent)||parent===p.NAME||parent===p.sourcePolity||p.sovereignName)continue;
   add({kind:'member',child:p.NAME,parent,from:p.validFrom,to:p.validTo,source:'Cliopatria MemberOf',detail:'复合政权／联盟成员；不自动判定为殖民地或附属国'});
  }
 }
 for(const r of curated){
  if(!applies(r,year))continue;
  if(['vassal','protectorate','colony','allegiance'].includes(r.kind))add({kind:r.kind,child:r.child,parent:r.parent,from:r.from,to:r.to,detail:r.detail,source:r.source});
  if(r.kind==='personalUnion'&&r.members?.length>=2){const [child,parent]=[r.members[0],r.members[1]].sort();add({kind:'union',child,parent,from:r.from,to:r.to,title:r.title,detail:r.detail,source:r.source});}
 }
 for(const feature of world?.features||[]){const p=feature.properties;if(p.jointRulers?.length){for(const parent of p.jointRulers)add({kind:'jointRule',child:p.NAME,parent,from:p.validFrom,to:p.validTo,detail:'联合管理／共管；不将名义共管等同双方实际权力相等',source:p.sourceUrl||'共管关系历史记录'});}}
 for(const r of relations){
  if(!applies(r,year))continue;
  const text=clean(r.name),direct=text.match(/^(Allegiance|Vassalage) of (.+) to (.+)$/);
  if(direct)add({kind:direct[1]==='Vassalage'?'vassal':'allegiance',child:direct[2],parent:direct[3],from:r.from,to:r.to,source:'Cliopatria relation',detail:direct[1]==='Vassalage'?'附属／封臣关系':'名义效忠／朝贡；不等同领土兼并'});
  const union=text.match(/^Personal union of (.+) with (.+)$/);
  if(union){const [a,b]=[union[1],union[2]].sort();add({kind:'union',child:a,parent:b,from:r.from,to:r.to,source:'Cliopatria relation',detail:'共主联合；两地政体与行政体系可以不同'});}
 }
 return [...result.values()];
}

export function relationMembers(row){return Array.isArray(row.members)?row.members:[row.child,row.parent].filter(Boolean);}
