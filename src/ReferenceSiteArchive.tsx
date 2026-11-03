import {ExternalLink,Info,MapPin} from 'lucide-react';
import type {AtlasFeature} from './MapView';
import {localName} from './data';

export default function ReferenceSiteArchive({feature}:{feature:AtlasFeature}){
 const p=feature.properties,point=feature.geometry.type==='Point'?feature.geometry.coordinates:[];
 return <>
  <p className="detail-description">{p.accuracy}</p>
  <div className="reference-banner"><Info size={16}/>据点位置参考 · 不划为独立领土</div>
  <dl className="fact-list">
   <div><dt>来源关联地区</dt><dd>{p.ownerLabel}</dd></div>
   <div><dt>来源关联势力</dt><dd>{localName(p.operator)}</dd></div>
   <div><dt>示意适用区间</dt><dd>{p.validFrom}—{p.validTo}</dd></div>
   <div><dt>参考坐标</dt><dd>{point.map(n=>n.toFixed(3)).join(', ')}</dd></div>
   <div><dt>具体站名与营业年份</dt><dd>待核定；沿用上游图源的时期范围</dd></div>
  </dl>
  <p className="micro-note"><MapPin size={12}/>原图的小块轮廓保存在原始数据中，当前位置是其内部参考点；未把小块面积当作据点的实控面积。</p>
  <a className="source-link" href={p.sourceUrl} target="_blank" rel="noreferrer">Cliopatria 原始轮廓 <ExternalLink size={12}/></a>
  <a className="source-link" href={p.contextSource} target="_blank" rel="noreferrer">加拿大地图集 · 毛皮贸易站资料 <ExternalLink size={12}/></a>
 </>;
}
