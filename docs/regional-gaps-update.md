# 苏格兰、爱尔兰、南也门与1944年意大利空白修复

核查日期：2026-10-31。修复源数据缺项、共主王国提前合并，以及同名大陆／岛屿记录互相遮蔽的问题。年度查询继续按有效时期选择轮廓，没有用平滑插值伪装年度测绘。

## 范围

- 苏格兰及北英格兰：1609—1706年恢复苏格兰单独的地域，1652—1659年为英联邦控制阶段。1603年为共主联合，1707年才按国家合并显示大不列颠。1641年纽卡斯尔补回英格兰地域，同时说明苏军占领和当年撤军；未复原逐日占领线。
- 爱尔兰：公元前500年至公元499年显示铁器时代诸部族，500—1168年显示盖尔诸国，1169—1602年显示盖尔诸领地。均是明确标注的地域集合，不是统一国家，未虚构共同国王或内部国界。保留源图已有北欧人城镇及单列伯国。英王实际控制部分自1177年单列爱尔兰领地，1541年起单列爱尔兰王国；1603年征服结束后的遗漏补入王国。修正1602年投降后仍延续到1608年的西班牙金塞尔据点。
- 南也门：1948—1969年同时保留大陆与索科特拉等历史GIS片段。亚丁殖民地与东、西保护地诸邦分列；1959年起注明部分诸邦逐渐组成联邦，1963年起反映亚丁加入后的分组，未声称全部诸邦同年入盟。1967年按独立后的年末状态显示南也门人民共和国，1970年才使用民主人民共和国名称。北也门及沙特、阿曼现有轮廓不被自动覆盖。
- 1944年意大利：恢复南部王国、罗马、那不勒斯、佛罗伦萨及岛屿等地区。北部为德国占领下的意大利社会共和国，德国东北部作战管理区另列并使用既有占领斜线。该年采用12月附近的概化代表状态；分界是哥特防线战区示意，不能理解为全年固定或战术级准确前线。

## 主要来源

页面核验还补出1944年邻近科西嘉的遗漏，归为法国解放地区，未错误并入意大利。依据：[法国国防部的科西嘉解放记录](https://www.defense.gouv.fr/80-ans-liberation-corse-recit-trois-actes)。

- [英国议会：1603年共主联合](https://www.parliament.uk/about/living-heritage/evolutionofparliament/legislativescrutiny/act-of-union-1707/overview/union-of-the-crowns/)、[1707年国家合并](https://commonslibrary.parliament.uk/research-briefings/cbp-10649/)
- [英国国家档案馆：苏格兰盟约派与内战](https://www.nationalarchives.gov.uk/education/resources/civil-war-people/civil-war-person-scottish-covenanter/)
- [都柏林大学图书馆：爱尔兰历史地图](https://libguides.ucd.ie/findingmaps/mapshistireland)、[爱尔兰文化遗产署：史前与铁器时代](https://heritageireland.ie/articles/mesolithic-iron-age-8000bc-400ad/)
- [爱尔兰王权法](https://www.legislation.gov.uk/aip/Hen8/33/1)、[爱尔兰国家图书馆：金塞尔投降协议手稿](https://catalogue.nli.ie/Record/MS_UR_004415)
- [英国国民陆军博物馆：亚丁](https://www.nam.ac.uk/explore/aden-emergency)、[英国议会1963年联邦记录](https://api.parliament.uk/historic-hansard/written-answers/1963/jul/02/federation)、[联合国1967年年鉴](https://digitallibrary.un.org/record/860183/files/1122896-EN.pdf)
- [新西兰文化与遗产部：意大利战役时间线](https://nzhistory.govt.nz/war/the-italian-campaign/timeline)、[美国大屠杀纪念馆：意大利及社会共和国](https://encyclopedia.ushmm.org/content/en/article/italy)、[德国占领意大利研究项目：作战管理区](https://www.ns-taeter-italien.org/en/glossary)

基础地域来自已打包Cliopatria历史GIS，Natural Earth只用于海岸与地理位置遮罩。爱尔兰集合未补造逐王国边界；亚丁分组不是逐邦精确测绘；意大利战线是明示的概化推断。各条目在地图档案中保留来源与限制。逐期记录见 `public/data/regional-gap-review.json`。

## 重建

在原时序、王朝、俄国内战、战后补绘及任期补录流程后运行：

```text
python -X utf8 scripts/repair_regional_gaps.py
node scripts/audit_postwar_archives.mjs
python -X utf8 scripts/audit_chronology.py
npm test
npm run build
```

首次阶段输入备份位于 `.local/regional-gap-review/original-shards/`。重复运行不累积记录。更换上游轮廓时须显式迁移备份；若重跑更早的战后补绘，须接着重跑本阶段，再生成审计与构建。

新增地区配色单独固定，盖尔诸领地、爱尔兰王权领地、亚丁各地域分组更名时不随年份重新着色，避免与相邻区域色彩过近。

回归检查覆盖各关键阶段、世纪分片交界、亚丁独立前后、意大利解放城市与德占区，以及以前的蒙古、法国、俄国和战后修复。

验证结果：`npm test` 66项通过；`npm run build` 完成。全球扫描55个分片、19,017条唯一时期记录、5,424个年度查询范围，结构错误0条；既有待核史实线索继续公开保留。
