from pathlib import Path
p=Path('outputs/tcg-vault/server.py');s=p.read_text(encoding='utf-8');s=s.replace("elif action == 'track':", """elif action == 'untrack':
            sid=data.get('id','')
            if sid not in s['tracked']: raise ValueError('Checklist not found')
            del s['tracked'][sid]
        elif action == 'track':""");p.write_text(s,encoding='utf-8')
p=Path('outputs/tcg-vault/public/app.js');s=p.read_text(encoding='utf-8');s=s.replace('<button data-set="${esc(id)}">Open checklist →</button>','<button data-set="${esc(id)}">Open checklist →</button><button class="remove-set" data-untrack="${esc(id)}">Remove set</button>');s=s.replace("const se=e.target.closest('[data-set]');", """if(b?.dataset.untrack){const id=b.dataset.untrack;dialog('Remove this checklist?',S.tracked[id].name,'<p>Your owned cards and wishlist will stay in your collection. Only this set’s checklist will be removed. You can Undo this change.</p>','<button data-close>Keep set</button><button class="primary" id="confirm-untrack">Remove checklist</button>');$('#confirm-untrack').onclick=async ev=>{ev.target.disabled=true;try{await save('untrack',{id});modal.close();await navigate('master');notify('Checklist removed. Owned cards kept. Undo is available.');}catch(err){notify(err.message);ev.target.disabled=false;}};return;}const se=e.target.closest('[data-set]');""");p.write_text(s,encoding='utf-8')
p=Path('outputs/tcg-vault/public/style.css');s=p.read_text(encoding='utf-8')+'\n.master-tile .remove-set{background:transparent;color:#b6bfd2;border:0;margin-top:8px;padding:8px}.master-tile .remove-set:hover{color:#ffb4c0;background:#392538}\n';p.write_text(s,encoding='utf-8')
p=Path('outputs/tcg-vault/test_server.py');s=p.read_text();pos=s.index('    def test_path_traversal_rejected');s=s[:pos]+'''    def test_untrack_keeps_cards_and_undo_restores_checklist(self):
        server.mutate('track',{'id':'sv03.5','mode':'unique'})
        server.mutate('batch',{'rows':[self.row()]})
        before=server.state()
        server.mutate('untrack',{'id':'sv03.5'})
        self.assertNotIn('sv03.5',server.state()['tracked'])
        self.assertEqual(server.state()['owned'],before['owned'])
        server.mutate('undo',{})
        self.assertEqual(server.state()['tracked'],before['tracked'])
        self.assertEqual(server.state()['owned'],before['owned'])
''' +s[pos:];p.write_text(s)
