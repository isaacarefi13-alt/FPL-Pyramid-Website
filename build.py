import json,re,os
from pathlib import Path
P=Path('/mnt/data/fpl_website')
# Records sourced from the connected Fantasy Premier League workbook, as at Nov 16, 2026.
# Format: rank|team|manager|W|D|L|points|for|against
raw={
'2025/26':{
'FPL1':'''1|Wizard of Ozil|Tanner Bush|23|2|13|71|1644|1590
2|2 Point FC|Jason Chugh|21|0|17|63|1619|1568
3|Return of the Fish|Grant Loos|20|1|17|61|1541|1455
4|Super Mik’s Wanx|Nick Buck|19|1|18|58|1704|1632
5|Ivory Toast|Jack Brooks|19|1|18|58|1686|1549
6|ABCDE FC|Tyler Galloway|17|2|19|53|1539|1632
7|Vardy Party (RIP)|Liam Bramley|17|1|20|52|1565|1663
8|VAR VAR Binks|Nathan Loos|17|0|21|51|1543|1568
9|Spell Treble|Sam Ansong|16|3|19|51|1529|1647
10|Xhaka Xhaka he-he|Timmy Martin|15|1|22|46|1606|1672''',
'FPL2':'''1|English’s Englishmen|Zach English|24|1|13|73|1590|1473
2|Rentboys FC|Isaac Arefi|24|0|14|72|1757|1466
3|Squeege FC|Deji Elisha|21|1|16|64|1436|1437
4|MLS Takeover|Lukas Buck|20|1|17|61|1475|1401
5|Big Virg|Nick Daniels|20|0|18|60|1606|1469
6|Champions of Europe|Zach Arefi|18|0|20|54|1586|1516
7|It’s Ash|Ash Rajmohan|18|0|20|54|1370|1526
8|Tiki Takka MoSalah|Josh Brooks|17|0|21|51|1705|1543
9|Robbo’s Rabbis|Joey Brooks|13|1|24|40|1448|1615
10|Jelly Jones|Jensen Ciehanski|13|0|25|39|1369|1561''',
'FPL3':'''1|Starboy Summer FC|Sam Paul|23|2|13|71|1678|1559
2|Saudi FC|Matt Martin|23|1|14|70|1747|1622
3|RyanGiggsRightHook|Adam Conselyea|22|0|16|66|1582|1466
4|Turno Dos FC|Camilo Colotto|20|0|18|60|1708|1638
5|Merteswagger|Connor Zimmer|19|0|19|57|1549|1494
6|Luton Town|Sam Polonia|18|1|19|55|1582|1579
7|Wizard of Ozil|Henry Valachovic|18|1|19|55|1555|1618
8|DJ’s Crew FC|Dennis Jeansonne|17|0|21|51|1509|1586
9|Scharface FC|Devon Cairns|15|3|20|48|1503|1626
10|Bowen 747|Matthew English|11|0|27|33|1355|1580'''},
'2024/25':{
'FPL1':'''1|Super Mik’s Lads|Nick Buck|25|0|13|75|1580|1439
2|Saka Boom|Tanner Bush|21|2|15|65|1645|1530
3|Ivory Toast|Jack Brooks|20|1|17|61|1675|1535
4|Vardy Party|Liam Bramley|19|0|19|57|1520|1547
5|Hasbulla FC|Nathan Loos|19|0|19|57|1460|1521
6|Thottingham Forest|Timmy Martin|18|1|19|55|1666|1555
7|Major League Saka|Jason Chugh|18|1|19|55|1466|1513
8|Chicken Tiki Mo Salah|Joey Brooks|18|1|19|55|1414|1523
9|Commish FC|Isaac Arefi|15|2|21|47|1565|1626
10|Gritty McGinn|Josh Brooks|13|0|25|39|1442|1621''',
'FPL2':'''1|Spell Treble|Sam Ansong|26|0|12|78|1684|1478
2|ABCDE FC|Tyler Galloway|26|0|12|78|1628|1474
3|Fish’s Revenge|Grant Loos|22|0|16|66|1538|1498
4|Big Virg|Nick Daniels|21|0|17|63|1557|1530
5|Squeege FC|Deji Elisha|20|0|18|60|1558|1483
6|Jelly Jones|Jensen Ciehanski|19|1|19|57|1520|1494
7|English’s Englishmen|Zach English|18|1|19|55|1399|1455
8|King Kai|Lukas Buck|13|1|24|40|1389|1488
9|Im Ash|Ash Rajmohan|12|1|25|37|1322|1531
10|Big Ange Ball|Zach Arefi|11|1|26|34|1371|1525'''},
'2023/24':{
'FPL1':'''1|Rabbo’s Rabbis|Joey Brooks|23|1|14|70|1748|1537
2|Rentboys FC|Isaac Arefi|23|0|15|69|1641|1542
3|Arsenal|Jason Chugh|22|0|16|66|1579|1503
4|Hasbulla FC|Nathan Loos|20|0|18|60|1477|1459
5|Ivory Toast|Jack Brooks|20|0|18|60|1449|1458
6|Shiver me Timbers|Tanner Bush|19|0|19|57|1577|1626
7|Sloppy Kloppy|Josh Brooks|19|0|19|57|1499|1513
8|ABCDE FC|Tyler Galloway|16|1|21|49|1552|1595
9|English’s Englishmen|Zach English|15|0|23|45|1511|1616
10|GroupMe FC|Grant Loos|12|0|26|36|1463|1645''',
'FPL2':'''1|Super Mik’s Lads|Nick Buck|25|1|12|76|1607|1475
2|Vardy Party|Liam Bramley|23|0|15|69|1772|1593
3|Thottingham Forest|Timmy Martin|22|2|14|68|1708|1528
4|Big Virg FC|Nick Daniels|22|1|15|67|1571|1471
5|Jelly Jones|Jensen Ciehanski|22|0|16|66|1578|1598
6|Fidget Spinner FC|Lukas Buck|17|1|20|52|1456|1514
7|Team Treble|Sam Ansong|15|1|22|46|1454|1466
8|Squeege FC|Deji Elisha|14|1|23|43|1403|1600
9|That’s So Spursy|Zach Arefi|13|2|23|41|1376|1508
10|Ash|Ash Rajmohan|12|1|25|37|1269|1431'''},
'2022/23':{'FPL1':'''1|Rip Fish|Grant Loos|23|2|13|71|1628|1436
2|ABCDE FC|Tyler Galloway|20|3|15|63|1581|1460
3|Rabbi-Joes Lads|Joey Brooks|19|2|17|59|1599|1507
4|2 Girls 1 Klopp|Jason Chugh|19|2|17|59|1588|1532
5|Toney Soprano Gabagu|Josh Brooks|19|1|18|58|1473|1497
6|Rentboys FC|Isaac Arefi|18|1|19|55|1408|1566
7|Hasbulla FC|Nathan Loos|17|1|20|52|1499|1507
8|Waka Saka|Tanner Bush|17|1|20|52|1450|1533
9|Ivory Toast|Jack Brooks|15|2|21|47|1469|1454
10|English’s Englishmen|Zach English|14|3|21|45|1445|1518'''},
'2021/22':{'FPL1':'''1|Rabbi-Joes Lads|Joey Brooks|24|1|13|73|1688|1446
2|Ivory Toast|Jack Brooks|24|1|13|73|1593|1428
3|ABCDE FC|Tyler Galloway|21|2|15|65|1592|1451
4|English’s Englishmen|Zach English|20|1|17|61|1440|1486
5|AVERAGE|AVERAGE|20|0|18|60|1508|1488
6|Cincinnati Kid|Adam Fisher|19|0|19|57|1527|1448
7|DewMeister Mutual|Jason Chugh|18|2|18|56|1606|1614
8|Rowe Ya Boat|Tanner Bush|17|3|18|54|1426|1492
9|Below AVERAGE|Grant Loos|16|1|21|49|1465|1612
10|Lil Uzi Havertz|Josh Brooks|14|2|22|44|1403|1491
11|Rentboys FC|Isaac Arefi|14|1|23|43|1719|1713
12|Shart FC|Nathan Loos|13|2|23|41|1321|1601'''},
'2020/21':{'FPL1':'''1|OSU Medical School|Brett Shields|28|0|10|84|1635|1318
2|Rabbi-Joes Lads|Joey Brooks|25|1|12|76|1460|1272
3|Jozay’s Lads|Josh Brooks|23|0|15|69|1573|1355
4|Cincinnati Kid|Adam Fisher|23|0|15|69|1494|1463
5|English’s Englishmen|Zach English|21|1|16|64|1429|1377
6|Ivory Toast|Jack Brooks|20|0|18|60|1531|1400
7|Rentboys FC|Isaac Arefi|18|1|19|55|1455|1479
8|ABCDE FC|Tyler Galloway|17|0|21|51|1372|1389
9|Timbo’s Team|Timmy Martin|15|0|23|45|1350|1576
10|Liverbool|Jason Chugh|13|0|25|39|1344|1521
11|Sugandese|Grant Loos|11|2|25|35|1385|1486
12|I’m 6’3|Nathan Loos|11|1|26|34|1434|1611'''},
'2019/20':{'FPL1':'''1|Rentboys FC|Isaac Arefi|26|0|12|78|1756|1414
2|ABCDE FC|Tyler Galloway|24|1|13|73|1580|1427
3|English’s Englishmen|Zach English|20|1|17|61|1571|1454
4|Freight Train FC|Adam Fisher|20|0|18|60|1545|1497
5|Matip Comes Last|Jason Chugh|17|0|21|51|1520|1652
6|Ligma|Grant Loos|14|4|20|46|1433|1693
7|Sicko Mode|Nathan Loos|14|1|23|43|1495|1649
8|Fuck the Commish|Timmy Martin|13|1|24|40|1374|1620'''},
'2018/19':{'FPL1':'''1|Rentboys FC|Isaac Arefi|24|0|14|72|1531|1402
2|Freight Train FC|Adam Fisher|24|0|14|72|1494|1417
3|R.I.P Swansea|Timmy Martin|23|0|15|69|1617|1362
4|Fiddle Matip|Jason Chugh|22|1|15|67|1587|1315
5|SomeoneBuyHazard $10|Brett Shields|22|0|16|66|1644|1441
6|Smuttymenjensens|Tanner Bush|19|1|18|58|1368|1482
7|English’s Englishmen|Zach English|18|0|20|54|1428|1488
8|Have It|Tyler Galloway|17|2|19|53|1344|1416
9|Frag Out|Grant Loos|16|3|19|51|1479|1487
10|$5 Per Player|Jimmy Fasulo|15|0|23|45|1403|1575
11|Darude Sandstorm|Nathan Loos|13|0|25|39|1308|1575
12|Alli Express|Josh Brooks|11|1|26|34|1213|1400'''},
'2017/18':{'FPL1':'''1|The Wizard of Ozil|Tanner Bush|27|1|10|82|1809|1548
2|Rentboys FC|Isaac Arefi|20|3|15|63|1438|1471
3|Balled Up Tissues|Brett Shields|19|1|18|58|1464|1471
4|Coutinho Fucked Me|Jason Chugh|18|0|20|54|1542|1570
5|ABCDE FC|Tyler Galloway|18|0|20|54|1438|1432
6|ThereIsAHoleInMyWall|Nathan Loos|17|2|19|53|1661|1553
7|Ivory Toast|Jack Brooks|15|2|21|47|1481|1626
8|RainbowDashWarriors|Adam Fisher|13|1|24|40|1386|1598'''}
}
current={
'FPL1':'''Wizard of Ozil|Tanner Bush
2 Point FC|Jason Chugh
Return of the Fish|Grant Loos
Super Mik’s Wanx|Nick Buck
Ivory Toast|Jack Brooks
ABCDE FC|Tyler Galloway
Vardy Party (RIP)|Liam Bramley
VAR VAR Binks|Nathan Loos
Spell Treble|Sam Ansong
Xhaka Xhaka he-he|Timmy Martin''',
'FPL2':'''English’s Englishmen|Zach English
Rentboys FC|Isaac Arefi
Squeege FC|Deji Elisha
Turno Dos FC|Camilo Colotto
Big Virg|Nick Daniels
Champions of Europe|Zach Arefi
It’s Ash|Ash Rajmohan
Tiki Takka MoSalah|Josh Brooks
Robbo’s Rabbis|Joey Brooks
Jelly Jones|Jensen Ciehanski''',
'FPL3':'''Tiki Takka MoSalah|Josh Brooks
Robbo’s Rabbis|Joey Brooks
Jelly Jones|Jensen Ciehanski
Stillzy FC|Tyler Stills
Merteswagger|Connor Zimmer
Luton Town|Sam Polonia
Wizard of Ozil|Henry Valachovic
Kwabs team name here|Kwab Ayesu
Scharface FC|Devon Cairns
Bowen 747|Matthew English'''
}
# All-time data: rank,manager,seasons,gp,w,d,l,points,sf,sa,titles
alltime_raw={
'FPL1':'''1|Jason Chugh|9|342|168|6|168|510|13851|13788|0
2|Isaac Arefi|8|304|158|8|138|482|12513|12213|2
3|Tyler Galloway|8|304|150|11|143|461|11998|11802|0
4|Tanner Bush|7|266|143|10|113|439|10919|10801|2
5|Nathan Loos|9|342|141|7|194|430|13198|14044|0
6|Jack Brooks|7|266|133|7|126|406|10884|10450|0
7|Grant Loos|7|266|112|13|141|349|10394|10814|1
8|Joey Brooks|5|190|109|6|75|333|7862|7239|2
9|Zach English|6|228|108|6|114|330|8824|8939|0
10|Josh Brooks|6|228|99|4|125|301|8544|8988|0
11|Adam Fisher|5|190|99|1|90|298|7446|7423|0
12|Timmy Martin|5|190|84|3|103|255|7613|7785|0
13|Brett Shields|3|114|69|1|44|208|4743|4230|1
14|Nick Buck|2|76|44|1|31|133|3284|3071|1
15|Liam Bramley|2|76|36|1|39|109|3085|3210|0
16|AVERAGE|1|38|20|0|18|60|1508|1488|0
17|Sam Ansong|1|38|16|3|19|51|1529|1647|0
18|Jimmy Fasulo|1|38|15|0|23|45|1403|1575|0''',
'FPL2':'''1|Nick Daniels|3|114|63|1|50|190|4734|4470|0
2|Deji Elisha|3|114|55|2|57|167|4397|4520|0
3|Jensen Ciehanski|3|114|54|1|60|163|4467|4653|0
4|Lukas Buck|3|114|50|3|61|153|4320|4403|0
5|Zach Arefi|3|114|42|3|69|129|4333|4549|0
6|Ash Rajmohan|3|114|42|2|70|128|3961|4488|0
7|Zach English|2|76|42|2|32|128|2989|2928|1
8|Sam Ansong|2|76|41|1|34|124|3138|2944|1
9|Tyler Galloway|1|38|26|0|12|78|1628|1474|0
10|Nick Buck|1|38|25|1|12|76|1607|1475|1
11|Isaac Arefi|1|38|24|0|14|72|1757|1466|0
12|Liam Bramley|1|38|23|0|15|69|1772|1593|0
13|Timmy Martin|1|38|22|2|14|68|1708|1528|0
14|Grant Loos|1|38|22|0|16|66|1538|1498|0
15|Josh Brooks|1|38|17|0|21|51|1705|1543|0
16|Joey Brooks|1|38|13|1|24|40|1448|1615|0
20|Camilo Colotto|1|38|20|0|18|60|1708|1638|0''',
'FPL3':'''1|Sam Paul|1|38|23|2|13|71|1678|1559|1
2|Matt Martin|1|38|23|1|14|70|1747|1622|0
3|Adam Conselyea|1|38|22|0|16|66|1582|1466|0
4|Camilo Colotto|1|38|20|0|18|60|1708|1638|0
5|Connor Zimmer|1|38|19|0|19|57|1549|1494|0
6|Sam Polonia|1|38|18|1|19|55|1582|1579|0
7|Henry Valachovic|1|38|18|1|19|55|1555|1618|0
8|Dennis Jeansonne|1|38|17|0|21|51|1509|1586|0
9|Devon Cairns|1|38|15|3|20|48|1503|1626|0
10|Matthew English|1|38|11|0|27|33|1355|1580|0'''
}
# Cup Group A-F from FPL CUP Table
cups_raw='''A|1|Josh Brooks|3|0|2|205|9
A|2|Devon Cairns|3|0|2|173|9
A|3|Sam Ansong|2|0|3|224|6
A|4|Sam Polonia|2|0|3|175|6
A|5|Grant Loos|2|0|2|154|6
B|1|Zach Arefi|4|0|1|204|12
B|2|Henry Valachovic|3|0|2|228|9
B|3|Camilo Colotto|3|0|2|171|9
B|4|Tyler Galloway|2|0|3|177|6
B|5|Zach English|0|0|4|138|0
C|1|Jensen Ciehanski|4|0|1|233|12
C|2|Jack Brooks|4|0|1|218|12
C|3|Deji Elisha|3|0|2|230|9
C|4|Connor Zimmer|1|0|4|193|3
C|5|Sam Paul|0|0|4|144|0
D|1|Nick Buck|3|0|2|226|9
D|2|Matthew English|3|0|2|224|9
D|3|Jason Chugh|3|0|1|186|9
D|4|Adam Conselyea|2|0|3|197|6
D|5|Nick Daniels|1|0|4|172|3
E|1|Matt Martin|4|0|1|229|12
E|2|Isaac Arefi|2|1|2|219|7
E|3|Liam Bramley|2|1|2|216|7
E|4|Tanner Bush|2|0|2|160|6
E|5|Tyler Stills|1|0|4|169|3
F|1|Joey Brooks|5|0|0|208|15
F|2|Nathan Loos|3|0|2|215|9
F|3|Timmy Martin|2|0|2|139|6
F|4|Ash Rajmohan|1|0|4|146|3
F|5|Kwabena Ayesu|1|0|4|112|3'''
# Derby totals derived from the Total rows of derby sheet. No inferred head-to-head results.
derby_raw='''The Arefi Derby|Isaac Arefi|Zach Arefi|5|1|0|4
The Loos Derby|Nathan Loos|Grant Loos|16|6|1|9
The Brooks Derby|Josh Brooks|Jack Brooks|1|0|0|1
The Martin Derby|Matt Martin|Timmy Martin|1|1|0|0
The Taylor Derby|Tyler Stills|Jensen Ciehanski|2|0|0|2
The Old Town Park Derby|Joey Brooks|Nick Daniels|4|1|0|3
The English Derby|Zach English|Matthew English|2|1|0|1
The Perrysburg Derby|Devon Cairns|Connor Zimmer|7|2|0|5
The Blake Street Derby|Liam Bramley|Isaac Arefi|7|3|1|3
The Toilet Bowl Derby|Kwab Ayesu|Joey Brooks|3|0|0|3
The St. Charles Derby|Adam Conselyea|Henry Valachovic|4|1|0|3
The Fantrax Derby|Camilo Colotto|Zach Arefi|4|2|1|1
The Westerville Tennis Derby|Tanner Bush|Jensen Ciehanski|0|0|0|0
The Florida Man Derby|Tyler Galloway|Jason Chugh|11|7|0|4
The Jollof Derby|Deji Elisha|Sam Ansong|2|1|0|1
The New Albany Derby|Nick Buck|Nathan Loos|6|4|0|2
The Sammy P Derby|Sam Polonia|Sam Paul|6|3|0|3
The OSUCOM Derby|Jack Brooks|Sam Paul|1|1|0|0'''
# Hall of Fame tab, recorded winners 2017/18 to 2025/26 plus FPL2 and FPL3
champions_raw='''FPL1|2017/18|Tanner Bush|The Wizard of Ozil|82|Mo Salah · 303 pts
FPL1|2018/19|Isaac Arefi|Rentboys FC|72|Sergio Agüero · 169 pts
FPL1|2019/20|Isaac Arefi|Rentboys FC|78|Kevin De Bruyne · 251 pts
FPL1|2020/21|Brett Shields|OSU Medical School|84|Bruno Fernandes · 244 pts
FPL1|2021/22|Joey Brooks|Rabbi-Joes Lads|73|Jarrod Bowen · 206 pts
FPL1|2022/23|Grant Loos|Rip Fish|71|Mo Salah · 272 pts
FPL1|2023/24|Joey Brooks|Rabbo’s Rabbis|70|Phil Foden · 230 pts
FPL1|2024/25|Nick Buck|Super Mik’s Lads|75|Chris Wood · 200 pts
FPL1|2025/26|Tanner Bush|Wizard of Ozil|71|Gabriel · 209 pts
FPL2|2023/24|Nick Buck|Super Mik’s Lads|76|Phil Foden · 230 pts
FPL2|2024/25|Sam Ansong|Spell Treble|78|Mo Salah · 344 pts
FPL2|2025/26|Zach English|English’s Englishmen|73|Declan Rice · 184 pts
FPL3|2025/26|Sam Paul|Starboy Summer FC|71|Bruno Fernandes · 235 pts'''
records=[]
for year,groups in raw.items():
 for div,block in groups.items():
  for line in block.strip().splitlines():
   a=line.split('|');rank,team,manager,w,d,l,pts,sf,sa=a
   records.append(dict(season=year,division=div,rank=int(rank),team=team,manager=manager,w=int(w),d=int(d),l=int(l),pts=int(pts),sf=int(sf),sa=int(sa),sd=int(sf)-int(sa)))
