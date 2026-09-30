from pathlib import Path
p=Path('outputs/tcg-vault/public/app.js');s=p.read_text(encoding='utf-8');pos=s.index('function setLogo(')
s=s[:pos]+'''function pokemonArt(s){
 if(!s.pokemon)return '';
 return `<div class="pokemon-portraits">${s.pokemon.map(name=>{const c=s.cards.find(c=>c.name.toLowerCase()===name.toLowerCase())||s.cards.find(c=>c.name.toLowerCase().includes(name.toLowerCase()));const dex=c?.dexId?.[0];return dex?`<figure><img src="https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/${Number(dex)}.png" alt="${esc(name)}" data-pokemon-art data-card-fallback="${esc(c.image?c.image+'/low.webp':'')}" loading="lazy"><figcaption>${esc(name)}</figcaption></figure>`:c?.image?`<figure><img src="${esc(c.image)}/low.webp" alt="${esc(name)}" data-pokemon-art><figcaption>${esc(name)}</figcaption></figure>`:'';}).join('')}</div>`;
}
document.addEventListener('error',e=>{const img=e.target;if(!img.hasAttribute?.('data-pokemon-art'))return;if(img.dataset.cardFallback){img.src=img.dataset.cardFallback;delete img.dataset.cardFallback;}},true);
''' +s[pos:]
s=s.replace("if(img.tagName!=='IMG'||img.dataset.image==='card'||", "if(img.tagName!=='IMG'||img.hasAttribute('data-pokemon-art')||img.dataset.image==='card'||")
s=s.replace('${setLogo(s)?`<img class="set-logo"', '${s.pokemon?pokemonArt(s):setLogo(s)?`<img class="set-logo"')
p.write_text(s,encoding='utf-8')
p=Path('outputs/tcg-vault/public/style.css');s=p.read_text(encoding='utf-8');s+='\n.pokemon-portraits{display:flex;flex-wrap:wrap;gap:12px;margin-bottom:22px}.pokemon-portraits figure{margin:0;text-align:center}.pokemon-portraits img{width:115px;height:115px;object-fit:contain;filter:drop-shadow(0 6px 14px #a855f733)}.pokemon-portraits figcaption{font-size:12px;color:#b8c4d9;margin-top:4px}.set-info .pokemon-portraits{margin:0;flex-shrink:0}.set-info .pokemon-portraits img{width:85px;height:85px}\n';p.write_text(s,encoding='utf-8')
p=Path('outputs/tcg-vault/server.py');s=p.read_text(encoding='utf-8').replace("img-src 'self' https://assets.tcgdex.net data:","img-src 'self' https://assets.tcgdex.net https://raw.githubusercontent.com data:");p.write_text(s,encoding='utf-8')
