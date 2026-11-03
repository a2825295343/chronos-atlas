# 1945—1955年战后地图与领导人补录

核查日期：2026-10-31。此轮针对用户指出的1950年前后空白和领导人缺项，覆盖当前地图在1945—1955年的有效记录，不冒称一套完整的全球历史行政档案。

## 地图补绘

- 利比亚：区分英国管理的的黎波里塔尼亚、昔兰尼加和法国管理的费赞；1949—1950年显示昔兰尼加埃米尔国。1951年按12月24日独立后的年末代表状态显示利比亚王国，并补足1952年的断档。
- 厄立特里亚：1952年9月以前为英国管理，1952年以后补入与埃塞俄比亚的联邦范围，并说明自治地位；不回填现代独立厄立特里亚。
- 英属索马里保护地、葡属帝汶、福克兰／马尔维纳斯群岛：分别显示保护、殖民／海外管理和争议领地的管理关系。群岛填色只表示当时实际管理。
- 苏联：补出反子午线另一侧楚科奇的漏绘地理部分，不以现代俄罗斯轮廓替换苏联。
- 加沙：1949—1955年标明埃及管理，不视作对主权归属作裁定；以色列只补原轮廓邻近的沿海小缝，保留周边已有控制区。
- 纠正1947年保加利亚仍称王国、战后匈牙利关联奥匈帝国、亚齐仍指旧苏丹国、将1948年巴勒斯坦民族群体直接当成统一国家等身份问题。

补绘使用Natural Earth地理遮罩，限定在有史料支持的地区与阶段，并扣除当年已存在的势力。利比亚内部管理区是按地理分区概化，不是逐年历史测绘；没有把湖面、干涸湖床和所有海岸差异自动分给邻国。逐条面积、来源与重叠检查见 `public/data/postwar-territory-review.json`。

## 任期与角色

本轮补充505条有起止年份的任期／管理机构记录，涉及85个政权实体、298个经身份核对的人物。年表只用作候选名单，国家归属依准确职务和人物P39任期；不会使用出生、去世日期作为在位年，也不会根据网页上临近的国家标题自动认定任职国家。君主、摄政、总统、总理、过渡机关分别标注；特殊历史角色另附逐项来源。

另纠正将当代总统兼任政府首脑的制度倒推到历史的错误：1950年土耳其与印度尼西亚分别显示当时总统与实际总理任期。

殖民地与管理区在缺少当地统治者记录时可明确引用管理方中央元首、政府首脑，并显示提示。这不等于已经补齐当地所有总督。乌拉圭、丹吉尔、柏林等集体或多国机构不虚构一位“总统”；新赫布里底显示英法两方中央元首；1948年巴勒斯坦地方势力明确不适用单一国家元首。

1950年当前地图的170条有效记录均有个人、集体机构或明确引用的中央任期，其中88条为本地政权／机构资料、82条引用管理方中央任期。1945—1955年每年的逐项字段检查、独立政府首脑缺项和图片状态见 `/postwar-archive.html` 及 `public/data/postwar-archive-audit.json`。字段存在不等于每项史实都经过专家逐条审定。

代表旗保留具体年代、用途和出处；补充昔兰尼加、也门王国与当时藏军的代表旗。后者标为军旗，不以旗帜裁定主权或国际承认。此轮及前几轮实际选用的历史人物图像均已取得本地有效图像；可能是后世画像或纪念像，不承诺同时代写生。

## 主要出处

- [联合国利比亚独立、权力移交文件](https://digitallibrary.un.org/record/704492/files/A_1949_Add-1-EN.pdf)
- [英国向联合国提交的厄立特里亚1950—1952年管理报告](https://digitallibrary.un.org/record/1643155/files/A_2233-EN.pdf)
- [英国1960年索马里兰独立法令](https://www.legislation.gov.uk/uksi/1960/1060/pdfs/uksi_19601060_en.pdf)
- [联合国关于领地管理安排的历史材料](https://www.un.org/unispal/document/auto-insert-179951/)
- [联合国巴勒斯坦问题时间表](https://www.un.org/unispal/timeline/)
- [乌拉圭1952年集体政府移交法](https://www.impo.com.uy/bases/leyes-originales/11789-1952/1)
- [法国总统府：樊尚·奥里奥尔](https://www.elysee.fr/vincent-auriol)、[勒内·科蒂](https://www.elysee.fr/rene-coty)
- [德国联邦选举官：历任联邦总统](https://www.bundeswahlleiterin.de/en/service/glossar/b/bundespraesident.html)
- [土耳其议会制度史](https://www.tbmm.gov.tr/history/)
- [印度尼西亚内阁档案](https://setkab.go.id/profil-kabinet/)、[纳席尔内阁](https://setkab.go.id/kabinet-moh-natsir/)
- [英国议会君主任期目录](https://api.parliament.uk/regnal-years/reigns)

其余个人任期与特殊机构来源保存在 `public/data/postwar-leadership-review.json`。人物、旗帜原图和作者许可分别保存在对应媒体索引。

## 重建与验证

在原时序、王朝和1918—1919年俄国修复流程之后依次运行：

```text
python -X utf8 scripts/repair_postwar_territories.py
python -X utf8 scripts/supplement_postwar_leadership.py
python -X utf8 scripts/historical_archive_media.py all
python -X utf8 scripts/repair_regional_gaps.py
node scripts/audit_postwar_archives.mjs
python -X utf8 scripts/audit_chronology.py
npm test
npm run build
```

首次备份为 `.local/postwar-review/territories-original.geojson`。与其他补绘流程相同，更换上游数据后须显式迁移备份，不能把旧备份当成新上游。领导人准备脚本使用缓存年表、候选身份及官方实体接口；任期补录可重复执行，不累积同一补录标记。

回归检查覆盖独立和移交年份、沿海漏绘、周边势力不被补绘覆盖、君主与政府首脑区分、同名消歧义页排除、集体元首、跨年边界以及旧有法国、蒙古和俄国修复。
