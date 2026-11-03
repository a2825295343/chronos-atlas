import {useEffect,useRef,useState} from 'react';
import {formatYear,positionToYear,yearToPosition} from './history.mjs';
/** Keep pointer feedback local. Heavy atlas requests are coalesced, with an
 * immediate final commit on pointer/keyboard release and cancellation. */
export default function TimelineRange({year,onChange}:{year:number;onChange:(year:number)=>void}){
 const [preview,setPreview]=useState(year),dragging=useRef(false),next=useRef(year),timer=useRef<ReturnType<typeof setTimeout>|null>(null),callback=useRef(onChange);
 callback.current=onChange;
 useEffect(()=>{if(!dragging.current){setPreview(year);next.current=year;}},[year]);
 useEffect(()=>()=>{if(timer.current)clearTimeout(timer.current);},[]);
 const commit=()=>{if(timer.current)clearTimeout(timer.current);timer.current=null;dragging.current=false;callback.current(next.current);};
 return <><div className="timeline-progress" style={{width:yearToPosition(preview)+'%'}}/><input className="time-range" type="range" aria-label="历史时间线" aria-valuetext={formatYear(preview)} min={0} max={100} step={0.005} value={yearToPosition(preview)} onPointerDown={()=>{dragging.current=true;}} onChange={e=>{const value=positionToYear(Number(e.target.value));next.current=value;setPreview(value);if(!timer.current)timer.current=setTimeout(()=>{timer.current=null;callback.current(next.current);},180);}} onPointerUp={commit} onPointerCancel={commit} onKeyUp={commit} onBlur={commit}/>{dragging.current&&<output className="time-preview" style={{left:Math.max(5,Math.min(95,yearToPosition(preview)))+'%'}}>{formatYear(preview)}</output>}</>;
}
