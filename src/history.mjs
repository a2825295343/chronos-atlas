import {baseColor} from './colors.mjs';
export const MIN_YEAR = -123000;
export const MAX_YEAR = 2026;
// Nonlinear scale keeps recorded history usable without hiding prehistory.
export const TIME_STOPS = [[0,-123000],[8,-10000],[17,-3000],[30,-1000],[40,1],[54,1000],[66,1500],[78,1800],[89,1945],[100,2026]];
function interpolate(value, reverse=false) {
  const stops=TIME_STOPS.map(([x,y])=>reverse?[y,x]:[x,y]);
  for(let i=1;i<stops.length;i++) if(value<=stops[i][0]) {
    const [a,b]=stops[i-1], [c,d]=stops[i]; return b+(value-a)/(c-a)*(d-b);
  }
  return stops.at(-1)[1];
}
export const positionToYear = value => {const year=Math.round(interpolate(Math.max(0,Math.min(100,value))));return year===0?1:year;};
export const yearToPosition = year => interpolate(Math.max(MIN_YEAR,Math.min(MAX_YEAR,year)),true);
export const formatYear = year => year<0?`公元前 ${Math.abs(year).toLocaleString('zh-CN')} 年`:`公元 ${year} 年`;
export function snapshotForYear(entries,year) { return entries.filter(e=>e.year<=year).at(-1)??entries[0]; }
export function nextHistoricalYear(year, direction=1) { const next=year+direction; return next===0?direction:Math.max(MIN_YEAR,Math.min(MAX_YEAR,next)); }
export const colorForName=baseColor;
function ringArea(ring) {
  let total=0;
  for(let i=0;i<ring.length;i++) { const a=ring[i],b=ring[(i+1)%ring.length];let delta=(b[0]-a[0])*Math.PI/180;if(delta>Math.PI)delta-=2*Math.PI;if(delta< -Math.PI)delta+=2*Math.PI; total+=delta*(2+Math.sin(a[1]*Math.PI/180)+Math.sin(b[1]*Math.PI/180)); }
  return Math.abs(total*6371.0088**2/2);
}
export function areaKm2(geometry) {
  const polygons=geometry.type==='Polygon'?[geometry.coordinates]:geometry.type==='MultiPolygon'?geometry.coordinates:[];
  return polygons.reduce((sum,polygon)=>sum+Math.max(0,ringArea(polygon[0])-polygon.slice(1).reduce((s,r)=>s+ringArea(r),0)),0);
}
export function featureCenter(geometry) {
  const polygons=geometry.type==='Polygon'?[geometry.coordinates]:geometry.type==='MultiPolygon'?geometry.coordinates:[];
  const ring=polygons.reduce((best,p)=>ringArea(p[0])>ringArea(best)?p[0]:best,[]);
  if(!ring.length)return [0,0];
  let x=0,y=0,weight=0;
  for(let i=0;i<ring.length-1;i++){const a=ring[i],b=ring[i+1],w=a[0]*b[1]-b[0]*a[1];x+=(a[0]+b[0])*w;y+=(a[1]+b[1])*w;weight+=w;}
  return Math.abs(weight)>1e-6?[x/(3*weight),y/(3*weight)]:ring[0];
}
export function territoryBounds(geometries) {
  const longitudes=new Set();
  let south=90,north=-90;
  for(const geometry of geometries){
    const polygons=geometry.type==='Polygon'?[geometry.coordinates]:geometry.type==='MultiPolygon'?geometry.coordinates:[];
    for(const [exterior=[]] of polygons){
      for(const [longitude,latitude] of exterior){
        longitudes.add(((longitude%360)+360)%360);
        south=Math.min(south,latitude);
        north=Math.max(north,latitude);
      }
    }
  }
  if(!longitudes.size)return undefined;
  const sorted=[...longitudes].sort((a,b)=>a-b);
  // Cut the longitude circle at its largest empty gap to keep dateline islands together.
  let largestGap=-1,west=0,east=0;
  for(let i=0;i<sorted.length;i++){
    const current=sorted[i],next=sorted[(i+1)%sorted.length];
    const gap=next-current+(i===sorted.length-1?360:0);
    if(gap>largestGap){
      largestGap=gap;
      west=next>180?next-360:next;
      east=west+360-gap;
    }
  }
  const clampLatitude=latitude=>Math.max(-85,Math.min(85,latitude));
  return [[west,clampLatitude(south)],[east,clampLatitude(north)]];
}
export function pointInGeometry(point,geometry) {
  function inside(ring) {let result=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>point[1])!==(b[1]>point[1])&&point[0]<(b[0]-a[0])*(point[1]-a[1])/(b[1]-a[1])+a[0])result=!result;}return result;}
  const polys=geometry.type==='Polygon'?[geometry.coordinates]:geometry.type==='MultiPolygon'?geometry.coordinates:[];
  return polys.some(p=>inside(p[0])&&!p.slice(1).some(inside));
}
