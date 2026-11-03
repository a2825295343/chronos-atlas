/** Map lettering uses geographic names; administrative explanations remain in
 * displayName, controller, sovereign and the archive's representation notes. */
const overrides={
 'German Empire':'德意志帝国',
 'Kingdom of Germany':'德意志王国',
 'Qatar Protectorate':'卡塔尔',
 'Control area - germany-soviet':'德国',
 'Control area - germany-british':'德国',
 'Control area - germany-french':'德国',
 'Control area - germany-american':'德国',
 'Control area - de-france-north':'法国',
 'Control area - de-france-full':'法国',
 'Control area - temporary-Q69808':'法国',
 'Eritrea in Federation with Ethiopia':'厄立特里亚',
 'Gajapati Kingdom':'奥里萨',
 'Tomara Delhi':'德里',
 'OETA East Arab Administration':'叙利亚',
 'OETA Western Military Administration':'黎巴嫩与叙利亚海岸',
};
export function mapName(properties,localize=name=>name){
 const p=properties||{};
 if(p.suppressPolityLabel)return '';
 if(p.mapLabel)return p.mapLabel;
 if(overrides[p.NAME])return overrides[p.NAME];
 const name=p.displayName||localize(p.NAME)||'';
 return name.replace(/\s*[（(][^()（）]*[）)]/gu,'').trim();
}

