# 德国名称、卡塔尔与阿曼身份、全球档案分期补充

本轮不是全球全部历史事实的穷尽核验。以下列出已落实内容、依据与边界。

## 国家名称与地理身份

- `German Empire` 在原始时期记录、中文本地化和地图文字中统一显示“德意志帝国”。`Kingdom of Germany` 保持“德意志王国”，德意志邦联、北德意志邦联保留各自名称，未将共和国套上君主制国名。
- 1947—1955年源数据的 `Qatar Protectorate / Q944391` 实际套用了阿曼轮廓，Q944391又是“卡塔尔历史”主题条目。已在卡塔尔半岛建立 `local:qatar-protectorate`，恢复本地统治者及英国保护关系；1971年交接按年内说明，1972年起采用独立卡塔尔身份。
- 清除“英属卡塔尔”和“英属阿曼”的残留殖民地分割。阿曼沿海与南部为马斯喀特苏丹国，1947—1955年内陆核心另列阿曼伊玛目国。英国影响及军事介入不等于直接殖民统治。
- 阿曼内陆采用1913年已有来源轮廓作概化定位，外沿参照现代地理；未宣称是每年精确实控界。1957—1959年的绿山军事控制线尚未精细补绘。
- 伊玛目国使用 `local:oman-imamate-1913`，避免将“Oman proper”历史地理区域本身当作国家。
- 卡塔尔新增1936—1949、1949—1971两种有许可信息的历史旗帜，不再只回退到英国代表旗。

主要依据：

- https://www.dhm.de/en/exhibitions/permanent-exhibition/the-german-empire-and-the-first-world-war/
- https://diwan.gov.qa/en/About-Qatar/History-of-Qatar
- https://qdl.qa/en/keeping-lion-bay-anglo-qatar-treaty-1916
- https://www.qatar.qa/en/qatar/al-adaam/
- https://www.qdl.qa/en/financial-troubles-said-bin-taimur
- https://www.rafmuseum.org.uk/research/online-exhibitions/an-enduring-relationship-a-history/oman-and-the-cold-war/

## 新增档案

- 109条具名任期，102人，11个档案身份：高丽、朝鲜王国、吞武里、拉达那哥欣、桑海、伊默里纳、夏威夷、卡塔尔及其保护关系时期、阿曼伊玛目国、查谟和克什米尔土邦。
- 核对了高丽918—1392年、朝鲜1392—1897年的每年君主覆盖，复位分开记载，交接年允许先后多名。
- 100人的身份经精确条目和人物类型核对；两名阿曼伊玛目采用有原始档案及学术来源的本地人物身份。排除了同名但1734年已去世的穆罕默德·哈利利，不借用他人的肖像。
- 肖像处理共新增41个人物的可用媒体匹配；没有可靠图像者仍明确显示待补。
- 9项新增战争：高丽—契丹、壬辰、1627后金侵朝、1636—1637清侵朝、1765—1767缅暹、1785—1786缅暹、海地革命、新西兰北方战争、阿曼内战与绿山战争。另补充1879英祖战争的原因、结果与将领。
- 战争按阶段列出参战者并关联外交；海地革命中法国立场发生变化，未固定全期在同一阵营。绿山战争在1957年与UCDP合并，在其他有来源的阶段单独显示，1956年不自动连成连续战争。
- 本轮不虚构可比较的精确兵力。桑海1582—1588年的几次交接等仍有缺项，未自动延长前任任期。

来源包括韩国国史编纂委员会《高丽史》与《朝鲜王朝实录》、泰国驻外机构历史资料、美国国家公园管理局、美国国务院历史办公室、英国皇家空军博物馆、新西兰文化遗产机构、卡塔尔埃米尔办公室及各条记录保留的人物与学术出处。

## 动态地名

新增66条分期地理单元，覆盖朝鲜半岛、新西兰、马达加斯加、马里、阿曼、卡塔尔。

- 朝鲜八道、咸吉／永安／咸镜名称变动、1896年十三道分拆；1895年明确标为府制时期的旧域地理参照，没有伪造23府精确界线。
- 新西兰1853年六省及其后霍克斯湾、马尔堡、南地、韦斯特兰等分合；新普利茅斯／塔拉纳基更名和1876年制度终止。
- 非洲及海湾增加有时代依据的历史地理区名称。

这些单元由现代定位地块合并，**不是当年精确行政界**。设置 `geographicReference:true`、`boundaryVisible:false`，不把未经核实的界线画成历史行政边界。已有较好的历史边界优先。

## 验证与重建

- `node --test tests/gulf-global-nov02.test.mjs`：国家名称、1947—1955年城市归属、独立后殖民残片、当地君主、逐年君主覆盖、肖像文件、战争阶段及外交关联、分区改革。
- `npm test`：128项通过。
- `npm run build`：通过。
- 全球时序结构扫描：55个分片，5424个年度查询，结构错误0。仍公开保留157条元数据核查线索、54组空间重叠线索；这些结果不等于逐条史学审定。

本轮数据重建顺序：

```text
python scripts/repair_qatar_oman_identity.py
python scripts/complete_global_reigns_nov02.py fetch
python scripts/complete_global_reigns_nov02.py apply
python scripts/complete_gulf_context_nov02.py
python scripts/expand_dated_regions_nov02.py
python scripts/supplement_global_wars_nov02.py
python scripts/historical_archive_media.py portraits
node scripts/audit_postwar_archives.mjs
python scripts/audit_chronology.py
npm test
npm run build
```

地理修复脚本从本轮独立备份读取19、20世纪原始分片；之后若有新的同世纪修改，应按修改时间顺序重放，避免旧备份覆盖新工作。
