import {useEffect,useState} from 'react';
import {ExternalLink} from 'lucide-react';
import {nationalObservation,comparableEconomy} from './statistics-policy.mjs';
type Observation={population?:number;gdp?:number;military?:number};
type Economy={name:string;iso2:string;capital:string;region:string;income:string;observations:Record<string,Observation>};
type Database=Record<string,Economy>;
let pending:Promise<Database>|undefined;
let nationalPending:Promise<any>|undefined;
export function useNationalStrength(code:string|undefined,year:number,name=''){
 const [data,setData]=useState<any>(null);
 useEffect(()=>{let live=true;nationalPending??=fetch('/data/national-strength.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error();return r.json();});nationalPending.then(d=>{if(live)setData(d);}).catch(()=>{});return()=>{live=false;};},[]);
 return nationalObservation(data,code,year,name);
}
const aliases:Record<string,string>={'United States of America':'USA','Russian Federation':'RUS',"People’s Republic of China":'CHN',"People\'s Republic of China":'CHN','South Korea':'KOR','North Korea':'PRK','Republic of Korea':'KOR','Democratic Republic of the Congo':'COD','Republic of the Congo':'COG','French Fifth Republic':'FRA','Federated Republic of Germany':'DEU','Republic of China':'TWN','Pahlavi Dynasty':'IRN','Francoist Spain':'ESP','Estado Novo':'PRT','Portuguese Republic':'PRT','Iraqi Republic':'IRQ','USA':'USA','United States':'USA','China':'CHN','Russia':'RUS','Egypt':'EGY','Iran':'IRN','Syria':'SYR','Turkey':'TUR','Vietnam':'VNM','Laos':'LAO','Burma':'MMR','Byelarus':'BLR','Congo':'COG','Zaire':'COD','Czech Republic':'CZE','Slovakia':'SVK','Bahamas':'BHS','Brunei':'BRN','Ivory Coast':'CIV','Hong Kong':'HKG',"Korea, Democratic People's Republic of":'PRK','Korea, Republic of':'KOR','Kyrgyzstan':'KGZ','Macedonia':'MKD','Swaziland':'SWZ','Venezuela':'VEN','Yemen':'YEM','Tanzania, United Republic of':'TZA','Trinidad':'TTO','Saint Kitts and Nevis':'KNA','Saint Lucia':'LCA','Saint Vincent and the Grenadines':'VCT'};
export function useStatistics(name:string,year:number){
 const [database,setDatabase]=useState<Database|null>(null);
 useEffect(()=>{pending??=fetch('/data/statistics.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error('Statistics unavailable');return r.json();});let cancelled=false;pending.then(db=>{if(!cancelled)setDatabase(db);}).catch(()=>{});return()=>{cancelled=true;};},[]);
 const core=name.replace(/^(?:(?:Federal|Federated|Islamic|Arab|Socialist|People's Democratic|People's|Democratic|Second|Third|First)\s+)?(?:Republic|Kingdom) of (?:the )?/,'');
 const normalize=(value:string)=>value.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]/g,'');
 const comparable=!(year<1991&&['Federal Republic of Germany','West Germany','German Democratic Republic','East Germany','Soviet Union','Union of Soviet Socialist Republics'].includes(name));
 const candidate=year>=1960&&database&&comparable?(aliases[name]?aliases[name]:aliases[core]?aliases[core]:Object.entries(database).find(([,e])=>normalize(e.name)===normalize(name)||normalize(e.name)===normalize(core))?.[0]):undefined;
 const economy=candidate&&database&&comparableEconomy(candidate,year,name)?database[candidate]:undefined;
 return {economy,observation:economy?.observations[String(year)]};
}
export const dollars=(value:number)=>value>=1e12?`${(value/1e12).toFixed(2)} 万亿美元`:value>=1e8?`${(value/1e8).toFixed(1)} 亿美元`:value>=1e4?`${(value/1e4).toFixed(1)} 万美元`:`${Math.round(value).toLocaleString()} 美元`;
export function StatisticsChart({economy,year}:{economy:Economy;year:number}){
 const points=Object.entries(economy.observations).filter(([y,v])=>Number(y)<=year&&v.gdp!=null).sort((a,b)=>Number(a[0])-Number(b[0]));
 if(points.length<2)return null;
 const first=Number(points[0][0]),last=Number(points.at(-1)![0]),max=Math.max(...points.map(p=>p[1].gdp!));
 const line=points.map(([y,v])=>`${((Number(y)-first)/(last-first)*246+1).toFixed(1)},${(59-v.gdp!/max*52).toFixed(1)}`).join(' ');
 return <div className="statistics-chart"><div className="section-label"><span/>经济的时间切片</div><p>名义 GDP · 当年美元 · 未调整通胀</p><svg viewBox="0 0 250 65" role="img" aria-label={`${first} 至 ${last} 年名义 GDP 变化`}><defs><linearGradient id="stat-fill" x1="0" y1="0" x2="0" y2="1"><stop stopColor="#c4b07a" stopOpacity=".2"/><stop offset="1" stopColor="#c4b07a" stopOpacity="0"/></linearGradient></defs><path d={`M 1,63 L ${line.replaceAll(' ',' L ')} L 247,63 Z`} fill="url(#stat-fill)"/><polyline points={line} fill="none" stroke="#bca575" strokeWidth="1.4"/></svg><div className="chart-axis"><span>{first}</span><span>{last}</span></div><a className="source-link" href="https://data.worldbank.org/indicator/NY.GDP.MKTP.CD" target="_blank" rel="noreferrer">World Bank WDI · CC BY 4.0 <ExternalLink size={11}/></a><p>统计单位依世界银行定义，与地图疆界可能不同。缺失年份不插值。</p></div>;
}
