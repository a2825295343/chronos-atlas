# 中国古代档案、中亚名称与碎片修订

## 本轮范围

- 1856年华北缺项：以1855、1857年清朝轮廓共同覆盖区限定，只补空白，保留太平天国及其他已有控制方。说明区分行政归属概览、捻军袭扰与持续实控。
- 18—19世纪美洲：1693条有日期的规则小块位置记录转为据点参考；41716处现代地理切分残片并回同一原始图源、同一时期的地区。没有按面积全局删除岛屿、飞地或原住民地域；每组处理都校验除已单列参考符号外无不明面积增减。
- 中亚：东、西喀喇汗国分别建档、命名和固定配色。16世纪塔里木地区改按叶尔羌汗国、吐鲁番核心及天山地方诸部分列，不将三个地域套用同一蒙兀儿斯坦档案。吐鲁番分界采用明确标注的地理核心概化，并非独立测绘的国界。
- 中国古代：导入649条具名在位记录，涉及74个政权；325位人物经Q5实体核对。未解析真实人物编号的具名君主使用本地资料ID，不伪造Wikidata编号。不用出生、去世栏推算任期。
- 战争：新增40条中国古代战争、战事与战役，保留各自有效年份；内战军政集团不提前标成后来的国家。修复北宋、南宋和金朝与原战争名的匹配。战役库不是所有古代战争的穷尽目录，没有同口径依据的兵力仍留待核定。
- 外交：时期集合不再成为上级政权；周王室礼制名分、会盟、和约、军事同盟分别说明。葵丘会盟不把未赴会的晋献公列为参与方；辽宋和约不说成共同防御同盟。
- 交互：省份轮廓高亮由当前选择状态同步；选中国家、地点、据点等其他对象后清空省份高亮。

## 来源与精度

- [教育部中国历代帝王年表](https://dict.revised.moe.edu.tw/appendix.jsp?ID=2&ver=5)：对照官方年表；有些先秦纪年、即位元年及传统朝代统计口径不同，不机械抹平。
- [专门君主名录](https://en.wikipedia.org/wiki/List_of_Chinese_monarchs)及各先秦国家的具名名录：只解析在位栏及明确的君主序列，源HTML与校验值保留。
- [《史记》周本纪](https://ctext.org/shiji/zhou-ben-ji/zhs)、[晋世家](https://ctext.org/shiji/jin-shi-jia/zhs)、[白起王翦列传](https://ctext.org/shiji/bai-qi-wang-jian-lie-zhuan/zhs)：战争与名分关系的史料参照。
- [喀喇汗王朝研究](https://www.iranicaonline.org/articles/qarakhanid/)、[叶尔羌](https://www.iranicaonline.org/articles/yarkand/)、[《拉失德史》](https://en.wikisource.org/wiki/Page:The_Tarikh-i-Rashidi_-_Mirza_Muhammad_Haidar,_Dughl%C3%A1t_-_tr._Edward_D._Ross_(1895).djvu/129)：区分分支与地域社群。
- [加拿大毛皮贸易站地图](https://open.canada.ca/data/en/dataset/96e248e8-f422-5d69-a085-cce12b04e11a)：据点和连续领土不能混为一谈。规则小块的符号识别属形状与地域辅助推断，具体站名、营业日期不凭形状杜撰。
- [Cliopatria](https://github.com/Seshat-Global-History-Databank/cliopatria)：原图与有效期保留为来源；逐年查询不代表每年都有独立边界测绘。灰色仍表示未关联可靠轮廓，不等于无人居住或没有政治组织。

## 重建顺序

`repair_qing_1856_and_american_fragments.py` → `repair_central_asian_identities.py` → `supplement_chinese_archives.py candidates/fetch/apply` → `supplement_chinese_wars.py` → `merge_historical_wars.py` → 历史肖像更新 → 时序审计 → 测试与生产构建。

前两个脚本各有首次输入备份；上游重跑会恢复其首次输入，必须重放后续步骤。图片保留人物实体、来源与许可；没有可靠肖像的君主不使用随意生成的人像。

## 最终验证与后续发现（2026-11-02）

110项测试通过，生产构建通过。已在实际页面确认：前462年晋国显示晋出公、首都新田，外交页不再把时期集合当宗主国；点击省份后缩小改选唐朝，省份高亮消失；1823年加拿大西部规则小块改为可点击的据点参考。

最后核验还发现英属殖民地的宗主国名称随年份变化、档案编号却仍固定为现代英国，导致1823年误用只有结束日期的乔治五世记录。现在宗主国编号也按时期切换，缺少起年且没有明确单年证据的领导人记录不会向全部早期年份展开。乔治五世的起年按[王室官方名录](https://www.royal.uk/george-v)补为1910年；1823年殖民地使用[乔治四世1820—1830年的档案](https://www.royal.uk/george-iv)。可用`repair_british_colonial_leadership.py`重放此项日期补正。

页面截图：`chinese-archive-jin-462.png`、`province-highlight-before.png`、`province-highlight-cleared.png`、`america-sites-1823.png`。
