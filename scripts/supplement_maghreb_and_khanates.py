"""Dated historical archive additions keyed to the atlas's political entities."""
from collections import Counter
from territory_repair_stage import read, write

TAG = 'maghreb-and-eurasian-reigns'
BOOK = 'https://erenow.org/postclassical/new-islamic-dynasties-chronological-genealogical-manual/'
SAADI = 'https://ghayb.com/wp-content/uploads/2021/03/The_New_Cambridge_History_Of_Islam_Volum-2.pdf'
CHAG = 'https://www.iranicaonline.org/articles/chaghatayid-dynasty/'
CENTRAL = 'https://www.iranicaonline.org/articles/central-asia-v/'
ATWOOD = 'https://turkistanilibrary.com/sites/default/files/encyclopedia_of_mongolia_and_the_mongol.pdf'
facts = read('public/data/polity-facts.json')
entities = facts['entities']
counts = Counter()


def cite(source):
    return BOOK + str(source) + '.php' if isinstance(source, int) else source


def fact(q, field, label, start, end, source, **extra):
    fields = entities[q]['fields']
    row = dict(value=label, label=label, citation=[cite(source)], at=None,
               supplement=TAG, **{'from': start, 'to': end}, **extra)
    fields.setdefault(field, []).append(row)
    counts[field] += 1


def ruler(q, label, start, end, source, role, approximate=False):
    fact(q, 'ruler', label, start, end, source, roleLabel=role, approximate=approximate)


def chain(q, source, role, end, terms, approximate=False):
    rows = [(int(year), name) for year, name in
            (part.split(' ', 1) for part in terms.split('|'))]
    for i, (start, name) in enumerate(rows):
        stop = rows[i + 1][0] if i + 1 < len(rows) else end
        ruler(q, name, start, stop, source, role, approximate)


