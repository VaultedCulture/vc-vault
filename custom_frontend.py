from pathlib import Path
p=Path('outputs/tcg-vault/public/app.js');s=p.read_text(encoding='utf-8')
s=s.replace("function missing(c){return S.tracked[c.set.id]?.mode", "function missing(c){return (view==='browse'?S.tracked[activeSet.id]:S.tracked[c.set.id])?.mode")
s=s.replace("${s.cards.length} numbered cards · ${esc(s.releaseDate||'Release date unavailable')}","${s.cards.length} cards · ${s.pokemon?'Across '+new Set(s.cards.map(c=>c.set.id)).size+' sets':esc(s.releaseDate||'Release date unavailable')}")
s=s.replace("const setNote = s =>", "const setNote = s => s.pokemon ? 'English catalogue matches for '+s.pokemon.join(' + ')+'. Includes named forms. Special stamps and unlisted releases may be absent.' :")
s=s.replace("${S.tracked[c.set.id]?.mode==='variants'?", "${(view==='browse'?S.tracked[activeSet.id]:S.tracked[c.set.id])?.mode==='variants'?")
s=s.replace("rows.push([s.name,c.localId,c.name", "rows.push([c.set.name,c.localId,c.name")
s=s.replace("function renderMasters(){const entries", "function renderMasters(){const entries")
s=s.replace("$('#content').innerHTML=`<div class=\"master-grid\">", "$('#content').innerHTML=`<div class=\"results-line\"><p>Expansion sets and your favourite Pokémon, together.</p><button class=\"primary\" data-action=\"custom\">＋ Custom Pokémon set</button></div><div class=\"master-grid\">")
s=s.replace("'Find a set to master');return;", "'Find a set to master')+'<button class=\"primary\" data-action=\"custom\">＋ Custom Pokémon set</button>';return;")
s=s.replace("case 'export-missing':", "case 'custom':customSet();break;case 'export-missing':")
s=s.replace("<div class=\"set-list\" id=\"set-list\"></div>","<button class=\"primary\" data-action=\"custom\" style=\"margin-bottom:16px\">＋ Custom Pokémon set</button><div class=\"set-list\" id=\"set-list\"></div>")
pos=s.index('function track()')
s=s[:pos]+'''function customSet(){
 dialog('Create a Pokémon master set.','Bring your favourites together across the English catalogue.',`<label class="field">Checklist name<input id="custom-name" value="Ponyta & Rapidash" maxlength="80"></label><label class="field">Pokémon names, separated by commas<input id="custom-pokemon" value="Ponyta, Rapidash" placeholder="Ponyta, Rapidash"></label><label class="field">Checklist scope<select id="custom-mode"><option value="unique">One of each card</option><option value="variants">Standard prints, including reverse holos</option></select></label><p class="price-note">Matches Pokémon card names, including regional forms, ex/V cards and named variants. English catalogue only; special stamps and unlisted releases may be absent. Your owned cards count automatically.</p><div id="custom-preview" aria-live="polite"></div>`,`<button data-close>Cancel</button><button class="primary" id="preview-custom">Find cards across all sets</button><button class="primary" id="create-custom" hidden>Create checklist</button>`);
 let found=null;
 const invalidate=()=>{found=null;$('#create-custom').hidden=true;$('#custom-preview').textContent='';};
 $('#custom-pokemon').oninput=invalidate;
 $('#preview-custom').onclick=async e=>{e.target.disabled=true;$('#create-custom').hidden=true;$('#custom-preview').textContent='Searching the catalogue and loading card details…';try{const pokemon=$('#custom-pokemon').value.split(',').map(x=>x.trim()).filter(Boolean);const data=await api('pokemon-preview',{pokemon});found=pokemon;$('#custom-preview').innerHTML=`<div class="notice"><b>${data.cards.length} cards across ${data.sets} sets</b><p>${data.cards.filter(c=>qty(c.id)).length} already owned.</p></div><div class="custom-matches">${data.cards.map(c=>`<div><b>${esc(c.name)}</b><small>${esc(c.set.name)} · #${esc(c.localId)}</small></div>`).join('')}</div>`;$('#create-custom').hidden=false;}catch(err){$('#custom-preview').textContent=err.message;}finally{e.target.disabled=false;}};
 $('#create-custom').onclick=async e=>{if(!found)return;e.target.disabled=true;try{const before=new Set(Object.keys(S.tracked));await save('custom',{name:$('#custom-name').value,pokemon:found,mode:$('#custom-mode').value});const id=Object.keys(S.tracked).find(id=>!before.has(id));modal.close();await navigate('browse',id);notify('Your Pokémon master set is ready.');}catch(err){notify(err.message);e.target.disabled=false;}};
}
''' +s[pos:]
p.write_text(s,encoding='utf-8')
p=Path('outputs/tcg-vault/public/style.css');s=p.read_text();s+='\n.custom-matches{max-height:240px;overflow:auto;margin-top:14px}.custom-matches>div{padding:10px;border-bottom:1px solid #30384d;display:flex;justify-content:space-between;gap:14px}.custom-matches small{color:var(--muted)}\n';p.write_text(s)
