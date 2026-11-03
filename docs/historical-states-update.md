# 王朝、国家与联合关系修订（2026-10-31）

地图显示领土归属；统治家族、政治联合与共同君主分别记入档案和有年代的外交关系。名称中有“联盟”不意味着统一国家，也不能据名称自动拆分一切联合实体。

## 本次修订

- 卡尔马联盟、丹麦—挪威和瑞典—挪威拆为各自时期的丹麦、挪威、瑞典领土。卡尔马联盟的政治框架与实际共主关系分开记录。瑞典在摄政阶段不被强行赋予丹麦君主；1814年之后的冰岛不误分给挪威。
- 雅盖洛家族统治区在1569年之前区分波兰王冠领与立陶宛大公国，分别查阅君主；1569年成立的波兰立陶宛联邦保留为条约建立的复合国家。
- 哈布斯堡统治区区分奥地利世袭领地、波希米亚、匈牙利、尼德兰及勃艮第等。缺乏可靠内界的诸领地明确标为集合，不冒充一个正式统一国家。其他13类 `House of ...` 家族名称按当地领地或明确的领地集合改写。
- 共同君主关系由两个王位上同一个人的有效任期相交生成。婚姻、政治联合、共同君主分别标注；年度视图可能同时显示年内先后即位者。
- 补录教皇国755—1870年的正式教宗任期或完整年度空位；补充奥地利、波兰、立陶宛、匈牙利、波希米亚、神圣罗马帝国、尼德兰、北欧及马穆鲁克等档案。各项任期保留具体角色和出处，不以家族成员身份推定任职。
- 新增72条有年代的关系记录。补选342个人物的本地画像、纪念像或照片；并非每幅均为同时代肖像。没有可靠画像的人物仍保留文字档案。
- 奥斯曼1844年之前提供分期代表旗：早期白色王旗、祖勒菲卡尔军旗、1721年图像中的军旗和早期星月旗类型。说明明确区分史料复原、代表性选择与已知统一旗制，显示窗口不冒充确切采用日期。
- 新增15项战争／战役专题，包括两次奥斯曼—马穆鲁克战争、1453年君士坦丁堡、查尔迪兰、罗得岛、马耳他、塞浦路斯—勒班陀、长期土耳其战争、大土耳其战争、尼德兰起义与欧洲继承战争等。国家外交页可进入当年相关战争的交战双方、统帅、战役、原因及结果。兵力数字不足时保留定性比较与资料限制，不编造精确数字。
- 1516年末地图反映叙利亚与黎凡特被奥斯曼征服，1517年末反映埃及并入；同年战争列表仍可包含年内消失的马穆鲁克国家。

## 主要史料

- [梵蒂冈历任教宗官方目录](https://www.vatican.va/content/vatican/en/holy-father.html)
- [哈布斯堡历史：马克西米利安一世的领地](https://www.habsburger.net/en/chapter/reuniting-habsburg-lands-maximilian-i)
- [牛津大学雅盖洛研究年表](https://jagiellonians.site.ox.ac.uk/jagiellonians-timeline)
- [奥斯陆大学：1397年联盟文书](https://www.norgeshistorie.no/kilder/senmiddelalder/K1011-Unionsbrev.html)
- [卡尔马省博物馆：联盟战争](https://medeltiden.kalmarlansmuseum.se/en/society/the-kalmar-union/the-union-wars/)
- [挪威王室：1814—1905年宪法与联合](https://www.kongehuset.no/historie/grunnlov-og-union-1814-1905)
- [丹麦王室历代君主](https://www.kongehuset.dk/en/the-monarchy-in-denmark/the-royal-lineage)
- [土耳其伊斯兰百科全书：旗帜](https://islamansiklopedisi.org.tr/bayrak)
- [FIAV：奥斯曼军旗研究](https://fiav.org/wp-content/uploads/2021/05/17-31-Martykan-HistoryOfOttomanMilitaryFlags.pdf)
- [阿什莫林博物馆：1516—1517年征服](https://islamicceramics.ashmolean.org/Iznik/conquest.htm)

逐项来源、任期与限定说明另保存在旗帜、人物、关系及战争记录里。

## 精度与复核

历史地图的外部疆界沿用所选时期的历史GIS。卡尔马、雅盖洛和哈布斯堡内部拆分使用独立王国的历史轮廓作掩膜；北欧后期改用后期王国轮廓。1516年的征服区也使用地理遮罩概化。它们是明确标注方法的重建，尚非每一年精确实测边界，不能据新增分期宣称所有历史数据补齐。

全球审计覆盖55个分片、18,548条去重有效期记录、5,424次年度查询；结构错误为0，另保留163项年代关联线索与57组空间重叠线索待审。现代2024、2026年的既有187个国家记录均保留旗帜和元首信息；2026年仍有18条任期时效需进一步核定，不能把字段存在等同于全部史实已确证。

验证命令：`npm test`（53项通过）、`npm run build`。回归包括联盟成员边界、1500年波兰与立陶宛不同君主、瑞典退出共主阶段、教皇空位、法国王旗、1516/1517年征服与战争参与者。

## 后续数据维护

依次执行：

```text
python -X utf8 scripts/refine_dynastic_states.py
python -X utf8 scripts/repair_russian_civil_war_gap.py
python -X utf8 scripts/supplement_historical_rulers.py
python -X utf8 scripts/supplement_dynastic_relations.py
python -X utf8 scripts/merge_historical_wars.py
python -X utf8 scripts/historical_archive_media.py all
python -X utf8 scripts/audit_chronology.py
node scripts/audit_modern_archives.mjs
npm test
npm run build
```

首次原始数据准备需要 `.local/historical-review-2026-10-31/` 内的官方教宗目录、各国君主表及人工复核候选清单；`fetch_historical_rulers.py` 负责解析这些已准备的候选名称并获取实体、具体职位资料。不要把出生／死亡日期列当成在位年。

`refine_dynastic_states.py` 从 `.local/dynasty-originals/` 重建，备份对应已完成时序修订的版本；如果重建上游资料，须显式迁移这些备份，再运行本轮处理，不可混用旧备份和新上游。补录脚本只替换自身标记的数据，避免反复执行累积关系和任期。