def maghreb():
    s = '苏丹'
    chain('Q582861', 17, s, 1465, '1244 阿布·叶海亚·阿布·伯克尔|1258 阿布·优素福·雅库布|1286 阿布·雅库布·优素福|1307 阿布·萨比特·阿米尔|1308 阿布·拉比·苏莱曼|1310 阿布·赛义德·奥斯曼二世|1331 阿布·哈桑·阿里|1348 阿布·伊南·法里斯|1358 穆罕默德二世|1358 阿布·伯克尔|1359 阿布·萨利姆·易卜拉欣|1361 塔舒芬|1362 穆罕默德二世|1366 阿卜杜勒·阿齐兹一世|1372 穆罕默德三世|1373 艾哈迈德一世|1384 穆萨|1386 穆罕默德四世|1386 穆罕默德五世|1387 艾哈迈德二世|1393 阿卜杜勒·阿齐兹二世|1397 阿卜杜拉|1398 奥斯曼三世|1420 阿卜杜勒·哈克二世')
    ruler('Q582861', '阿布·扎卡里亚·叶海亚·瓦塔斯', 1420, 1448, 17, '瓦塔斯家族摄政，马林苏丹仍在位')
    chain('Q307697', 18, '特莱姆森苏丹', 1337, '1236 亚格穆拉桑|1283 奥斯曼一世|1304 穆罕默德一世|1308 阿布·哈穆·穆萨一世|1318 阿布·塔舒芬一世')
    chain('Q307697', 18, '特莱姆森苏丹', 1543, '1359 阿布·哈穆·穆萨二世|1389 阿卜杜勒·拉赫曼二世|1394 优素福一世|1394 优素福二世|1395 穆罕默德二世|1400 阿卜杜拉一世|1402 穆罕默德三世|1411 阿卜杜勒·拉赫曼三世|1411 赛义德|1411 阿卜杜勒·瓦希德|1424 穆罕默德四世|1428 阿卜杜勒·瓦希德|1430 艾哈迈德一世|1462 穆罕默德五世|1469 阿布·塔舒芬|1469 穆罕默德六世|1504 穆罕默德七世|1517 穆萨三世|1528 阿卜杜拉二世|1540 穆罕默德八世|1541 艾哈迈德二世')
    chain('Q307697', 18, '特莱姆森苏丹', 1555, '1544 艾哈迈德二世|1550 哈桑')
    chain('Q752662', 19, '哈夫斯君主', 1347, '1229 阿布·扎卡里亚·叶海亚一世|1249 穆罕默德一世·穆斯坦西尔|1277 叶海亚二世|1279 易卜拉欣一世|1284 奥马尔一世|1295 穆罕默德二世|1309 阿布·伯克尔一世|1309 哈立德一世|1311 扎卡里亚一世|1317 穆罕默德三世|1318 阿布·伯克尔二世|1346 奥马尔二世')
    ruler('Q752662', '艾哈迈德·伊本·阿比·乌马拉', 1282, 1284, 19, '争位者，曾控制突尼斯')
    chain('Q752662', 19, '哈夫斯君主', 1357, '1350 艾哈迈德一世|1350 易卜拉欣二世')
    chain('Q752662', 19, '哈夫斯君主', 1534, '1358 易卜拉欣二世|1369 哈立德二世|1370 艾哈迈德二世|1394 阿布·法里斯·阿卜杜勒·阿齐兹|1434 穆罕默德四世|1435 奥斯曼|1488 叶海亚四世|1489 阿卜杜勒·穆明|1490 扎卡里亚二世|1494 穆罕默德五世|1526 哈桑')
    chain('Q752662', 19, '哈夫斯君主', 1569, '1535 哈桑|1543 艾哈迈德三世')
    ruler('Q752662', '穆罕默德六世', 1573, 1574, 19, '末代君主')
    chain('Q970799', 20, s, 1549, '1472 穆罕默德·谢赫|1504 穆罕默德·布尔图卡利|1526 阿布·阿拔斯·艾哈迈德|1545 穆罕默德·卡斯里|1547 阿布·阿拔斯·艾哈迈德')
    ruler('Q970799', '阿布·哈孙', 1554, 1554, 20, '短期复位的瓦塔斯苏丹')
    chain('Q1136188', SAADI, '萨阿德君主', 1603, '1510 穆罕默德·卡伊姆|1517 艾哈迈德·阿拉吉|1544 穆罕默德·谢赫|1557 阿卜杜拉·加利卜|1574 穆罕默德·穆塔瓦基勒|1576 阿卜杜勒·马利克|1578 艾哈迈德·曼苏尔')
    ruler('Q1136188', '穆罕默德·谢赫', 1524, 1544, SAADI, '塔鲁丹特支系领袖，与马拉喀什汗廷并立')
    for name, start, end, role in [
        ('宰丹·纳西尔',1608,1612,'马拉喀什苏丹'), ('宰丹·纳西尔',1613,1627,'马拉喀什苏丹'),
        ('阿卜杜拉·伊本·穆罕默德',1613,1624,'非斯支系苏丹'),
        ('阿卜杜勒·马利克二世',1627,1631,'马拉喀什苏丹'),
        ('瓦利德',1631,1636,'马拉喀什苏丹'), ('穆罕默德·谢赫·萨吉尔',1636,1655,'马拉喀什苏丹'),
        ('艾哈迈德·阿拔斯',1655,1659,'马拉喀什末代萨阿德苏丹')]:
        ruler('Q1136188', name, start, end, SAADI, role)
    chain('Q205718', 14, '齐里德君主', 1148, '972 布卢金一世|984 曼苏尔|996 巴迪斯|1016 穆伊兹|1062 塔米姆|1108 叶海亚|1116 阿里|1121 哈桑')
    chain('Q588672', 14, '哈马德君主', 1152, '1015 哈马德|1028 卡伊德|1054 穆赫辛|1055 布卢金二世|1062 纳西尔|1088 曼苏尔|1105 巴迪斯|1105 阿齐兹|1124 叶海亚', True)
    chain('Q75613', 15, '穆拉比特埃米尔', 1147, '1061 优素福·伊本·塔什芬|1107 阿里·伊本·优素福|1142 塔什芬·伊本·阿里|1146 易卜拉欣|1146 伊斯哈格', True)
    chain('Q199688', 16, '穆瓦希德哈里发', 1269, '1130 阿卜杜勒·穆明|1163 优素福一世|1184 雅库布·曼苏尔|1199 穆罕默德·纳西尔|1213 优素福二世|1224 阿卜杜勒·瓦希德一世|1224 阿卜杜拉·阿迪勒|1227 伊德里斯·马蒙|1232 阿卜杜勒·瓦希德·拉希德|1242 阿里|1248 奥马尔|1266 伊德里斯')
    ruler('Q199688', '叶海亚·穆塔西姆', 1227, 1235, 16, '马拉喀什争位者')
    chain('Q207600', 12, '阿格拉布埃米尔', 909, '800 易卜拉欣一世|812 阿卜杜拉一世|817 齐亚达特·阿拉一世|838 阿格拉布|841 穆罕默德一世|856 艾哈迈德|863 齐亚达特·阿拉二世|863 穆罕默德二世|875 易卜拉欣二世|902 阿卜杜拉二世|903 齐亚达特·阿拉三世')
    chain('Q940123', 10, '伊巴德派伊玛目', 909, '778 阿卜杜勒·拉赫曼·伊本·鲁斯塔姆|788 阿卜杜勒·瓦哈卜|824 阿弗拉赫|872 阿布·伯克尔|874 穆罕默德|894 优素福|895 雅库布|899 优素福|907 亚格赞', True)
    for q, start, end, source, capital, government in [
        ('Q582861',1269,1465,17,'非斯','马林家族世袭苏丹国'),
        ('Q307697',1236,1555,18,'特莱姆森','扎亚尼德家族世袭苏丹国'),
        ('Q752662',1229,1574,19,'突尼斯','哈夫斯家族世袭君主国'),
        ('Q970799',1472,1549,20,'非斯','瓦塔斯家族世袭苏丹国'),
        ('Q1136188',1524,1603,SAADI,'马拉喀什','谢里夫王族统治的苏丹国'),
        ('Q940123',778,909,10,'塔赫特','伊巴德派伊玛目政权')]:
        fact(q,'capital',capital,start,end,source)
        fact(q,'government',government,start,end,source)
    fact('Q940123','religion','伊巴德派伊斯兰教',778,909,10)


