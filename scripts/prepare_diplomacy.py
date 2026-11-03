"""Convert original COW records from documented academic mirrors, retaining direction."""
import csv,json,pathlib,collections
ROOT=pathlib.Path(__file__).resolve().parents[1]
def read(name):return list(csv.DictReader((ROOT/'.local/cow'/name).open(newline='',encoding='utf-8-sig')))
def number(value):
    try:return int(value)
    except (TypeError,ValueError):return None
def main():
    countries={}
    for row in read('countries.csv'):countries[row['CCode']]=row['StateNme']
    grouped={}
    rows=read('alliance.csv')
    for row in rows:
        start=number(row['dyad_st_year']);end=number(row['dyad_end_year'])
        if start is None or end is None:continue
        kinds=[key for key in ['defense','neutrality','nonaggression','entente']if row[key]=='1']
        key=(row['version4id'],row['ccode1'],row['ccode2'],start,end,tuple(kinds))
        if key in grouped:
            grouped[key]['years'].add(number(row['year']));continue
        grouped[key]={'years':{number(row['year'])},'id':'cow-a-'+ '-'.join(map(str,key[:5])),'kind':'alliance','from':start,'to':end,'fromCode':row['ccode1'],'toCode':row['ccode2'],'fromName':row['state_name1'],'toName':row['state_name2'],'terms':kinds,'startMonth':number(row['dyad_st_month']),'endMonth':number(row['dyad_end_month']),'leftCensored':row['left_censor']=='1','rightCensored':row['right_censor']=='1','source':'COW Formal Alliances 4.1','url':'https://correlatesofwar.org/data-sets/formal-alliances/'}
    alliances=[];rejected=[]
    for record in grouped.values():
        years=sorted(y for y in record.pop('years') if y is not None)
        runs=[]
        for y in years:
            if runs and y==runs[-1][-1]+1:runs[-1].append(y)
            else:runs.append([y])
        for run in runs:
            copy={**record,'sourceStart':record['from'],'sourceEnd':record['to'],'from':max(record['from'],run[0]),'to':min(record['to'],run[-1]),'id':record['id']+'-'+str(run[0])+'-'+','.join(record['terms'])}
            if copy['from']>copy['to']:
                rejected.append({'id':copy['id'],'problem':'Annual row outside original dyad interval'});continue
            copy['rightCensored']=record['rightCensored'] and copy['to']>=2012
            alliances.append(copy)
    war_rows=[]
    for row in read('war.csv'):
        for period in [1,2]:
            start=number(row['StartYear'+str(period)]);end=number(row['EndYear'+str(period)])
            if not start or not end or start<0 or end<0:continue
            war_rows.append({'id':'cow-w-'+row['WarNum']+'-'+row['ccode']+'-'+str(period),'warId':row['WarNum'],'kind':'war','name':row['WarName'],'code':row['ccode'],'country':row['StateName'],'side':row['Side'],'from':start,'to':end,'startMonth':number(row['StartMonth'+str(period)]),'endMonth':number(row['EndMonth'+str(period)]),'source':'COW Inter-State Wars 4.0','url':'https://correlatesofwar.org/data-sets/cow-war/'})
    output={'rejectedIntervals':rejected,'countries':countries,'alliances':alliances,'wars':war_rows,'coverage':{'alliances':[1816,2012],'wars':[1816,2007]},'citation':['Gibler, Douglas M. 2009. International Military Alliances, 1648–2008. CQ Press.','Sarkees, Meredith Reid and Frank Wayman. 2010. Resort to War: 1816–2007. CQ Press.'],'downloadMirrors':['https://github.com/hwalbert/diss_repo','https://github.com/mateosuster/cow_data'],'notes':['条约承诺有方向，不能将单向承诺默认为双向。','战争按参战国、阵营和参战时间记录；同一战争同侧不等于相互作战。','数据库结束年不是条约真实终止年。']}
    (ROOT/'public/data/diplomacy.json').write_text(json.dumps(output,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    print('Alliances:',len(grouped),'participation periods:',len(war_rows),'source annual rows:',len(rows),flush=True)
if __name__=='__main__':main()
