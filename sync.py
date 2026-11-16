#!/usr/bin/env python3
"""Conservative FPL Draft importer: never manufacture or overwrite unverifiable results."""
import json, os, sqlite3, urllib.request, urllib.error, datetime, pathlib, csv, io
ROOT=pathlib.Path(__file__).resolve().parent
DB=ROOT/'pyramid.sqlite3'
LEAGUES={'FPL1':148874,'FPL2':82799,'FPL3':215819}
SEASON=os.environ.get('FPL_SEASON','2026/27')
BASE='https://draft.premierleague.com/api'

def fetch(url):
    req=urllib.request.Request(url,headers={'User-Agent':'FPLPyramidArchive/1.0 (community league)', 'Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)

def init(db):
    db.executescript('''CREATE TABLE IF NOT EXISTS raw_fetches (division TEXT NOT NULL, endpoint TEXT NOT NULL, fetched_at TEXT NOT NULL, payload TEXT NOT NULL, PRIMARY KEY(division,endpoint));
    CREATE TABLE IF NOT EXISTS fixtures (season TEXT NOT NULL, division TEXT NOT NULL, gameweek INTEGER NOT NULL, match_id TEXT NOT NULL, home_entry TEXT NOT NULL, away_entry TEXT NOT NULL, home_score INTEGER NOT NULL, away_score INTEGER NOT NULL, PRIMARY KEY(season,division,gameweek,match_id));
    CREATE TABLE IF NOT EXISTS entry_names (season TEXT NOT NULL, division TEXT NOT NULL, entry_id TEXT NOT NULL, manager TEXT NOT NULL, team TEXT NOT NULL, PRIMARY KEY(season,division,entry_id));
    CREATE TABLE IF NOT EXISTS sync_log (at TEXT, division TEXT, endpoint TEXT, status TEXT, detail TEXT);
    ''')

def log(db,division,endpoint,status,detail=''):
    db.execute('INSERT INTO sync_log VALUES(?,?,?,?,?)',(datetime.datetime.now(datetime.timezone.utc).isoformat(),division,endpoint,status,str(detail)[:500]))

def entries_from(details):
    entries=details.get('league_entries',[]) if isinstance(details,dict) else []
    if not isinstance(entries,list):return []
    out=[]
    for e in entries:
        if not isinstance(e,dict):continue
        eid=e.get('entry_id',e.get('id'))
        if eid is None:continue
        manager=e.get('player_first_name','')+' '+e.get('player_last_name','')
        manager=manager.strip() or e.get('player_name') or e.get('manager_name') or e.get('entry_name') or f'Entry {eid}'
        team=e.get('entry_name') or e.get('name') or str(manager)
        out.append((str(eid),str(manager),str(team)))
    return out

def extract_matches(payload):
    """Accept only explicit, completed H2H matches with scores and event IDs."""
    if isinstance(payload,list):items=payload
    elif isinstance(payload,dict):
        items=next((payload[k] for k in ('matches','results','fixtures') if isinstance(payload.get(k),list)),[])
    else:items=[]
    out=[]
    for m in items:
        if not isinstance(m,dict):continue
        gw=m.get('event',m.get('gameweek'))
        home=m.get('league_entry_1',m.get('entry_1',m.get('home_entry')))
        away=m.get('league_entry_2',m.get('entry_2',m.get('away_entry')))
        hs=m.get('league_entry_1_points',m.get('entry_1_points',m.get('home_score')))
        ass=m.get('league_entry_2_points',m.get('entry_2_points',m.get('away_score')))
        # FPL may expose partial scores. Only final fixtures are persisted.
        complete=m.get('finished',m.get('is_finished',m.get('final',False)))
        if not complete:continue
        try:
            gw=int(gw);hs=int(hs);ass=int(ass)
            if not (1<=gw<=38) or home is None or away is None or str(home)==str(away):continue
            mid=str(m.get('id',f'{gw}:{home}:{away}'))
            out.append((gw,mid,str(home),str(away),hs,ass))
        except (TypeError,ValueError):continue
    return out

def run():
    db=sqlite3.connect(DB);init(db)
    for division,lid in LEAGUES.items():
        for endpoint in (f'league/{lid}/details',f'league/{lid}/standings',f'league/{lid}/matches'):
            try:
                payload=fetch(f'{BASE}/{endpoint}')
                db.execute('INSERT OR REPLACE INTO raw_fetches VALUES(?,?,?,?)',(division,endpoint,datetime.datetime.now(datetime.timezone.utc).isoformat(),json.dumps(payload)))
                if endpoint.endswith('/details'):
                    for eid,name,team in entries_from(payload):
                        db.execute('INSERT OR REPLACE INTO entry_names VALUES(?,?,?,?,?)',(SEASON,division,eid,name,team))
                if endpoint.endswith('/matches'):
                    matches=extract_matches(payload)
                    for gw,mid,h,a,hs,ass in matches:
                        db.execute('INSERT OR REPLACE INTO fixtures VALUES(?,?,?,?,?,?,?,?)',(SEASON,division,gw,mid,h,a,hs,ass))
                    log(db,division,endpoint,'ok',f'{len(matches)} verified finished fixtures')
                else:log(db,division,endpoint,'ok')
                print(division,endpoint,'OK')
            except Exception as ex:
                log(db,division,endpoint,'error',repr(ex));print(division,endpoint,'ERROR',repr(ex))
            db.commit()
    db.close()

if __name__=='__main__':run()