def khanates():
    chain('Q4332415', ATWOOD, '瓦剌联盟首领／太师', 1452, '1409 马哈木|1418 脱欢|1438 也先', True)
    ruler('Q4332415', '也先', 1452, 1453, ATWOOD, '瓦剌实际领袖')
    ruler('Q4332415', '也先', 1453, 1454, ATWOOD, '称汗')
    chain('Q79965', 135, '术赤系汗', 1359, '1242 拔都|1255 撒里答|1256 兀剌黑赤|1257 别儿哥|1266 忙哥帖木儿|1280 脱脱蒙哥|1287 秃剌不花|1291 脱脱|1312 月即别|1341 田尼别|1342 札尼别|1357 别儿迪别', True)
    chain('Q79965', 135, '术赤系汗', 1410, '1380 脱脱迷失|1395 帖木儿·忽都鲁|1399 沙迪别|1407 不剌', True)
    ruler('Q79965','库楚克·穆罕默德',1435,1459,135,'金帐汗国后期汗，诸支同时并立',True)
    ruler('Q79965','赛义德·艾哈迈德一世',1433,1455,135,'西部术赤系争位者，与其他汗廷并立',True)
    ruler('Q79965','阿赫马德汗',1465,1481,135,'大帐汗',True)
    chain('Q487829', 133, '察合台系汗', 1326, '1227 察合台|1244 哈剌旭烈兀|1246 也速蒙哥|1251 哈剌旭烈兀|1252 兀鲁忽乃|1260 阿鲁忽|1266 木八剌沙|1266 八剌|1271 聂古伯|1272 不花帖木儿|1282 都哇|1306 宽阇|1308 塔里忽|1309 怯别|1309 也先不花一世|1318 怯别', True)
    for name, a, b in [('塔儿麻失里',1331,1334),('也孙帖木儿',1338,1342),('合赞算端',1343,1346)]:
        ruler('Q487829',name,a,b,CHAG,'察合台系汗',True)
    for q in ['Q487829','Q1191125']:
        # The atlas retains the generic source identity on eastern polygons into 1462.
        chain(q, CENTRAL, '东察合台汗', 1368, '1347 秃忽鲁帖木儿|1363 亦里牙思火者', True)
        ruler(q,'黑的儿火者',1389,1399,CENTRAL,'东察合台汗',True)
        ruler(q,'马哈麻汗',1408,1416,CENTRAL,'东察合台汗',True)
        ruler(q,'歪思汗',1418,1428,CENTRAL,'东察合台汗',True)
        ruler(q,'也先不花二世',1429,1462,CENTRAL,'东察合台汗',True)
    ruler('Q1191125','羽奴思汗',1462,1487,CENTRAL,'蒙兀儿斯坦汗',True)
    for q, name, a, b, role in [
        ('local:yarkand-khanate','赛德汗',1514,1533,'叶尔羌汗'),
        ('local:yarkand-khanate','阿卜杜勒·拉希德汗',1533,1560,'叶尔羌汗'),
        ('local:yarkand-khanate','阿卜杜勒·卡里姆汗',1560,1591,'叶尔羌汗'),
        ('local:turpan-khanate','曼速儿汗',1503,1543,'东部汗廷，后以吐鲁番为中心'),
        ('local:turpan-khanate','沙汗',1543,1570,'吐鲁番汗')]:
        ruler(q,name,a,b,'https://www.iranicaonline.org/articles/yarkand/' if 'yarkand' in q else CENTRAL,role,True)
    fact('Q4332415','government','瓦剌诸部联盟',1409,1454,ATWOOD)


