import {useEffect,useState} from 'react';
type Portrait={path:string;label:string;file:string;commons:string;license:string;source:string;caption:string};
type Database={people:Record<string,Portrait>;manualRulers:Record<string,string>};
let pending:Promise<Database>|undefined;
export function usePortraits(){const [data,setData]=useState<Database|null>(null);useEffect(()=>{let cancelled=false;pending??=fetch('/data/portraits.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error();return r.json();});pending.then(d=>{if(!cancelled)setData(d);}).catch(()=>{pending=undefined;});return()=>{cancelled=true;};},[]);return data;}
export function RulerPortrait({qid,name}:{qid?:string;name:string}){const data=usePortraits(),portrait=qid?data?.people[qid]:undefined;return portrait?<a className="ruler-portrait" href={portrait.commons} target="_blank" rel="noreferrer" title={`${portrait.caption}；${portrait.license}`}><img src={portrait.path} alt={`${name}的肖像`} loading="lazy"/><small>肖像来源 ↗</small></a>:<div className="ruler-portrait missing-portrait"><span>♙</span><small>肖像待补</small></div>;}
