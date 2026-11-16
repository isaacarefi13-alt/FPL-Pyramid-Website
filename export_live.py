#!/usr/bin/env python3
"""Export verified match data over the historic snapshot; cup remains a separate manual feed."""
import json, sqlite3, pathlib, collections, datetime, os, urllib.request, csv, io
from sync import ROOT,DB,SEASON,init

def build():
    data=json.loads((ROOT/'data.json').read_text())
    if not DB.exists():return data,0
    db=sqlite3.connect(DB);init(db)
    rows=db.execute('SELECT division,gameweek,home_entry,away_entry,home_score,away_score FROM fixtures WHERE season=?',(SEASON,)).fetchall()
    if not rows:return data,0
    names={(d,e):(n,t) for d,e,n,t in db.execute('SELECT division,entry_id,manager,team FROM entry_names WHERE season=?',(SEASON,))}
    # Strict safety: do not replace 2026/27 placeholder rows unless all fixture entry IDs have a name.
    if any((d,e) not in names for d,gw,h,a,hs,ass in rows for e in (h,a)):return data,0
    stats=collections.defaultdict(lambda:dict(w=0,d=0,l=0,sf=0,sa=0))
    for d,gw,h,a,hs,ass in rows:
        x=stats[(d,h)];y=stats[(d,a)];x['sf']+=hs;x['sa']+=ass;y['sf']+=ass;y['sa']+=hs
        if hs>ass:x['w']+=1;y['l']+=1
        elif hs<ass:x['l']+=1;y['w']+=1
        else:x['d']+=1;y['d']+=1
    # Replace only divisions with at least one verified result; never duplicate historical season data.
    active={d for d,e in stats}
    data['records']=[r for r in data['records'] if not (r['season']==SEASON and r['division'] in active)]
    for d in active:
        items=[]
        for (division,e),s in stats.items():
            if division!=d:continue
            n,t=names[(d,e)];pts=3*s['w']+s['d'];items.append(dict(season=SEASON,division=d,rank=0,team=t,manager=n,pts=pts,sd=s['sf']-s['sa'],**s))
        items.sort(key=lambda r:(-r['pts'],-r['sf'],-r['sd'],r['manager']))
        for i,r in enumerate(items,1):r['rank']=i
        data['records'].extend(items)
    # All-time: historical archive plus verified current season results. Do not overwrite historic source totals.
    for d in active:
        byname={r['manager']:dict(r) for r in data['alltime'] if r['division']==d}
        for r in [r for r in data['records'] if r['season']==SEASON and r['division']==d]:
            name=r['manager'];a=byname.get(name)
            if a is None:
                a=dict(division=d,rank=0,manager=name,seasons=0,gp=0,w=0,d=0,l=0,pts=0,sf=0,sa=0,sd=0,titles=0)
                byname[name]=a
            if a['gp']==0:a['seasons']+=1
            a['gp']+=r['w']+r['d']+r['l']
            for k in ('w','d','l','pts','sf','sa','sd'):a[k]+=r[k]
        data['alltime']=[r for r in data['alltime'] if r['division']!=d]
        ranked=sorted(byname.values(),key=lambda r:(-r['pts'],-r['sf'],r['manager']))
        for i,r in enumerate(ranked,1):r['rank']=i
        data['alltime'].extend(ranked)
    # Derbies: increment from verified current-season fixtures, keyed by canonical manager names.
    for derby in data['derbies']:
        for d,gw,h,a,hs,ass in rows:
            if {names[(d,h)][0],names[(d,a)][0]}!={derby['first'],derby['second']}:continue
            derby['played']+=1
            if hs==ass:derby['draws']+=1
            else:
                winner=names[(d,h)][0] if hs>ass else names[(d,a)][0]
                derby['firstWins' if winner==derby['first'] else 'secondWins']+=1
    data['meta']['live_matches']=len(rows)
    data['meta']['last_sync']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    return data,len(rows)

def cup_csv(data):
    # Publish just the FPL Cup tab as CSV (File > Share > Publish to web > specific tab > CSV).
    url=os.environ.get('FPL_CUP_CSV_URL','')
    if not url:return
    if not url.startswith('https://docs.google.com/spreadsheets/'):raise ValueError('Cup CSV must use a Google Sheets published CSV URL')
    with urllib.request.urlopen(url,timeout=20) as resp:txt=resp.read().decode('utf-8-sig')
    reader=csv.DictReader(io.StringIO(txt))
    required={'group','rank','manager','w','d','l','sf','pts'}
    if not required.issubset(set(reader.fieldnames or [])):raise ValueError('Cup CSV requires headers: '+', '.join(sorted(required)))
    entries=[]
    for row in reader:
        entries.append({k:int(row[k]) if k in {'rank','w','d','l','sf','pts'} else row[k] for k in required})
    if entries:data['cups']=entries

if __name__=='__main__':
    data,n=build()
    try:cup_csv(data)
    except Exception as ex:print('Cup sync skipped:',ex)
    (ROOT/'live-data.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
    (ROOT/'live-data.js').write_text('window.FPL_DATA = '+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';')
    print('Exported',n,'verified fixtures; historical snapshot retained if zero.')
