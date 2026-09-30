"""TCG Vault: single-user, loopback-only collection app. Python 3.10+, no dependencies."""

import argparse, concurrent.futures, json, mimetypes, re, secrets, sqlite3, threading, urllib.request

from datetime import datetime, timezone

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from pathlib import Path

from urllib.parse import urlsplit



ROOT = Path(__file__).resolve().parent

DB = ROOT / 'collection.sqlite3'

TOKEN = secrets.token_urlsafe(32)

LOCK = threading.RLock()



class ClosingConnection(sqlite3.Connection):

    def __exit__(self, *args):

        try:

            return super().__exit__(*args)

        finally:

            self.close()



def connect():

    c = sqlite3.connect(DB, factory=ClosingConnection)

    c.execute('CREATE TABLE IF NOT EXISTS state (id INTEGER PRIMARY KEY, body TEXT NOT NULL)')

    c.execute('CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, body TEXT NOT NULL)')

    c.execute('INSERT OR IGNORE INTO state VALUES (1, ?)', (json.dumps({'owned': {}, 'tracked': {}, 'wishlist': []}),))

    c.commit()

    return c



def state():

    with connect() as c:

        s = json.loads(c.execute('SELECT body FROM state WHERE id=1').fetchone()[0])

        s['canUndo'] = bool(c.execute('SELECT 1 FROM history LIMIT 1').fetchone())

        return s



def fetch(path):

    if not re.fullmatch(r'(sets|cards)(/[a-zA-Z0-9._-]+)?', path):

        raise ValueError('Invalid catalogue identifier')

    f = ROOT / 'catalogue' / (path.replace('/', '_') + '.json')

    if f.exists(): return json.loads(f.read_text(encoding='utf-8'))

    req = urllib.request.Request('https://api.tcgdex.net/v2/en/' + path, headers={'User-Agent': 'TCGVault/1.0'})

    with urllib.request.urlopen(req, timeout=30) as r: data = json.load(r)

    with LOCK:

        f.parent.mkdir(exist_ok=True)

        f.write_text(json.dumps(data), encoding='utf-8')

    return data



def variants(card):

    v = card.get('variants', {})

    return [k for k in ('normal', 'holo', 'reverse', 'firstEdition', 'wPromo') if v.get(k)] or ['unspecified']



def set_data(sid):

    if sid.startswith('custom-'):

        item=state()['tracked'].get(sid)

        if not item: raise ValueError('Custom checklist not found')

        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:

            cs=list(ex.map(lambda cid:fetch('cards/'+cid),item['cardIds']))

        return {'id':sid,'name':item['name'],'cards':cs,'pokemon':item['pokemon'],'serie':{'name':'Custom Pokémon checklist'}}

    s = dict(fetch('sets/' + sid))

    def detail(c): return fetch('cards/' + c['id'])

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:

        s['cards'] = list(ex.map(detail, s['cards']))

    return s



def pokemon_cards(names):

    if not isinstance(names, list) or not 1 <= len(names) <= 12 or any(not isinstance(n,str) or not 2 <= len(n.strip()) <= 50 for n in names):

        raise ValueError('Choose 1–12 Pokémon names')

    names = list(dict.fromkeys(n.strip().casefold() for n in names))

    index = fetch('cards')

    allowed = {s['id'] for s in fetch('sets') if not re.match(r'^(?:[AB]\d|P-A)',s['id'])}

    candidates = [c for c in index if c['id'].rsplit('-',1)[0] in allowed and any(re.search(r'(?<!\w)'+re.escape(n)+r'(?!\w)',c['name'],re.I) for n in names)]

    if len(candidates)>1500: raise ValueError('Too many matches; choose more specific Pokémon names')

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:

        details=list(ex.map(lambda c:fetch('cards/'+c['id']),candidates))

    details=[c for c in details if c.get('category')=='Pokemon']

    if not details: raise ValueError('No Pokémon cards found. Check the spelling and try again.')

    return list({c['id']:c for c in details}.values())





