import {colorGroups} from './color-groups.mjs';
// Names of one continuing country share a color key. Dynasties and independent
// predecessor/successor states otherwise keep their own historical identity.
const aliases={
 'Buyid Dynasty':'布韦希王朝',
 'Republic of Haiti':'海地','Second Empire of Haiti':'海地','Empire of Haiti':'海地','Divided Haiti':'海地',
 'Principality of Bulgaria':'保加利亚','Kingdom of Bulgaria':'保加利亚',
 'Konbaung Dynasty':'缅甸','Burma':'缅甸','Myanmar':'缅甸',
 'Argentine Confederation':'阿根廷','Argentine Republic':'阿根廷','Argentina':'阿根廷',
 'Eastern Kara-Khanids':'东喀喇汗国','Western Karakhanid Khanate':'西喀喇汗国',
 'Eastern Moghulistan':'叶尔羌汗国','Western Moghulistan':'天山蒙兀儿诸部',
 'Kyrgyz Tian Shan Communities':'天山吉尔吉斯诸部','Turpan Khanate':'吐鲁番汗国',
 'Asuka Japan':'日本朝廷','Nara Japan':'日本朝廷','Heian Japan':'日本朝廷',
 'Tokugawa Government':'江户幕府','Japanese clan - Tokugawa':'江户幕府',
 'Japanese clan - Hashiba':'Japanese clan - Toyotomi','Japanese clan - Nagao':'Japanese clan - Uesugi',
 'Emirate of Riyadh':'内志酋长国','Emirate of Nejd and Hasa':'内志酋长国','Sultanate of Nejd':'内志酋长国',
 'Omani Al Busaidi State':'阿曼',
 'Sultanate of Muscat and Oman':'阿曼','Sultanate of Oman':'阿曼',
 'Qatar Dynasty':'卡塔尔','Qatar Protectorate':'卡塔尔','State of Qatar':'卡塔尔',
 'Sheikhdom of Kuwait':'科威特','State of Kuwait':'科威特',
 'Sheikhdom of Bahrain':'巴林','State of Bahrain':'巴林','Kingdom of Bahrain':'巴林',
 'Han Kingdom (Liu Bang)':'汉朝','Western Chu':'西楚',
 'Gaelic Irish Kingdoms':'盖尔爱尔兰诸领地','Gaelic Irish Lordships':'盖尔爱尔兰诸领地',
 'Lordship of Ireland':'爱尔兰王权领地','Kingdom of Ireland':'爱尔兰王权领地',
 'Western Aden Protectorate States':'西亚丁保护诸邦','Western South Arabian States':'西亚丁保护诸邦',
 'Eastern Aden Protectorate States':'东亚丁保护诸邦','Eastern South Arabian Protectorate':'东亚丁保护诸邦',
 "People's Republic of Southern Yemen":'也门',
 "People's Republic of China":'中华人民共和国',
 'Russian Socialist Federative Soviet Republic':'苏维埃俄国',
 'Old Kingdom of Norway':'挪威','Kingdom of Denmark':'丹麦','Crown of the Kingdom of Poland':'波兰王国','Royal Hungary':'匈牙利','Austrian Hereditary Lands':'奥地利','Austrian Empire':'奥地利',
 Germany:'德国',France:'法国',Spain:'西班牙',Portugal:'葡萄牙',Italy:'意大利',Japan:'日本',
 'United States':'美国','United States of America':'美国',USA:'美国',
 'United Kingdom':'英国','Kingdom of Great Britain':'英国','Kingdom of England':'英国',
 'United Kingdom of Great Britain and Ireland':'英国','United Kingdom of Great Britain and Northern Ireland':'英国',
 Russia:'俄罗斯','Russian Federation':'俄罗斯',USSR:'苏联','Soviet Union':'苏联',
 Poland:'波兰','Second Polish Republic':'波兰','Republic of Poland':'波兰',
 Belgium:'比利时','Kingdom of Belgium':'比利时',Norway:'挪威','Kingdom of Norway':'挪威',
 Denmark:'丹麦',Netherlands:'荷兰',Iran:'伊朗',Turkey:'土耳其',
 'Federal Republic of Germany':'德国（联邦）','German Federal Republic':'德国（联邦）',
 'Federated Republic of Germany':'德国（联邦）','West Germany':'德国（联邦）',
 'German Democratic Republic':'德国（民主）','East Germany':'德国（民主）',
 'Bogd Khanate of Mongolia':'蒙古国','Great Mongol State':'蒙古国',
 "Mongolian People's Republic":'蒙古国','Great Yuan':'大宛',
};
export function colorIdentity(name){
 const key=String(name||'').normalize('NFKC').trim().replace(/\s+/g,' ');
 return aliases[key]||colorGroups[key]||key;
}

