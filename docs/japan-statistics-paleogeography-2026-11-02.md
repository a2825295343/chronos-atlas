# 日本、战争关联、历史地名与古地理修订

修订日期：2026-11-02。构建仍由 `npm run build` 生成，启动方式保持 `启动观澜.cmd`。

## 已修正的具体问题

- **1868—1869年日本空白**：以战前本土轮廓、旧国位置和戊辰战争年表补绘。区分明治新政府、1868年奥羽越列藩同盟及箱馆附近的虾夷旧幕府军／虾夷政权。范围为年度活动概览，不能作为逐日战线；没有把虾夷军对整个北海道的名义主张画成全岛实际控制。
- **日本具名统治者**：168条源任期、223条分政权／职务适用记录（含3条正式职位空缺说明），涉及160人。补录德川15代、足利15代的在职与复职阶段、镰仓9代将军及北条执权、538年以后可考帝系；幕府档案另列朝廷天皇。正式将军、任将军前的镰仓殿、执权与退任后主持幕政分别注明。交接年可有多人；空位不强行延长上一任。160人中155人已有带来源与许可信息的画像资源，其余保留具名任期。
- **幕末代表旗**：1854年起的日之丸船舶识别旗可以作为晚期幕府及1868—1869年日本的代表旗。界面明确说明所用图像沿用后来的定式，未声称当时已有1870年的法定尺寸。
- **战争关联**：外交页使用与战争总览相同的本年战争集合，按参战有效期、COW国家编号与政权名称变体关联，覆盖COW、UCDP及有出处的历史补录。越战可以从北越、南越、美国、韩国、澳大利亚、泰国等当年参战国进入。离开战争的国家不因曾经参战而一直显示。
- **越战参战方与任期补充**：按年份将COW的“Vietnam”和UCDP的“Vietnam (North Vietnam)”合并，避免同一北越军力出现两次；补入南方民族解放阵线，沿用同阵营并明确不重复累加兵力。补录8位南北越主要元首／总理的12条分期记录，并将老挝国际化阶段与同年的UCDP记录合并保留来源口径。
- **戊辰战争去重**：沿用COW `cow-intra-588`，附上核对后的说明与地区参战组织；保留原始阵营兵力／伤亡，地区组织不再重复累加成额外的国家军力。
- **越南所有权错误**：修正1967—1972年把南越地区当成美国领土的源记录，移除后来仍残留的美国几何。美国军事介入保留在战争档案。另移除1951年以后中华民国源多边形中残留的海南部分。
- **人口辖区**：中华民国1949年以后使用COW 713（台湾）而非710（中国）；1991年为20,557,000，来源按千人取整。世界银行缺少台湾该年数据时不会回退到中国大陆GDP或人口。苏联解体前后、南斯拉夫及德国统一过渡的统计也加上辖区保护；使用早年参考时显示实际观测年，不冒充所选年。
- **世界银行回溯口径**：德国统一前、越南统一前、巴基斯坦分裂前、苏丹／南苏丹分离前、埃塞俄比亚／厄立特里亚分离前、也门统一前及马来西亚包含新加坡的过渡阶段，不直接使用不相同辖区的现代经济体回溯值。可以匹配同年历史国家序列时使用该序列。

## 历史地块

新增382条分期分区／历史地理参考记录，覆盖35个现代国家范围、897个现代定位单元；包含1869—1871年日本旧国参考。另给170个已经成立／命名的近代分区补上可用起年，避免一律被1950或1959年的默认门槛屏蔽。

覆盖英国旧郡、德意志历史地域、伊比利亚旧区域、罗马时代区域、两河流域、伊朗、阿富汗、北欧、东欧、北非与部分撒哈拉以南非洲、东南亚及美洲等。已有更好的历史区划优先显示。纯历史地理参考不绘制未经核实的行政分界；点击可见年代、出处及定位方法。

**这些补录没有把全球所有现代省份变成精确古代省份。** 许多早期地方名称、行政层级和逐年边界仍缺乏可核定数据。不能仅为了消除空白，把后世行政名称倒填到史前。

## 古海岸线与沉没陆架