def regional_reigns():
    iran = 'https://www.iranicaonline.org/articles/aq-qoyunlu-confederation/'
    timur = 'https://uodiyala.edu.iq/uploads/PDF%20ELIBRARY%20UODIYALA/EL45/A%20History%20of%20Inner%20Asia%20%282000%20ebook%29.pdf'
    chain('Q555994', iran, '白羊王朝君主', 1490, '1402 卡拉·奥斯曼|1435 阿里贝格|1438 哈姆扎贝格|1444 杰汉吉尔|1453 乌尊·哈桑|1478 哈利勒|1478 雅库布', True)
    ruler('Q555994','穆拉德',1500,1508,iran,'白羊王朝末期伊拉克、法尔斯方向的分支君主',True)
    ruler('Q555994','阿尔万德',1497,1504,iran,'白羊王朝末期竞争汗廷',True)
    chain('Q324470', iran, '黑羊王朝君主', 1400, '1380 卡拉·穆罕默德|1390 卡拉·优素福', True)
    chain('Q324470', iran, '黑羊王朝君主', 1468, '1406 卡拉·优素福|1420 伊斯坎达尔|1438 贾汗沙|1467 哈桑·阿里', True)
    chain('Q484195', timur, '帖木儿家族统治者', 1449, '1370 帖木儿|1405 沙哈鲁|1447 兀鲁伯')
    ruler('Q484195','哈里勒苏丹',1405,1409,timur,'撒马尔罕支系，继承争位')
    ruler('Q484195','兀鲁伯',1409,1447,timur,'沙哈鲁治下的河中统治者')
    chain('Q484195', timur, '河中统治者', 1500, '1449 阿卜杜勒·拉提夫|1450 阿卜杜拉|1451 阿布·赛义德|1469 苏丹艾哈迈德|1494 苏丹马哈茂德', True)
    chain('Q484195', 'https://www.iranicaonline.org/articles/hosayn-bayqara/', '赫拉特的帖木儿支系君主', 1507, '1470 侯赛因·拜哈拉|1506 巴迪乌扎曼')
    chain('Q178084',134,'伊儿汗',1335,'1256 旭烈兀|1265 阿八哈|1282 帖古迭儿|1284 阿鲁浑|1291 海合都|1295 拜都|1295 合赞|1304 完者都|1316 不赛因')
    chain('Q11709',161,'德里苏丹',1526,'1451 巴赫卢尔·洛迪|1489 西坎达尔·洛迪|1517 易卜拉欣·洛迪')
    chain('Q167134',165,'章普尔苏丹',1483,'1394 马利克·萨尔瓦尔|1399 穆巴拉克沙|1401 易卜拉欣沙|1440 马哈茂德沙|1458 穆罕默德沙|1458 侯赛因沙')
    chain('Q374521','https://mapacademy.io/article/bahmani-sultanate/','巴赫曼尼苏丹',1518,'1347 哈桑·巴赫曼沙|1358 穆罕默德沙一世|1375 穆贾希德沙|1378 达乌德沙|1378 穆罕默德沙二世|1397 吉亚斯丁|1397 沙姆斯丁|1397 菲鲁兹沙|1422 艾哈迈德沙一世|1436 艾哈迈德沙二世|1458 胡马雍沙|1461 尼扎姆沙|1463 穆罕默德沙三世|1482 马哈茂德沙',True)
    ruler('Q4083686','纳西尔丁·马哈茂德沙',1435,1459,162,'孟加拉苏丹',True)
    chain('Q4083686',162,'孟加拉苏丹',1538,'1494 阿拉丁·侯赛因沙|1519 纳斯拉特沙|1532 菲鲁兹沙|1533 吉亚斯丁·马哈茂德沙',True)
    ruler('Q123027565','宰因·阿比丁',1420,1470,'https://www.iranicaonline.org/articles/kashmir-iii-administration/','克什米尔苏丹',True)
    ruler('Q167639','德瓦·拉亚二世',1424,1446,'https://vijayanagara.nic.in/en/about-district/','毗奢耶那伽罗君主，任期各来源有差异',True)
    vij = 'https://iks.iitgn.ac.in/wp-content/uploads/2020/01/Krishnadevaraya_and_his_political_theory_of_Vijayanagara.pdf'
    ruler('Q167639','伊马迪·纳拉辛哈',1491,1505,vij,'名义君主',True)
    ruler('Q167639','纳拉萨·纳亚卡',1491,1503,vij,'摄政与实际执政者',True)
    ruler('Q167639','维拉·纳拉辛哈',1503,1505,vij,'实际执政者，约1505年即位',True)
    chain('Q167639',vij,'毗奢耶那伽罗君主',1529,'1505 维拉·纳拉辛哈|1509 克里希纳德瓦·拉亚')
    thai = 'https://www.ayutthaya-history.com/Historical_Events14.html'
    chain('Q841364',thai,'阿瑜陀耶国王',1529,'1424 波隆摩拉差二世|1448 波隆玛·戴莱洛迦纳|1488 波隆摩拉差三世|1491 拉玛铁菩提二世',True)
    ruler('Q1059707','提洛迦拉',1441,1487,'https://asset.library.wisc.edu/1711.dl/7WQTPRO7QDHMR8G/R/file-a5c0a.pdf','兰纳国王')
    laos = 'https://seasite.niu.edu/lao/chronology_of_lan_xang_dynasty.htm'
    chain('Q853477',laos,'澜沧国王',1495,'1429 孟赛|1430 法开|1433 孔坎|1434 育空|1435 坎格|1441 赛雅·乍甲帕|1478 苏万那·班朗|1485 拉森泰·普瓦纳')
    chain('Q853477',laos,'澜沧国王',1571,'1497 宋普|1500 维苏纳拉|1520 波提萨拉特|1548 塞塔提拉')
    ava='https://academic.oup.com/hawaii-scholarship-online/book/14485/chapter-abstract/286704879'
    chain('Q2500952',ava,'阿瓦国王',1526,'1442 那罗波帝一世|1467 梯诃都罗|1480 明康二世|1501 那罗波帝二世',True)
    mal='https://www.melaka.gov.my/kerajaan/info-negeri/sejarah.html'
    chain('Q46652',mal,'马六甲苏丹',1511,'1444 阿布·沙希德沙|1446 穆扎法尔沙|1458 曼苏尔沙|1477 阿拉乌丁·里亚亚沙|1488 马哈茂德沙',True)
    chain('Q170770','https://www.britannica.com/place/Russia/The-Muscovite-period','莫斯科大公',1533,'1389 瓦西里一世|1425 瓦西里二世|1462 伊凡三世|1505 瓦西里三世',True)
    ruler('Q151536','叶夫菲米二世',1429,1458,'https://www.pravenc.ru/text/187753.html','诺夫哥罗德大主教，共和国重要政治人物')
    ruler('Q186537','兀鲁·穆罕默德',1438,1445,137,'喀山汗国建立者',True)


