# 全球档案与分期区划扩充

本批更新日期：2026-11-02。覆盖欧洲、亚洲、非洲和美洲的具体缺口，不表示全球所有历史信息已补齐。

## 已写入

- **204 条有界任职记录，197 位具名人物，14 个政权档案**；跳过 8 条已经存在的完全相同记录。包括早期英格兰、卡佩法兰西、葡萄牙、缅甸贡榜、大越李氏与陈氏、越南阮朝、阿散蒂、埃塞俄比亚、摩洛哥、巴西帝国与共和国、智利和阿根廷。
- **22 项历史战争或系列概览**：英格兰两次男爵战争、两阶段苏格兰独立战争、葡萄牙继承与复辟战争、法国宗教战争、英格兰内战、三十年战争、宋越战争、蒙古／元与大越战争、蓝山起义、郑阮战争、西山战争、清缅战争、三王之战、姆布维拉战役、美国及巴西独立战争。
- **10 项既有 COW 战争的中文详情**：英缅、英阿散蒂、英埃塞俄比亚、意埃、硝石战争、智利内战、西斯普拉丁战争等。保留原有统计时间范围，并解释正式宣战、持续抵抗与条约时间不同的情况。
- **106 条有年代的区划记录**：62 条按实际行政组合合并底图的分期区划、44 条历史名称与地理核心参考。法国 2016 年大区合并、印度 2000／2014／2019 年分邦、巴西分州及领地更名均可改变地块组合；另有越南阮朝省名、巴西帝国省名及英属缅甸分区名称。
- **38 条分期政体与宗教背景字段**，区分正式君主、共治、流亡主张、地方诸酋、法国保护下王权、巴西摄政制度和政教分离等情况。
- 本批名录中 **167 位人物已有可用且核对许可的肖像**。图像可能为照片、后世画像或纪念像，并明确说明；没有可靠人物图像时不借用同名者。

## 同步纠正的身份

- 1862 年后的阿根廷源条目改用“阿根廷共和国”及其总统档案，保留更早的邦联阶段。
- 1820—1885 年来源中笼统的 `Burma` 改接贡榜时期缅甸，地图使用“缅甸”，不再从现代国家档案取国王。前后同一势力颜色保持一致。
- 只调整上述身份和名称，保留源轮廓；没有借此扩大领土。

## 区划精度与时间口径

法国地区由原省级底图单元按法定大区组合合并；印度新邦、巴西部分分州按现有底图单元重组。显示的边线仍具有底图概化误差，并非地籍界址。

越南古省、巴西帝国及早期缅甸使用现代定位面合并的历史核心，不声称已经核定当年精确边界，设为 `geographicReference:true`、`boundaryVisible:false`。更具体的巴西省名会覆盖旧的宽泛定位名称，避免两层文字重叠。

巴西南马托格罗索按 1979 年行政运行分期，说明 1977 年立法设州；托坎廷斯按 1988 年宪法设州，注明首届政府 1989 年开始运行。法国 2016 年使用年末已确定名称，注明年初临时组合名称。年度君主交接可显示多位先后任职者，并非全年共治。

海尔·塞拉西在意大利占领期间标为“流亡皇帝及其主权主张”，不将其名义皇位等同本土实控。葡萄牙摄政危机与摩洛哥内战未以延长上一任任期来虚构连续统治。

## 生成及检查

在前序修补数据完成后执行：

```text
python -X utf8 scripts/expand_world_rosters.py fetch
python -X utf8 scripts/expand_world_rosters.py apply
python -X utf8 scripts/expand_world_context.py
python -X utf8 scripts/expand_world_regions.py
python -X utf8 scripts/expand_world_wars.py
python -X utf8 scripts/world_roster_media.py
python -X utf8 scripts/audit_chronology.py
npm test
npm run build
```

审计应在测试之前完成：测试会核对报告与当前分片的记录数。不要在审计仍写入时运行这项一致性检查。

定向测试覆盖真实人物、1883 年越南四次皇位交接、流亡身份、国家档案关联、参战年份、法国和印度区划变更、巴西新旧地块无重叠及历史参考几何限制。数据报告位于 `public/data/world-*-review.json`。

最终验证：146 项测试通过，生产构建通过。全局年代审计检查 5,424 次年份查询、55 个分片，结构错误为 0；仍保留 154 条身份年代线索及 53 对空间重叠供后续核查，不将结构检查等同全部史实已获确认。浏览器核对葡萄牙 1900 年国王肖像、法国 2015／2016 年区划变化及诺曼底地块详情；截图为 `world-roster-portugal-1900.png`、`world-regions-france-2015.png`、`world-regions-france-2016.png`。

## 主要来源

- [英格兰君主年表](https://en.wikipedia.org/wiki/List_of_English_monarchs)、[法兰西君主年表](https://en.wikipedia.org/wiki/List_of_French_monarchs)、[葡萄牙君主年表](https://en.wikipedia.org/wiki/List_of_Portuguese_monarchs)。具名人物逐一通过规范文章或精确重定向关联 Wikidata 人类实体，未使用模糊姓名匹配或生卒年推断任期。
- [越南阮朝](https://en.wikipedia.org/wiki/Nguy%E1%BB%85n_dynasty)、[缅甸贡榜](https://en.wikipedia.org/wiki/Konbaung_dynasty)、[阿散蒂君主](https://en.wikipedia.org/wiki/List_of_rulers_of_Asante)、[埃塞俄比亚皇帝](https://en.wikipedia.org/wiki/List_of_emperors_of_Ethiopia)。
- [智利国会图书馆：普列托总统](https://www.bcn.cl/historiapolitica/resenas_parlamentarias/wiki/Jos%C3%A9_Joaqu%C3%ADn_Prieto_Vial)、[阿根廷国家元首年表](https://en.wikipedia.org/wiki/List_of_heads_of_state_of_Argentina)。
- [英国遗产组织：第一次男爵战争](https://www.english-heritage.org.uk/sieges-of-dover)、[纽卡斯尔大学：英国内战](https://britishcivilwars.ncl.ac.uk/background/)、[法国新教博物馆：宗教战争](https://museeprotestant.org/notice/les-huit-guerres-de-religion-1562-1598/)、[美国国家档案馆：1783 年巴黎和约](https://www.archives.gov/milestone-documents/treaty-of-paris)。
- [英国国家陆军博物馆：缅甸战争年表](https://www.nam.ac.uk/explore/timeline-burma-army)、[阿比西尼亚远征](https://www.nam.ac.uk/explore/abyssinia)。其他战争分别保留具体出处。
- [法国 INSEE：2016 年大区改革](https://www.insee.fr/fr/statistiques/1906658?sommaire=1906743)、[印度政府：2000 年新邦](https://www.pib.gov.in/newsite/erelcontent.aspx?lang=2&reg=48&relid=18420)、[特伦甘纳政府](https://www.telangana.gov.in/About/State-Profile/)、[2019 年查谟和克什米尔重组法](https://www.indiacode.nic.in/indiacode/handle/123456789/12030?sam_handle=123456789%2F1362&view_type=search)。
- [巴西 IBGE：1872—2010 年区划演变](https://agenciadenoticias.ibge.gov.br/agencia-sala-de-imprensa/2013-agencia-de-noticias/releases/14147-asi-publicacao-aborda-evolucao-da-divisao-territorial-brasileira-de-1872-a-2010)、[越南档案部门：君主时期行政区划](https://archives.org.vn/gioi-thieu-tai-lieu-nghiep-vu/ky-i-dia-gioi-hanh-chinh-viet-nam-thoi-ky-quan-chu.htm)。
