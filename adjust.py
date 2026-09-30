import urllib.request,base64
from pathlib import Path
u='https://www.pokebeach.com/news/2026/06/Pokemon_TCG_30th_Celebration_Vertical_Logo-2048x1790.png'
r=urllib.request.urlopen(urllib.request.Request(u,headers={'User-Agent':'Mozilla/5.0'}),timeout=20).read()
Path('work/30th-logo.png').write_bytes(r)
p=Path('outputs/tcg-vault/public/app.js');s=p.read_text(encoding='utf-8')
logo='data:image/png;base64,'+base64.b64encode(r).decode()
s=s.replace("const titles =", "const anniversaryLogo = '"+logo+"';\nconst setLogo = s => (s.id==='30th'||s.id==='30th-c') ? anniversaryLogo : (s.logo ? s.logo+'.webp' : '');\nconst setNote = s => s.id==='30th-c' ? 'Classic reprint subset · tracked separately from the main set' : s.id==='30th' ? 'Main set · Classic Collection tracked separately' : '';\nconst titles =")
s=s.replace("s.logo?`<img class=\"set-logo\" src=\"${esc(s.logo)}.webp\"", "setLogo(s)?`<img class=\"set-logo\" src=\"${esc(setLogo(s))}\"")
s=s.replace("s.logo?`<img src=\"${esc(s.logo)}.webp\"", "setLogo(s)?`<img src=\"${esc(setLogo(s))}\"")
s=s.replace("${s.cardCount.total} cards · ${esc(s.id)}${S.tracked[s.id]?' · Tracking':''}</small>","${s.cardCount.total} cards · ${esc(s.id)}${S.tracked[s.id]?' · Tracking':''}</small>${setNote(s)?`<small class=\"set-description\">${setNote(s)}</small>`:''}")
s=s.replace("<h2>${esc(t.name)}</h2><p>","<h2>${esc(t.name)}</h2>${setNote(s)?`<small class=\"set-description\">${setNote(s)}</small>`:''}<p>")
s=s.replace("<p>${s.cards.length} numbered cards · ${esc(s.releaseDate||'Release date unavailable')}</p>","<p>${s.cards.length} numbered cards · ${esc(s.releaseDate||'Release date unavailable')}</p>${setNote(s)?`<small class=\"set-description\">${setNote(s)}</small>`:''}")
p.write_text(s,encoding='utf-8')
p=Path('outputs/tcg-vault/public/style.css');s=p.read_text(encoding='utf-8').replace('.card-art.missing{filter:saturate(.72);opacity:.83}', '.card-art.missing{filter:grayscale(1);opacity:.38}')
s+='\n.master-tile .set-logo{display:block;width:150px;height:100px;object-position:left center;margin-bottom:20px}.master-tile{display:flex;flex-direction:column}.master-tile>button{margin-top:auto}.master-tile>small{margin-bottom:20px}.set-description{display:block;color:#a9b99a;font-size:11px;margin-top:6px;line-height:1.5}.set-choice .set-description{font-size:10px;max-width:370px}\n'
p.write_text(s,encoding='utf-8')
print('Updated logo, missing artwork style and subset labels. Logo bytes:',len(r))
