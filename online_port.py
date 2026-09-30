from pathlib import Path
import shutil,json,sqlite3,re
root=Path('outputs/vc-vault-online');old=Path('outputs/tcg-vault')
for n in ['app.js','style.css','favicon.svg']:shutil.copy2(old/'public'/n,root/'public'/n)
# Public catalogue metadata only, never collection state.
shutil.copytree(old/'catalogue',root/'public'/'catalogue',dirs_exist_ok=True)
c=sqlite3.connect(old/'collection.sqlite3');data=json.loads(c.execute('select body from state where id=1').fetchone()[0]);c.close()
(root/'lib'/'initial-vault.json').write_text(json.dumps(data),encoding='utf-8')
print('Migration snapshot:',sum(r['quantity'] for r in data['owned'].values()),'cards;',len(data['tracked']),'checklists')
h=(old/'public'/'index.html').read_text(encoding='utf-8');h=h.replace('Saved on this computer','Shared online collection').replace('Local collection','Private shared vault');h=h.replace('</header>','<a class="signout" href="/signout-with-chatgpt?return_to=/">Sign out</a></header>');(root/'lib'/'vault.html').write_text(h,encoding='utf-8')
p=root/'.openai'/'hosting.json';v=json.loads(p.read_text());v['d1']='DB';p.write_text(json.dumps(v,indent=2))
(root/'db'/'schema.ts').write_text('''import { sqliteTable, integer, text } from "drizzle-orm/sqlite-core";
export const vault = sqliteTable("vault", { id:integer("id").primaryKey(),body:text("body").notNull(),revision:integer("revision").notNull().default(0) });
export const history = sqliteTable("vault_history", {id:integer("id").primaryKey({autoIncrement:true}),body:text("body").notNull(),actor:text("actor").notNull()});
''')
p=root/'public'/'app.js';s=p.read_text(encoding='utf-8');s=s.replace("headers:body?{'Content-Type':'application/json','X-Vault-Token':token}:{},body:body?JSON.stringify(body)","headers:body?{'Content-Type':'application/json','X-Vault-Token':token}:{},body:body?JSON.stringify({...body,revision:S.revision})")
s=s.replace("S=d;catalogue=", "S=d;catalogue=")
s+='''\nlet syncBusy=false;async function syncVault(){if(syncBusy||modal.open||selected.size||document.hidden)return;syncBusy=true;try{const d=await api('state');if(d.revision!==S.revision){token=d.token;delete d.token;S=d;sets.clear();await navigate(view,activeSet?.id);notify('Shared collection updated.');}}catch{}finally{syncBusy=false;}}setInterval(syncVault,15000);window.addEventListener('focus',syncVault);
if(document.modelContext?.registerTool)document.modelContext.registerTool({name:'read_collection_summary',description:'Read counts from the shared Pokémon collection.',inputSchema:{type:'object',properties:{},additionalProperties:false},annotations:{readOnlyHint:true},execute:()=>({ownedCopies:Object.values(S.owned).reduce((n,x)=>n+x.quantity,0),checklists:Object.values(S.tracked).map(x=>x.name),wishlist:S.wishlist.length})});
''';p.write_text(s,encoding='utf-8')
p=root/'public'/'style.css';s=p.read_text(encoding='utf-8')+'\n.signout{font-size:12px;color:#b8c4d9;margin-left:16px;white-space:nowrap}@media(max-width:750px){.set-info{flex-wrap:wrap}.master-grid{grid-template-columns:1fr}.pokemon-portraits img{width:95px;height:95px}.signout{font-size:11px}}';p.write_text(s,encoding='utf-8')
(root/'app'/'page.tsx').write_text('export default function Home(){return <main>VC Vault — opening your shared collection…</main>;}')
p=root/'app'/'layout.tsx';s=p.read_text().replace('Starter Project','VC Vault').replace('A clean starting point for building your site.','Your private shared Pokémon collection.');p.write_text(s,encoding='utf-8')
