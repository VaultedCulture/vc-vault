import json,urllib.request,base64,concurrent.futures
from pathlib import Path
sets=json.loads(Path('outputs/tcg-vault/catalogue/sets.json').read_text());src=json.loads(Path('work/logo-sources.json').read_text());by={s['name'].lower():s for s in src}
fix={}
def one(s):
 if s.get('logo') and s['id']!='xy3':return
 item=by.get(s['name'].lower())
 if item:
  try:
   data=urllib.request.urlopen(item['images']['logo'],timeout=20).read();fix[s['id']]='data:image/png;base64,'+base64.b64encode(data).decode()
  except Exception:pass
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:list(ex.map(one,sets))
p=Path('outputs/tcg-vault/public/app.js');s=p.read_text(encoding='utf-8');start=s.index('const setLogo =');end=s.index('\n',start)
parents={'mep':'me01','mee':'me01','svp':'sv01','sve':'sv01','swsh12.5gg':'swsh12.5','swsh12tg':'swsh12','swsh11tg':'swsh11','swsh10tg':'swsh10','swsh9tg':'swsh9','cel25cc':'cel25','swsh4.5sv':'swsh4.5','sma':'sm115','rc':'bw11','xya':'xy1'}
new='const logoOverrides = '+json.dumps(fix)+';\nconst logoParents = '+json.dumps(parents)+''';
function fallbackLogo(s){const label=s.name.includes("McDonald")?"McDonald's":s.name.includes('trainer Kit')?'TRAINER KIT':s.pokemon?'POKÉMON':s.name;const sub=s.pokemon?s.pokemon.join(' + '):s.id.toUpperCase();return 'data:image/svg+xml,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="240" height="110" viewBox="0 0 240 110"><rect x="2" y="2" width="236" height="106" rx="16" fill="#20283b" stroke="#aa66ee" stroke-width="3"/><text x="120" y="47" text-anchor="middle" fill="#f4eaff" font-family="Arial" font-weight="bold" font-size="${label.length>19?13:19}">${esc(label)}</text><text x="120" y="78" text-anchor="middle" fill="#61dcea" font-family="Arial" font-size="13">${esc(sub)}</text></svg>`);}
function setLogo(s){if(s.id==='30th'||s.id==='30th-c')return anniversaryLogo;if(logoOverrides[s.id])return logoOverrides[s.id];const parent=logoParents[s.id]|| (s.id.startsWith('tk-xy-')?'xy1':s.id.startsWith('tk-sm-')?'sm1':null);const p=parent&&catalogue.find(x=>x.id===parent);return s.logo?s.logo+'.webp':p?.logo?p.logo+'.webp':fallbackLogo(s);}
document.addEventListener('error',e=>{const img=e.target;if(img.tagName!=='IMG'||img.dataset.image==='card'||!img.closest('.set-choice,.set-hero,.master-tile'))return;const wrap=img.closest('[data-set]');const id=wrap?.dataset.set;const s=catalogue.find(x=>x.id===id)||{id:'SET',name:'Pokémon TCG'};if(!img.dataset.fallback){img.dataset.fallback='1';img.src=fallbackLogo(s);}},true);
'''
s=s[:start]+new+s[end:];p.write_text(s,encoding='utf-8');print('Downloaded logos:',list(fix))
p=Path('outputs/tcg-vault/public/style.css');s=p.read_text(encoding='utf-8');s+='\n.custom-matches{max-height:240px;overflow:auto;margin-top:14px}.custom-matches>div{padding:10px;border-bottom:1px solid #30384d;display:flex;justify-content:space-between;gap:14px}.custom-matches small{color:var(--muted)}\n';p.write_text(s,encoding='utf-8')