def european_reigns():
    venice='https://www.archiviodistatovenezia.it/images/file-pdf/DaMosto_1.pdf'
    chain('Q4948',venice,'威尼斯总督',1538,'1400 米凯莱·斯泰诺|1414 托马索·莫切尼戈|1423 弗朗切斯科·福斯卡里|1457 帕斯夸莱·马利皮耶罗|1462 克里斯托福罗·莫罗|1471 尼科洛·特龙|1473 尼科洛·马尔切洛|1474 彼得罗·莫切尼戈|1476 安德烈亚·文德拉明|1478 乔瓦尼·莫切尼戈|1485 马尔科·巴尔巴里戈|1486 阿戈斯蒂诺·巴尔巴里戈|1501 莱昂纳多·洛雷丹|1521 安东尼奥·格里马尼|1523 安德烈亚·格里蒂')
    genoa='https://www.lombardiabeniculturali.it/istituzioni/cronologie/cariche/2/'
    ruler('Q174306','拉斐尔·阿多尔诺',1443,1447,genoa,'热那亚总督')
    ruler('Q174306','克莱沃的菲利普',1499,1506,'https://www.treccani.it/enciclopedia/gian-luigi-fieschi_(Dizionario-Biografico)/','法国统治下的热那亚总督')
    ruler('Q174306','保罗·达诺维',1507,1507,genoa,'短期执政的热那亚总督')
    chain('Q48189','https://imperialteutonicorder.com/id4.html','条顿骑士团大团长',1525,'1414 米夏埃尔·屈希迈斯特|1422 保罗·冯·鲁斯多夫|1441 康拉德·冯·埃利希斯豪森|1449 路德维希·冯·埃利希斯豪森|1467 海因里希·罗伊斯·冯·普劳恩|1470 海因里希·罗伊斯·冯·里希滕贝格|1477 马丁·特鲁赫泽斯·冯·韦茨豪森|1489 约翰·冯·蒂芬|1497 萨克森的腓特烈|1510 勃兰登堡-安斯巴赫的阿尔布雷希特',True)
    ruler('Q1064825','海登赖希·芬克·冯·奥韦尔贝格',1439,1450,'https://www.imperialteutonicorder.com/id62.html','利沃尼亚骑士团团长')
    ruler('Q1064825','沃尔特·冯·普莱滕贝格',1494,1535,'https://tallinnmuseum.com/2018/10/13/the-teutonic-order-in-medieval-livonia/','利沃尼亚骑士团团长，联邦内另有主教领')
    ruler('Q148499','腓特烈二世',1440,1470,'https://www.deutsche-biographie.de/downloadPDF?url=sfz52986.pdf','勃兰登堡选帝侯')
    ruler('Q148499','约阿希姆一世',1499,1535,'https://www.deutsche-biographie.de/downloadPDF?url=sfz53309.pdf','勃兰登堡选帝侯')
    ruler('Q156199','腓特烈三世（智者）',1486,1525,'https://www.deutsche-biographie.de/downloadPDF?url=sfz135137.pdf','萨克森选帝侯')
    ruler('Q148540','科西莫·德·美第奇',1434,1464,'https://www.treccani.it/enciclopedia/cosimo-de-medici-detto-il-vecchio_(Dizionario-Biografico)/','美第奇家族首脑，共和国实际执政者')
    ruler('Q148540','皮耶罗·索德里尼',1502,1512,'https://www.treccani.it/enciclopedia/i-sette-stati-d-italia_(Storia-della-civilta-europea-a-cura-di-Umberto-Eco)/','佛罗伦萨终身正义旗手')
    for q, government, a, b, source in [
        ('Q4948','贵族共和国，由大议会选举总督',1200,1797,venice),
        ('Q48189','骑士团领地，由大团长统辖',1309,1525,'https://whc.unesco.org/en/list/847/'),
        ('Q1064825','骑士团领、主教领及城市组成的复合政体',1435,1561,'https://tallinnmuseum.com/2018/10/13/the-teutonic-order-in-medieval-livonia/')]:
        fact(q,'government',government,a,b,source)


    chain('Q2288','https://etheses.dur.ac.uk/7202/1/7202_4384.PDF','特维尔大公',1485,'1425 鲍里斯·亚历山德罗维奇|1461 米哈伊尔·鲍里索维奇',True)
    ruler('Q269109','伊凡·伊凡诺维奇',1500,1521,'https://vestnik.rsu-rzn.ru/wp-content/uploads/2025/01/%D0%92%D0%95%D0%A1%D0%A2%D0%9D%D0%98%D0%9A-%E2%84%96-4_-2024-%D0%BC%D0%B0%D0%BA%D0%B5%D1%82-7-22.pdf','梁赞末代大公，早年由家族摄政',True)
    for q in ['Q1232887','Q426025']:
        ruler(q,'卢多维科',1440,1465,'https://www.treccani.it/enciclopedia/ludovico-duca-di-savoia_(Dizionario-di-Storia)/','萨伏依公爵')
        ruler(q,'菲利贝托二世',1497,1504,'https://www.treccani.it/enciclopedia/filiberto-ii-duca-di-savoia_(Dizionario-Biografico)/','萨伏依公爵')
        ruler(q,'卡洛二世（部分年表称三世）',1504,1553,'https://www.treccani.it/enciclopedia/carlo-ii-duca-di-savoia_(Dizionario-Biografico)/','萨伏依公爵')
    ruler('Q47261','阿尔布雷希特三世',1438,1460,'https://hdbg.eu/biografien/detail/herzog-von-bayern-albrecht-iv-von-bayern/527','巴伐利亚-慕尼黑公爵，巴伐利亚当时有多个支系')
    ruler('Q47261','阿尔布雷希特四世',1467,1508,'https://hdbg.eu/biografien/detail/herzog-von-bayern-albrecht-iv-von-bayern/527','巴伐利亚-慕尼黑公爵，1505年前后统一主要支系')
    ruler('Q836894','卢多维科·特雷维桑',1440,1465,'https://www.treccani.it/enciclopedia/ludovico-trevisan_(Dizionario-Biografico)/','阿奎莱亚宗主教，世俗领地已大幅缩减')


