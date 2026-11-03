# 年代交接、阿拉伯与秦汉地图修订

修订日期：2026-11-02。对应本轮连续反馈；不是全球历史资料已全部核定的声明。

## 地图与名称

- 移除 1956—1957 年匈牙利境内误连到奥匈帝国的记录和残留碎片；补接 1949 年匈牙利交接。奥地利与匈牙利保持分立。
- 海南 1950—1952 年按年末代表状态归中华人民共和国，1949 年仍保留中华民国记录。
- 1645—1647 年陕南缺口按抗清诸军及清军推进分期补接；1646 年东西部不同。边界为概化重建，不是逐月战线。
- 19 世纪阿拉伯的也门伊玛目名录改成具体政权名称；马斯喀特和阿曼的同一国家条目合并，实际独立的阿曼伊玛目国另列。
- 停战诸酋长国按可区分的酋长国拆列，增加英国保护关系。阿布扎比、迪拜等范围以现代定位面为参考，尚未精确复原各年的小飞地与卡尔巴等全部变化。
- 科威特、巴林及伊拉克、约旦、也门、沙特等过时的英国殖民标签按独立时间退出；保留实际保护关系和国家身份的区别。
- 1132—1240 年不再让统一的基辅罗斯大面覆盖已经分立的诸公国。尚不能细分的残余区域标为“罗斯诸地”，说明其为地域集合，不设置共同君主。
- 秦末现有分封记录逐个改成具体诸侯国身份；西楚不再误连“楚汉战争”，其他诸侯不再共用“项羽十八诸侯”的总目身份。按前 208—204 年政权变化退出现已被吞并的塞、翟等条目。没有为来源未提供的衡山国编造精确版图。
- 新朝原始记录误跨公元 6—29 年：6—8 年归西汉，9—22 年按新朝初期来源轮廓补接内地遗漏；23 年起区分更始汉、赤眉汉、东汉、成家、陇右及河西等势力。内地补绘保留匈奴、高句丽等已有势力，标注名义郡县范围与实控不一致的限制。
- 另清理瓦尔德克和皮尔蒙特、施瓦茨堡等残留人物名录式国家名称。

## 档案、战争与地块

- 新增或校订 66 条波斯、海湾及匈牙利等在位记录，另补秦末、新朝交接 35 条具名在位记录。来源有分歧或同年交接时保留说明，不把生卒年当作任期。
- 补入 16 场奥斯曼—波斯及明末战争/战役记录，另补新末起义和东汉统一战争 2 项。阶段冲突保留各自时间和参与方；没有资料的精确兵力不编造。
- 解放战争按年份关联国民政府、中国共产党/人民解放军及成立后的中华人民共和国；国民党战后兵力不再套用大陆数据。战争面板显示具体参与者名称。
- 匈牙利人民共和国按 1949—1989 年对应匈牙利统计身份，恢复 1956 年已有战争记录及当年人口序列的关联。
- 新增 39 条有年代的中国、奥斯曼和波斯分区参考；清代广西改为“广西省”，1958—1964 年使用“广西僮族自治区”，海南等地按时期换名。
- 这些新分区多为现代定位面合并的历史名称参考，设置 `boundaryVisible:false` 并说明几何限制，不将其宣传成核定的历史省界。

## 可重复生成

保留 `.local` 中各阶段原始分片备份。较早的修补阶段使用自己的快照，不能在新阶段后随意重跑覆盖；重建应按顺序执行：

```text
python scripts/repair_successions_gulf_rus.py
python scripts/complete_persia_gulf_archives.py fetch
python scripts/complete_persia_gulf_archives.py apply
python scripts/refine_qing_persia_regions.py
python scripts/supplement_persian_ming_wars.py
python scripts/repair_qin_xin_transition.py
python scripts/finalize_qin_xin_context.py
python scripts/finalize_polity_headings.py
python scripts/historical_archive_media.py portraits
node scripts/audit_postwar_archives.mjs
python scripts/audit_chronology.py
npm test
npm run build
```

## 验证

- 全项目测试：138 项通过，0 项失败。定向测试覆盖上述年度交接、陆地点归属、错误实体退出、战争双方、统治者和地名年代。
- 生产构建通过。浏览器实际核对新朝公元 16 年腹地与王莽档案、前 206 年西楚与项羽档案，以及 1956 年匈牙利旗帜、政府首脑交接、991.1 万人口和 1 项合并后的战争记录。
- 全局年代结构审计：5,424 次年份查询，结构错误 0；仍有 156 项身份元数据线索、53 对空间重叠待进一步历史核查。这不是所有边界都已准确的证明。
- 截图：`xin-territory-16-reviewed.png`、`qin-chu-206-reviewed.png`。

## 主要核对来源

- [《史记》卷七：项羽本纪](https://zh.wikisource.org/wiki/史記/卷007)、[卷八：高祖本纪](https://zh.wikisource.org/wiki/史記/卷008)。
- [《汉书》王莽传下](https://zh.wikisource.org/wiki/漢書/卷099下)、[《后汉书》光武帝纪上](https://zh.wikisource.org/wiki/後漢書/卷1上)。
- [《清史稿》卷二百十五](https://zh.wikisource.org/wiki/清史稿/卷215)：汉中、兴安与陕南抗清活动。
- [联合国 1957 年匈牙利特别委员会报告](https://digitallibrary.un.org/record/712474)。
- [阿联酋政府历史概述](https://u.ae/en/about-the-uae/History)、[科威特政府统治者资料](https://e.gov.kw/sites/kgoenglish/Pages/Visitors/AboutKuwait/GoverningBodyOverView.aspx)、[美国国务院巴林独立与承认记录](https://history.state.gov/countries/bahrain)。
- [Encyclopaedia Iranica：萨法维](https://www.iranicaonline.org/articles/safavids/)、[赞德](https://www.iranicaonline.org/articles/zand-dynasty/)、[阿夫沙尔与赞德时期奥斯曼—波斯关系](https://www.iranicaonline.org/articles/ottoman-persian-relations-ii-afsharid-and-zand-periods/)。
- [Ashmolean：奥斯曼—萨法维战争分期](https://islamicceramics.ashmolean.org/Iznik/safdwar.htm)。
- [加拿大乌克兰研究所：基辅罗斯](https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5CK%5CY%5CKyivanRushDA.htm)。

具体人物、图像许可、战争与分区出处分别保留在各数据条目的 `source`、`sources`、`commons` 或修订报告中。
