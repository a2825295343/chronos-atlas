import type {Map} from 'maplibre-gl';
/** A small, precomputed animated pattern, clipped by the geographic ocean mask.
 * No full-screen DOM overlay, pixel readback, or per-frame geographic updates. */
export function installOceanRipples(map:Map){
 const size=128,frames:Uint8Array[]=[],motion=matchMedia('(prefers-reduced-motion: reduce)'),canvas=document.createElement('canvas');canvas.width=size;canvas.height=size;
 const ctx=canvas.getContext('2d')!;
 for(let frame=0;frame<12;frame++){
  ctx.clearRect(0,0,size,size);ctx.lineWidth=.65;
  for(let row=-1;row<10;row++)for(let col=-1;col<6;col++){
   const phase=frame/12*Math.PI*2+row*.73+col*.91,alpha=.085+.055*Math.sin(phase),x=col*30+(row%2)*14,y=row*17;
   ctx.strokeStyle=`rgba(151,205,218,${Math.max(.015,alpha)})`;ctx.beginPath();
   for(let i=0;i<23;i++){const px=x+i,py=y+Math.sin(i/10+phase)*1.8;if(i===0)ctx.moveTo(px,py);else ctx.lineTo(px,py);}ctx.stroke();
  }
  frames.push(new Uint8Array(ctx.getImageData(0,0,size,size).data));
 }
 let previous=-1,timer:ReturnType<typeof setTimeout>|undefined;
 const schedule=()=>{if(!timer&&!motion.matches&&!document.hidden)timer=setTimeout(()=>{timer=undefined;map.triggerRepaint();},110);};
 map.addImage('ocean-ripples',{width:size,height:size,data:frames[0],render(){
  const frame=motion.matches?0:Math.floor(performance.now()/140)%12;if(frame===previous){schedule();return false;}previous=frame;(this as {data:Uint8Array}).data=frames[frame];schedule();return true;
 }});
 map.addLayer({id:'ocean-ripples',type:'fill',source:'ocean-mask',filter:['!=',['get','seamPatch'],true],paint:{'fill-pattern':'ocean-ripples','fill-antialias':false,'fill-opacity':['interpolate',['linear'],['zoom'],0,.35,3,.85,7,1]}});
 const wake=()=>map.triggerRepaint();document.addEventListener('visibilitychange',wake);motion.addEventListener('change',wake);
 map.on('remove',()=>{if(timer)clearTimeout(timer);document.removeEventListener('visibilitychange',wake);motion.removeEventListener('change',wake);});
}