- 使用[Spratt与Lisiecki 2016古海平面序列（NOAA存档）](https://www.ncei.noaa.gov/access/paleo-search/study/19982)，年龄基准为1950年以前的千年。保留原始均值与不确定性，不人为将原始曲线改成想象中的年代值。
- 将项目已有的[Tilezen／AWS地形瓦片](https://registry.opendata.aws/terrain-tiles/)中的真实海底高程与海平面相交，生成16档岸线：−130米至0米，以及+5、+10米。千年海平面序列在年份间插值，岸线使用最近的高程切片。
- 前4000年以前启用古海岸线；同步改变陆地、海洋遮罩、海岸线与水波纹裁剪。现代湖泊、河流和夸张立体地形在该模式关闭。切换到较晚时期恢复现代底图。
- 补充多格兰、巽他陆架、萨胡尔及白令陆桥的人群活动参考；仅补低海面时出露的陆架。它们以考古／人群活动区展示，不能据此推定统一国家、共享君主、军队或国旗。
- 高程源支持约5公里、计算网格约10公里；简化与坐标压缩将GeoJSON总量从414.3 MB降为178.1 MB。古地理图层按高程切片缓存，年份变化不重复加载同一切片。

**精度边界**：海平面重建通常有约9—12米的一倍标准差；未完整求解局地沉降、冰川均衡调整、侵蚀淤积、冰盖范围与古河道。当前时间轴最早约12.5万年前，岸线可见变化主要由海平面控制；没有模拟板块旋转。[USGS对板块速度的说明](https://www.usgs.gov/faqs/how-fast-do-tectonic-plates-move)可供对照。此版本是有明确不确定性的古地理参考，不能称为精确逐年大陆模型。

## 核对入口与来源

- 日本任期：[宫内厅帝系图](https://www.kunaicho.go.jp/e-about/genealogy/pdf/keizu-e.pdf)、[江户东京博物馆](https://www.edo-tokyo-museum.or.jp/s-exhibition/house-of-tokugawa/)，各任期同时保留具名条目链接。
- 王政复古：[日本国立公文书馆](https://www.archives.go.jp/exhibition/digital/henbou/contents/01.html)。箱馆：[北斗市1868—1869年表](https://www.city.hokuto.hokkaido.jp/bunkazai/data/nen2-1.htm)。日之丸：[鹿儿岛县资料](https://www.pref.kagoshima.jp/aa02/pr/gaiyou/itiban/hatu/hinomaru.html)。
- 越战：[美国国务院史料说明](https://history.state.gov/milestones/1969-1976/ending-vietnam)、COW及UCDP原始战争记录。
- 近代区名：[美国人口普查局](https://www.census.gov/dataviz/visualizations/048/508.php)、[加拿大省与地区](https://www.canada.ca/en/intergovernmental-affairs/services/provinces-territories.html)、1833年西班牙省制法令等。各分区的独立来源保留在属性中。
- 多格兰：[考古数据服务研究框架](https://archaeologydataservice.ac.uk/researchframeworks/mesolithic/Wiki.jsp?page=Doggerland)；巽他：[印尼地质研究](https://ijog.geologi.esdm.go.id/index.php/IJOG/article/view/182)；萨胡尔：[澳大利亚国家博物馆](https://aws-digital-classroom.nma.gov.au/learning-modules/1/migration-sahul)；白令陆桥：[美国国家公园管理局](https://www.nps.gov/articles/bering.htm)。

## 可复现脚本

```text
python -X utf8 scripts/repair_boshin_transition.py
python -X utf8 scripts/complete_japanese_archives.py candidates
python -X utf8 scripts/complete_japanese_archives.py fetch
python -X utf8 scripts/complete_japanese_archives.py apply
python -X utf8 scripts/repair_vietnam_statistical_scope.py
python -X utf8 scripts/complete_vietnam_war_context.py
python -X utf8 scripts/expand_global_historical_regions.py
python -X utf8 scripts/prepare_established_region_names.py
python -X utf8 scripts/prepare_paleogeography.py
python -X utf8 scripts/historical_archive_media.py portraits
python -X utf8 scripts/audit_chronology.py
npm test
npm run build
```

古海平面原始文件缓存于 `.local/sea-level-spratt2016.txt`，公开下载地址为 NOAA 的 `paleocean/by_contributor/spratt2016/spratt2016-noaa.txt`。日本具名人物通过Wikidata明确条目与人类类型核对，不用人名模糊搜索自动认领。

数据补丁有独立备份与标记。`repair_boshin_transition.py`只重建18号分片（即1800—1899年），`repair_vietnam_statistical_scope.py`重建19、20号分片；后续再修改同一分片时，应先评估各脚本的备份重放顺序。

验证：117项自动化测试通过，生产构建通过；全分片审计结构错误为0。新增回归覆盖1991年中华民国人口、统计辖区隔离、越战按年关联、日本统治者分职、1868—1869年日本覆盖、南越美国领土误关联、分期历史区名及出露陆架。具体边界的史料精度仍受上述限制。
