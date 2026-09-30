from pathlib import Path
import base64,re,json
root=Path('outputs/tcg-vault/public')
p=root/'index.html';s=p.read_text(encoding='utf-8');logo=base64.b64encode(Path(r'C:/Users/leann/Desktop/VC-vault.png').read_bytes()).decode();s=re.sub(r'<a class="brand".*?</a>', '<a class="brand" href="#browse" aria-label="VC Vault home"><img class="vc-logo" src="data:image/png;base64,'+logo+'" alt="VC Vault — The Collector’s Companion"></a>',s,count=1);s=s.replace('TCG Vault ·','VC Vault ·');p.write_text(s,encoding='utf-8')
p=root/'app.js';s=p.read_text(encoding='utf-8');marker='function image(c,'
rarity='''function rarityBadge(c){
 const r=(c.rarity||'').toLowerCase().trim();
 const modern=/^(sv|me|30th)/.test(c.set?.id||'');
 let count=0,tone='ink',shape='star';
 if(r==='common'){count=1;shape='circle';}
 else if(r==='uncommon'){count=1;shape='diamond';}
 else if(r==='rare'||r==='rare holo'){count=1;}
 else if(modern){const m={'double rare':[2,'ink'],'ultra rare':[2,'silver'],'illustration rare':[1,'gold'],'special illustration rare':[2,'gold'],'hyper rare':[3,'gold']};if(m[r]) [count,tone]=m[r];}
 if(!count)return '';
 const shapes={star:'<path d="m12 1.8 3.1 6.3 7 .9-5 4.9 1.2 7-6.3-3.3-6.3 3.3 1.2-7-5-4.9 7-.9z"/>',circle:'<circle cx="12" cy="12" r="8"/>',diamond:'<path d="m12 2 10 10-10 10L2 12z"/>'};
 const label=count+' '+tone+' '+(shape==='star'?'star'+(count===1?'':'s'):shape);
 return `<span class="rarity-symbols ${tone}" role="img" aria-label="${esc(c.rarity)}: ${label}" title="${esc(c.rarity)}">${Array.from({length:count},()=>`<svg viewBox="0 0 24 24" aria-hidden="true">${shapes[shape]}</svg>`).join('')}</span>`;
}
'''
s=s.replace(marker,rarity+marker);s=s.replace('<div class="card-meta">${esc(c.rarity', '<div class="card-meta">${rarityBadge(c)}<span>${esc(c.rarity');s=s.replace("${esc(c.set.name)}</div>${S.tracked", "${esc(c.set.name)}</span></div>${S.tracked");s=s.replace('<div class="kicker">IN YOUR VAULT</div>','<div class="detail-rarity">${rarityBadge(c)}<span>${esc(c.rarity||\'Rarity unavailable\')}</span></div><div class="kicker">IN YOUR VAULT</div>');p.write_text(s,encoding='utf-8')
p=root/'style.css';s=p.read_text(encoding='utf-8')
colors={'#101211':'#0b1020','#181c19':'#191f30','#2b312b':'#2b3347','#a0aaa0':'#99a9c1','#f2f5ee':'#f2f4fb','#c0f878':'#bc83ff','#232d1d':'#2b1d45','#222823':'#20283b','#657a54':'#a45ae1','#2a3428':'#302440','#141714':'#060a17','#7a887b':'#8292ac','#28321f':'#063041','#394c29':'#07647c','#879184':'#8e9cb4','#4b594b':'#485571','#d0d7cd':'#ced7ec','#afc79e':'#63d4e5','#8b9888':'#8a9bb7','#3d4d31':'#60418c','#34472980':'#753c9a80','#1c241a':'#241a3b','#afbca6':'#b2a8cf','#3b4535':'#343149','#181d19':'#141b2d','#7c887d':'#8493ad','#2b3823':'#33204e','#425535':'#674398','#191e1a':'#192032','#5e7251':'#8e62ba','#222c1c':'#302044','#9ba792':'#9aabc5','#869184':'#91a0ba','#2a3a21':'#143b49','#30392e':'#293049','#1c231b':'#141b30','#323d2c':'#32304d','#1a2118':'#151c30','#5a6e49':'#716389','#a9bb9b':'#b5a8d2','#93a08e':'#98aac6','#b6c1b0':'#bac8e0','#263320f5':'#241b3ef5','#739f4e':'#a55ee2','#46553a':'#694790','#181e18':'#141b2c','#b5c4a9':'#c3b4dd','#232e1e':'#28203e','#3e5030':'#624384','#8bb956':'#b272ec','#26321e':'#302047','#44513c':'#4f426b','#d1f4b0':'#dac3fa','#1b2a13':'#29133e','#879080':'#8e9bb4','#232a22':'#252b40','#c2b7a4':'#b8b5cd','#a9b99a':'#b4a8cc'}
for a,b in colors.items():s=s.replace(a,b)
s+='''
/* VC Vault brand: midnight navy, violet and cyan. */
.brand{display:block;margin:-10px -12px 0}.vc-logo{display:block;width:100%;height:auto;mix-blend-mode:screen}.nav-label{margin-top:32px}
.primary{background:linear-gradient(110deg,#a449f0,#b74cf0);border-color:#b25aef;color:#fff}.primary:hover{background:linear-gradient(110deg,#b65cff,#ca65ff);border-color:#d093ff;color:#fff}
nav button.active{color:#18d6ee}.save-dot:before{color:#1ed0d8}.metric .lime{color:#ca93ff}.progress>i{background:linear-gradient(90deg,#a855f7,#d05dcc)}
.set-hero{background:linear-gradient(115deg,#2c1d49,#321d3c 55%,#29204c);border-color:#603788}.card.selected{border-color:#bd79ff;box-shadow:0 0 0 1px #bd79ff}.status-pill.owned{color:#66e0ef;background:#073749}
.rarity-symbols{display:inline-flex;align-items:center;gap:2px;flex-shrink:0;vertical-align:middle;line-height:1;padding:3px 5px;border-radius:5px;background:#101525;border:1px solid #39415a}
.rarity-symbols svg{width:14px;height:14px;fill:currentColor}.rarity-symbols.gold{color:#f5c952}.rarity-symbols.silver{color:#e0e7f2}.rarity-symbols.ink{color:#111827;background:#b4bfd3;border-color:#b4bfd3}
.card-meta{display:flex;align-items:center;flex-wrap:wrap;gap:6px}.detail-rarity{display:flex;align-items:center;gap:8px;margin-bottom:20px;color:#bdc8dc;font-size:12px}
@media(max-width:750px){.brand{width:245px;max-width:85%;margin:-8px 0 -5px}}
'''
p.write_text(s,encoding='utf-8')
(root/'favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><defs><linearGradient id="v" x2="1" y2="1"><stop stop-color="#c657ff"/><stop offset="1" stop-color="#00ddf4"/></linearGradient></defs><rect width="48" height="48" rx="12" fill="#0b1020"/><text x="24" y="32" text-anchor="middle" font-family="Arial" font-weight="bold" font-size="26" fill="url(#v)">VC</text></svg>',encoding='utf-8')
print('Brand, palette and rarity badges updated')
