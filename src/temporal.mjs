import {colorGroups} from './color-groups.mjs';
import {colorPolities} from './colors.mjs';
import polygonClipping from 'polygon-clipping';

const cambodianUnions=new WeakMap();
function cambodianTerritory(main,other){
 if(!other)return main.geometry;
 let matches=cambodianUnions.get(main);
 if(!matches){matches=new WeakMap();cambodianUnions.set(main,matches);}
 if(!matches.has(other))matches.set(other,{type:'MultiPolygon',coordinates:polygonClipping.union(main.geometry.coordinates,other.geometry.coordinates)});
 return matches.get(other);
}
/** Query dated records; a relationship polygon never becomes a territorial owner. */
export function activePolities(collection,year){
 const rows=new Map();
 for(const feature of collection.features){
  const p=feature.properties;
  if(!p||p.validFrom>year||p.validTo<year)continue;
  const previous=rows.get(p.NAME);
  if(!previous||p.validFrom>previous.properties.validFrom||(p.validFrom===previous.properties.validFrom&&p.validTo<previous.properties.validTo))rows.set(p.NAME,feature);
 }
 // Supplemental Azerbaijani coverage is merged into the republic's geometry.
 if(year>=1992&&rows.get('Republic of Azerbaijan')?.properties.qid==='Q227'&&rows.get('Azerbaijan')?.properties.qid==='Q227')rows.delete('Azerbaijan');
 if(year>=1380&&year<=1394&&rows.has('Golden Horde'))rows.delete('Blue Horde');
 // The royal Prussian record supersedes the older composite source outline.
 if(year>=1701&&rows.has('Kingdom of Prussia'))rows.delete('Brandenburg-Prussia');
 // Both source names describe post-Angkor Cambodia, sometimes in separate
 // regions. Preserve their combined territory under one historical identity.
 if(year>=1432&&year<=1862){
  const main=rows.get('Khmer Empire')||rows.get('Cambodia');
  if(main){
   const other=rows.get('Khmer Empire')&&rows.get('Cambodia');
   rows.delete('Khmer Empire');rows.delete('Cambodia');
   rows.set('Kingdom of Cambodia',{...main,geometry:cambodianTerritory(main,other),properties:{...main.properties,
    NAME:'Kingdom of Cambodia',qid:'Q4919413',displayName:'柬埔寨王国',labelPath:undefined,
    representationNote:'原始地图以 Cambodia 和 Khmer Empire 分别收录后吴哥时期的地域，现合并为同一王国。边界仍属历史范围概化。'}});
  }
 }
 return colorPolities({type:'FeatureCollection',features:[...rows.values()].map(feature=>{
  const p=feature.properties;
  let name=p.NAME,qid=p.qid;
  const corrected={'Kingdom of France':'Q70972','Republic of Korea':'Q884','Republic of the Congo':'Q971','Republic of Vietnam':'Q180573','Republic of Albania':'Q222','Republic of Bulgaria':'Q219'};
  if(name==='Later Zhou'&&year<0){name='Eastern Zhou';qid='local:eastern-zhou';}
  if(name==='Western Jin'&&year>=317){name=year<420?'Eastern Jin':'Liu Song Dynasty';qid=year<420?'local:eastern-jin':'Q49697';}
  if(name==='Yue')qid='local:yue-state';
  if(name==='Qin')qid='Q34756';
  if(name==='Burgundian Kingdom'&&year>=534){name='Frankish Burgundy';qid='local:frankish-burgundy';}
  if(name==='Serbs'&&year>=1804&&year<=1918){
   name=year<1815?'Revolutionary Serbia':year<1882?'Principality of Serbia':'Kingdom of Serbia';
   qid=year<1882?'Q13107370':'Q241748';
  }
  qid=corrected[name]||qid;
  if(name==='First Hellenic Republic'&&year>=1913&&year<=1940){
   const republican=year>=1924&&year<=1934;
   name=republican?'Second Hellenic Republic':'Kingdom of Greece';
   qid=republican?'local:second-hellenic-republic':'Q209065';
  }
  if(name==='Kingdom of Lithuania'&&year>=1919&&year<=1940){name='Republic of Lithuania';qid='Q37';}
  if(name==='Brandenburg-Prussia'&&year>=1701){name='Kingdom of Prussia';qid='Q27306';}
  if(name==='Republic of China')qid=year<1949?'Q13426199':'Q865';
  if(name==='Estado Novo'&&year>=1974)qid='Q45';
  if(name==='Kingdom of Great Britain'){
   name=year<1801?'Kingdom of Great Britain':year<1922?'United Kingdom of Great Britain and Ireland':'United Kingdom';
   qid=year<1801?'Q161885':year<1922?'Q174193':'Q145';
  }
  if(name==='United Principalities of Moldavia and Wallachia'&&year>=1881){name='Kingdom of Romania';qid='Q203493';}
  const sovereignName=p.sovereignName==='United Kingdom'?(year<1707?'Kingdom of England':year<1801?'Kingdom of Great Britain':year<1922?'United Kingdom of Great Britain and Ireland':'United Kingdom'):p.sovereignName;
  const sovereignQid=p.sovereignName==='United Kingdom'?(year<1707?'Q179876':year<1801?'Q161885':year<1922?'Q174193':'Q145'):p.sovereignQid;
  const chineseNames={'Kingdom of Prussia':'普鲁士王国','Norman England':'诺曼英格兰王国','Burgundian Kingdom':'勃艮第王国','Frankish Burgundy':'法兰克勃艮第王国','Revolutionary Serbia':'塞尔维亚起义政权','Principality of Serbia':'塞尔维亚公国','Kingdom of Serbia':'塞尔维亚王国','Second Hellenic Republic':'希腊第二共和国','Kingdom of Greece':'希腊王国','Republic of Lithuania':'立陶宛共和国','Eastern Zhou':'东周','Eastern Jin':'东晋','Liu Song Dynasty':'刘宋','Yue':'越国','Qin':'秦国'};
  const displayName=name==='Li Zicheng'?(year>=1644?'大顺':'李自成起义军'):chineseNames[name]||(name!==p.NAME?(colorGroups[name]||name):p.displayName);
  return {...feature,properties:{...p,sourceQid:p.sourceQid||p.qid,sourceName:p.sourceName||p.NAME,NAME:name,SUBJECTO:p.controlArea?p.controller:name,qid,entityId:qid,sovereignName,sovereignQid,displayName}};
 })});
}
const stops=[[1.8,0,1],[3,0,1],[4,18,1.3],[6,48,2.4],[8,67,3.7],[10,72,4.4]];
export function perspectiveForZoom(zoom){
 if(zoom<=stops[0][0])return {pitch:0,exaggeration:1};
 for(let i=1;i<stops.length;i++)if(zoom<=stops[i][0]){
  const a=stops[i-1],b=stops[i],raw=(zoom-a[0])/(b[0]-a[0]),t=raw*raw*(3-2*raw);
  return {pitch:a[1]+(b[1]-a[1])*t,exaggeration:a[2]+(b[2]-a[2])*t};
 }
 return {pitch:72,exaggeration:4.4};
}