for div,block in current.items():
 for i,line in enumerate(block.strip().splitlines(),1):
  team,manager=line.split('|');records.append(dict(season='2026/27',division=div,rank=i,team=team,manager=manager,w=None,d=None,l=None,pts=None,sf=None,sa=None,sd=None))
alltime=[]
for div,block in alltime_raw.items():
 for l in block.strip().splitlines():
  a=l.split('|');rank,manager,ss,gp,w,d,lo,pts,sf,sa,titles=a
  alltime.append(dict(division=div,rank=int(rank),manager=manager,seasons=int(ss),gp=int(gp),w=int(w),d=int(d),l=int(lo),pts=int(pts),sf=int(sf),sa=int(sa),sd=int(sf)-int(sa),titles=int(titles)))
cups=[]
for l in cups_raw.splitlines():
 g,rank,name,w,d,lo,sf,pts=l.split('|');cups.append(dict(group=g,rank=int(rank),manager=name,w=int(w),d=int(d),l=int(lo),sf=int(sf),pts=int(pts)))
derbies=[]
for l in derby_raw.splitlines():
 n,a,b,played,aw,d,bw=l.split('|');derbies.append(dict(name=n,first=a,second=b,played=int(played),firstWins=int(aw),draws=int(d),secondWins=int(bw)))
champions=[]
for l in champions_raw.splitlines():
 div,season,manager,team,pts,mvp=l.split('|');champions.append(dict(division=div,season=season,manager=manager,team=team,points=int(pts),mvp=mvp))
data=dict(records=records,alltime=alltime,cups=cups,derbies=derbies,champions=champions,meta=dict(source='https://docs.google.com/spreadsheets/d/1mAR28FMRYDPSqXlthuV2MgzVM8iEnCJT5RjPOyGZjpI/edit',captured='November 16, 2026',note='Snapshot of the connected Fantasy Premier League Google Sheet. 2026/27 season has manager/team placeholders but no calculated standings, and duplicates appear across the FPL2 and FPL3 source sections. Historical all-time tables may contain stale references or formula errors; displayed records reproduce numeric source entries.'))
(P/'data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print('rows',len(records),'alltime',len(alltime),'cup',len(cups),'derbies',len(derbies),'champions',len(champions))
