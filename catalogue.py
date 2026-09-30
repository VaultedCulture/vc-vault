import json,urllib.request,concurrent.futures,time
from pathlib import Path
p=Path('outputs/tcg-vault/catalogue')
def get(path):
 f=p/(path.replace('/','_')+'.json')
 if f.exists():return json.loads(f.read_text(encoding='utf-8'))
 for attempt in range(3):
  try:
   data=json.load(urllib.request.urlopen('https://api.tcgdex.net/v2/en/'+path,timeout=25))
   f.write_text(json.dumps(data),encoding='utf-8');return data
  except Exception:
   if attempt==2:raise
sets=get('sets');print('Catalogue',len(sets),flush=True)
for sid in ['sv03.5','30th','sv08.5']:
 try:
  s=get('sets/'+sid)
  with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex: list(ex.map(lambda c:get('cards/'+c['id']),s['cards']))
  print(s['name'],len(s['cards']),flush=True)
 except Exception as e:print(sid,str(e),flush=True)