def split_moghulistan():
    source = 'https://jhistory.enu.kz/index.php/jHistory/issue/download/3/19'
    for q, label, name, detail in [
        ('local:moghul-western-court','西部蒙兀儿汗廷','Western Moghul Court',
         '羽奴思汗去世后，马哈木汗统领西部部众。1503年前后失去塔什干，此后地图范围仅作天山一带势力示意。'),
        ('local:moghul-eastern-court','东部蒙兀儿汗廷','Eastern Moghul Court',
         '阿黑麻汗和继任者曼速儿汗的东部汗廷。轮廓沿用原图，西南塔里木盆地仍存在独立掌权的杜格拉特首领。')]:
        entities.setdefault(q,dict(label=label,en=name,description=detail,fields={}))
        facts['labels'][q]=label
        fact(q,'government','察合台后裔汗廷',1487,1514,source)
    ruler('local:moghul-western-court','马哈木汗',1487,1508,source,'西部汗廷；1503年前后失去塔什干',True)
    chain('local:moghul-eastern-court',source,'东部蒙兀儿汗',1514,'1487 阿黑麻汗|1504 曼速儿汗',True)
    names = {}
    for century in (14,15):
        path=f'public/data/temporal/{century}.geojson'
        data=read(path)
        changed=False
        for f in data['features']:
            p=f['properties']
            if p.get('qid')!='Q1191125' or p['validFrom']!=1492 and p['validFrom']!=1502:
                continue
            if p['NAME']=='Eastern Chagatai Khanate':
                q='local:moghul-western-court'
            elif p['NAME']=='Moghulistan':
                q='local:moghul-eastern-court'
            else:
                continue
            e=entities[q]
            p.update(sourceName=p['NAME'],sourceQid=p['qid'],NAME=e['en'],SUBJECTO=e['en'],
                     displayName=e['label'],qid=q,entityId=q,sourceUrl=source,
                     identityCorrection=TAG,representationNote=e['description'])
            names[e['en']]=e['label']
            changed=True
        if changed:
            write(path,data)
    if names:
        for path in ['src/localization/display-names.zh.json','src/localization/temporal.zh.json']:
            data=read(path)
            data.update(names)
            write(path,data)



