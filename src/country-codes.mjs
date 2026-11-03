import referenceCountries from './cow-countries.mjs';
const normalize=text=>text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]/g,'');
const aliases={'Pahlavi Dynasty':'Iran','Francoist Spain':'Spain','Estado Novo':'Portugal','Portuguese Republic':'Portugal','Portuguese Empire':'Portugal','French Directory':'France','French Consulate':'France','First Hellenic Republic':'Greece','Third Hellenic Republic':'Greece','Empire of Japan':'Japan','Japanese Empire':'Japan','French Empire':'France','United Kingdom of Great Britain and Ireland':'United Kingdom','United Kingdom of Great Britain and Northern Ireland':'United Kingdom','Russian Federation':'Russia','Union of Soviet Socialist Republics':'Russia','French Fifth Republic':'France','Federated Republic of Germany':'German Federal Republic','Kingdom of Romania':'Rumania','USA':'United States of America','United States':'United States of America','Kingdom of France':'France','French Republic':'France','French Third Republic':'France','Second French Empire':'France','First French Empire':'France','Bourbon Kingdom of France':'France','German Empire':'Germany','Weimar Republic':'Germany','Nazi Germany':'Germany','Prussia':'Germany','West Germany':'German Federal Republic','East Germany':'German Democratic Republic','Russian Empire':'Russia','Soviet Union':'Russia','USSR':'Russia','Kingdom of Italy':'Italy','Kingdom of Spain':'Spain','Kingdom of Portugal':'Portugal','Qing Dynasty':'China',"People's Republic of China":'China','Ottoman Empire':'Turkey','Türkiye':'Turkey','Republic of Turkey':'Turkey','Zaire':'Democratic Republic of the Congo','Democratic Republic of Vietnam':'Vietnam','North Vietnam':'Vietnam','South Vietnam':'Republic of Vietnam','Republic of Korea':'South Korea','Democratic People’s Republic of Korea':'North Korea'};
/** COW identities describe changing statistical jurisdictions, not name similarity. */
export function cowCode(name,entity,countries,year){
 name=name.replace(/^Government of /,'').replace('Russia (Soviet Union)','Russia').replace('Vietnam (North Vietnam)',year<=1975?'North Vietnam':'Vietnam').replace('Yemen (North Yemen)',year<1990?'Yemen Arab Republic':'Yemen').replace('Myanmar (Burma)','Myanmar').replace('Serbia (Yugoslavia)','Serbia');
 if(name==="Hungarian People's Republic")return year>=1949&&year<=1989?'310':undefined;
 if(name==='Republic of China')return year>=1949?'713':'710';
 if(name==='Taiwan')return year>=1949?'713':undefined;
 if(name==='Republic of Vietnam')return year>=1955&&year<=1975?'817':undefined;
 if(name==='North Vietnam'||name==='Democratic Republic of Vietnam')return year>=1954&&year<=1976?'816':undefined;
 if(name==='South Vietnam')return year>=1955&&year<=1975?'817':undefined;
 if(['West Germany','German Federal Republic','Federal Republic of Germany','Federated Republic of Germany'].includes(name))return year>=1949?'260':undefined;
 if(['East Germany','German Democratic Republic'].includes(name))return year>=1949&&year<=1990?'265':undefined;
 const core=text=>text.replace(/^Government of /,'').replace(/^(?:(?:Federal|Federated|Islamic|Arab|Socialist|People's Democratic|People's|Democratic|Second|Third|First)\s+)?(?:Republic|Kingdom) of (?:the )?/,'');
 const candidates=[aliases[name]||name,aliases[entity?.en||'']||entity?.en||'',core(name)];
 if(candidates.includes('Germany')&&year>=1990)candidates.unshift('German Federal Republic');
 for(const candidate of candidates)for(const [code,label]of Object.entries(Object.keys(countries).length?countries:referenceCountries))if(normalize(candidate)===normalize(label))return code;
 return undefined;
}
