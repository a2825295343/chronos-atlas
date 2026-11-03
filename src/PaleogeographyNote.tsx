import {useEffect,useState} from 'react';
import {paleogeographyAt} from './paleogeography.mjs';
export default function PaleogeographyNote({year}:{year:number}){
 const [index,setIndex]=useState<any>(null);
 useEffect(()=>{fetch('/data/paleogeography/index.json').then(r=>r.ok?r.json():null).then(setIndex).catch(()=>{});},[]);
 const slice=paleogeographyAt(index,year);if(!slice)return null;
 return <details className="paleogeography-note"><summary>古海岸线 · 海平面约 {slice.estimate>0?'+':''}{slice.estimate} 米</summary><p>海平面估计不确定性约 ±{slice.sigma} 米。当前岸线采用 {slice.level} 米高程切片，随时间切换。</p><p>陆架人群是活动区域参考，不代表统一国家。局地沉降、冰川均衡调整与古河道尚未完整复原。</p><a href={index.source} target="_blank" rel="noreferrer">NOAA 数据与复原说明 ↗</a></details>;
}
