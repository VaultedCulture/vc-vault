from pathlib import Path
p=Path('outputs/tcg-vault/server.py');s=p.read_text()
s=s.replace('from urllib.parse import urlsplit','from urllib.parse import urlsplit')
pos=s.index('\ndef mutate(')
s=s[:pos]+'''
def pokemon_cards(names):
    if not isinstance(names, list) or not 1 <= len(names) <= 12 or any(not isinstance(n,str) or not 2 <= len(n.strip()) <= 50 for n in names):
        raise ValueError('Choose 1–12 Pokémon names')
    names = list(dict.fromkeys(n.strip().casefold() for n in names))
    index = fetch('cards')
    allowed = {s['id'] for s in fetch('sets') if not re.match(r'^(?:[AB]\\d|P-A)',s['id'])}
    candidates = [c for c in index if c['id'].rsplit('-',1)[0] in allowed and any(re.search(r'(?<!\\w)'+re.escape(n)+r'(?!\\w)',c['name'],re.I) for n in names)]
    if len(candidates)>1500: raise ValueError('Too many matches; choose more specific Pokémon names')
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        details=list(ex.map(lambda c:fetch('cards/'+c['id']),candidates))
    details=[c for c in details if c.get('category')=='Pokemon']
    if not details: raise ValueError('No Pokémon cards found. Check the spelling and try again.')
    return list({c['id']:c for c in details}.values())

''' + s[pos:]
s=s.replace("if action == 'track':", """if action == 'custom':
            title=data.get('name','').strip()
            if not 1 <= len(title) <= 80: raise ValueError('Name your checklist (up to 80 characters)')
            mode=data.get('mode','unique')
            if mode not in ('unique','variants'): raise ValueError('Choose a checklist scope')
            found=pokemon_cards(data.get('pokemon'))
            sid='custom-'+secrets.token_hex(8)
            s['tracked'][sid]={'name':title,'mode':mode,'pokemon':data['pokemon'],'cardIds':[x['id'] for x in found]}
        elif action == 'track':""")
s=s.replace("se = fetch('sets/' + sid)","se = {'name':s['tracked'][sid]['name'],'cards':s['tracked'][sid]['cardIds']} if sid.startswith('custom-') and sid in s['tracked'] else fetch('sets/' + sid)")
s=s.replace("s['tracked'][sid] = {'name': se['name'], 'mode': mode}","s['tracked'][sid] = {**s['tracked'].get(sid,{}), 'name': se['name'], 'mode': mode}")
s=s.replace("def set_data(sid):\n    s =", """def set_data(sid):
    if sid.startswith('custom-'):
        item=state()['tracked'].get(sid)
        if not item: raise ValueError('Custom checklist not found')
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
            cs=list(ex.map(lambda cid:fetch('cards/'+cid),item['cardIds']))
        return {'id':sid,'name':item['name'],'cards':cs,'pokemon':item['pokemon'],'serie':{'name':'Custom Pokémon checklist'}}
    s =""")
s=s.replace("mutate(urlsplit(self.path).path.removeprefix('/api/'), d)","""if urlsplit(self.path).path == '/api/pokemon-preview':
                cs=pokemon_cards(d.get('pokemon'))
                return self.send(200, {'cards':cs,'sets':len({c['set']['id'] for c in cs})})
            mutate(urlsplit(self.path).path.removeprefix('/api/'), d)""")
p.write_text(s)