def restore_venice_city():
    from shapely.geometry import Point, box, mapping, shape
    from shapely.ops import unary_union
    from territory_repair_stage import clean

    city = Point(12.3403, 45.4337)
    lagoon_core = box(12.30, 45.41, 12.38, 45.46)
    land = [shape(f['geometry']) for f in read('public/data/ne_10m_land.geojson')['features']]
    city_land = unary_union([g.intersection(lagoon_core) for g in land if g.intersects(lagoon_core)])
    assert city_land.covers(city)

    for century in range(12,18):
        path = f'public/data/temporal/{century}.geojson'
        data = read(path)
        changed = False
        for feature in data['features']:
            p = feature['properties']
            if p['NAME'] != 'Republic of Venice':
                continue
            territory = shape(feature['geometry'])
            if territory.covers(city) or territory.distance(city) > .25:
                continue
            # Restore the small lagoon core clipped from the historical coast.
            # Leave any competing historical polygon's land unchanged.
            competitors = []
            for other in data['features']:
                a = other['properties']
                if (a['NAME'] != p['NAME'] and a['validFrom'] <= p['validTo']
                        and p['validFrom'] <= a['validTo']):
                    geom = shape(other['geometry'])
                    if geom.intersects(lagoon_core):
                        competitors.append(clean(geom))
            inset = city_land.difference(unary_union(competitors))
            if not inset.covers(city):
                continue
            feature['geometry'] = mapping(clean(territory).union(inset))
            changed = True
        if changed:
            write(path, data)



if __name__ == '__main__':
    for entity in entities.values():
        for key, rows in entity['fields'].items():
            entity['fields'][key] = [row for row in rows if row.get('supplement') != TAG]
    maghreb()
    khanates()
    regional_reigns()
    european_reigns()
    split_moghulistan()
    restore_venice_city()
    write('public/data/polity-facts.json', facts)
    print(dict(counts))