def mutate(action, data):
    custom_cards = pokemon_cards(data.get('pokemon')) if action == 'custom' else None

    with LOCK, connect() as c:

        old = c.execute('SELECT body FROM state WHERE id=1').fetchone()[0]

        s = json.loads(old)

        if action == 'undo':

            row = c.execute('SELECT id,body FROM history ORDER BY id DESC LIMIT 1').fetchone()

            if not row: raise ValueError('Nothing to undo')

            c.execute('UPDATE state SET body=? WHERE id=1', (row[1],))

            c.execute('DELETE FROM history WHERE id=?', (row[0],))

            return

        if action == 'custom':

            title=data.get('name','').strip()

            if not 1 <= len(title) <= 80: raise ValueError('Name your checklist (up to 80 characters)')

            mode=data.get('mode','unique')

            if mode not in ('unique','variants'): raise ValueError('Choose a checklist scope')

            found=custom_cards

            sid='custom-'+secrets.token_hex(8)

            s['tracked'][sid]={'name':title,'mode':mode,'pokemon':data['pokemon'],'cardIds':[x['id'] for x in found]}

        elif action == 'untrack':
            sid=data.get('id','')
            if sid not in s['tracked']: raise ValueError('Checklist not found')
            del s['tracked'][sid]
        elif action == 'track':

            sid = data.get('id', '')

            mode = data.get('mode')

            if mode not in ('unique', 'variants'): raise ValueError('Choose a checklist scope')

            se = {'name':s['tracked'][sid]['name'],'cards':s['tracked'][sid]['cardIds']} if sid.startswith('custom-') and sid in s['tracked'] else fetch('sets/' + sid)

            if not se.get('cards'): raise ValueError('No cards available for this set yet')

            s['tracked'][sid] = {**s['tracked'].get(sid,{}), 'name': se['name'], 'mode': mode}

        elif action == 'batch':

            rows = data.get('rows')

            if not isinstance(rows, list) or not 1 <= len(rows) <= 2000: raise ValueError('Select 1â€“2000 entries')

            operation = data.get('operation', 'add')

            if operation not in ('add', 'set'): raise ValueError('Invalid operation')

            seen = set()

            for row in rows:

                card = fetch('cards/' + row.get('id', ''))

                v = row.get('variant')

                q = row.get('quantity')

                condition = row.get('condition', 'Near mint')

                if v not in variants(card): raise ValueError('This variant is not listed for ' + card['name'])

                if type(q) is not int or q < (1 if operation == 'add' else 0) or q > 999: raise ValueError('Quantity must be a whole number from 1 to 999 (0 to remove)')

                if condition not in ('Near mint', 'Lightly played', 'Moderately played', 'Heavily played', 'Damaged'): raise ValueError('Invalid condition')

                key = card['id'] + '|' + v + '|' + condition

                if key in seen: raise ValueError('Duplicate entry in batch')

                seen.add(key)

                previous = s['owned'].get(key, {}).get('quantity', 0)

                total = q + previous if operation == 'add' else q

                if total > 999: raise ValueError('Maximum 999 copies per entry')

                if total == 0: s['owned'].pop(key, None)

                else:

                    s['owned'][key] = {'id': card['id'], 'setId': card['set']['id'], 'name': card['name'], 'variant': v, 'condition': condition, 'quantity': total}

        elif action == 'wish':

            cid = data.get('id', '')

            fetch('cards/' + cid)

            if cid in s['wishlist']: s['wishlist'].remove(cid)

            else: s['wishlist'].append(cid)

        else: raise ValueError('Unknown action')

        c.execute('INSERT INTO history(body) VALUES (?)', (old,))

        c.execute('DELETE FROM history WHERE id NOT IN (SELECT id FROM history ORDER BY id DESC LIMIT 30)')

        c.execute('UPDATE state SET body=? WHERE id=1', (json.dumps(s),))



class Handler(BaseHTTPRequestHandler):

    def log_message(self, *_): pass

    def send(self, status, data, typ='application/json'):

        raw = json.dumps(data).encode() if typ == 'application/json' else data

        self.send_response(status)

        self.send_header('Content-Type', typ + ('; charset=utf-8' if typ.startswith('text/') else ''))

        self.send_header('Content-Length', str(len(raw)))

        self.send_header('Cache-Control', 'no-store')

        self.send_header('X-Content-Type-Options', 'nosniff')

        self.send_header('Referrer-Policy', 'no-referrer')

        self.send_header('Content-Security-Policy', "default-src 'self'; img-src 'self' https://assets.tcgdex.net https://raw.githubusercontent.com data:; style-src 'self' 'unsafe-inline'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'")

        self.end_headers()

        self.wfile.write(raw)

    def valid_host(self):

        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

    def do_GET(self):

        if not self.valid_host(): return self.send(403, {'error': 'Local access only'})

        path = urlsplit(self.path).path

        try:

            if path == '/api/state': return self.send(200, {**state(), 'token': TOKEN})

            if path == '/api/sets': return self.send(200, fetch('sets'))

            if path.startswith('/api/set/'): return self.send(200, set_data(path.split('/')[-1]))

            if path.startswith('/api/card/'): return self.send(200, fetch('cards/' + path.split('/')[-1]))

            if path == '/api/export': return self.send(200, {'version': 1, 'exported': datetime.now(timezone.utc).isoformat(), **state()})

            files = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css', '/favicon.svg': 'favicon.svg'}

            if path not in files: return self.send(404, {'error': 'Not found'})

            file = ROOT / 'public' / files[path]

            return self.send(200, file.read_bytes(), mimetypes.guess_type(file.name)[0] or 'text/plain')

        except ValueError as e: self.send(400, {'error': str(e)})

        except Exception: self.send(503, {'error': 'The card catalogue is unavailable. Check your internet connection and try again. Saved collection data is safe.'})

    def do_POST(self):

        if not self.valid_host() or self.headers.get('X-Vault-Token') != TOKEN:

            return self.send(403, {'error': 'Reload the app to reconnect securely'})

        origin = self.headers.get('Origin')

        if origin and origin not in (f'http://127.0.0.1:{self.server.server_port}', f'http://localhost:{self.server.server_port}'):

            return self.send(403, {'error': 'Invalid origin'})

        try:

            size = int(self.headers.get('Content-Length', '0'))

            if size > 500000 or size < 2: raise ValueError('Invalid request size')

            d = json.loads(self.rfile.read(size))

            if urlsplit(self.path).path == '/api/pokemon-preview':

                cs=pokemon_cards(d.get('pokemon'))

                return self.send(200, {'cards':cs,'sets':len({c['set']['id'] for c in cs})})

            mutate(urlsplit(self.path).path.removeprefix('/api/'), d)

            self.send(200, state())

        except (ValueError, TypeError, KeyError) as e: self.send(400, {'error': str(e)})

        except Exception: self.send(503, {'error': 'Could not save. Your previous collection is unchanged. Please try again.'})



if __name__ == '__main__':

    p = argparse.ArgumentParser()

    p.add_argument('--port', type=int, default=8765)

    p.add_argument('--db', type=Path, default=DB)

    a = p.parse_args(); DB = a.db

    connect().close()

    print(f'TCG Vault ready at http://127.0.0.1:{a.port}', flush=True)

    ThreadingHTTPServer(('127.0.0.1', a.port), Handler).serve_forever()

