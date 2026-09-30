import tempfile
import unittest
from pathlib import Path
import server

class CollectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        server.DB = Path(self.temp.name) / 'test.sqlite3'
    def tearDown(self):
        self.temp.cleanup()
    def row(self, variant='normal', quantity=1):
        return {'id':'sv03.5-001','variant':variant,'quantity':quantity,'condition':'Near mint'}
    def test_tracking_does_not_mark_owned(self):
        server.mutate('track', {'id':'sv03.5','mode':'variants'})
        self.assertEqual(server.state()['owned'], {})
        self.assertEqual(server.state()['tracked']['sv03.5']['mode'], 'variants')
    def test_batch_counts_variants_separately(self):
        server.mutate('batch', {'rows':[self.row(quantity=3),self.row('reverse',2)]})
        entries=list(server.state()['owned'].values())
        self.assertEqual(sum(x['quantity'] for x in entries),5)
        self.assertEqual(len(entries),2)
    def test_batch_is_atomic(self):
        with self.assertRaises(ValueError):
            server.mutate('batch', {'rows':[self.row(),self.row('holo')]})
        self.assertEqual(server.state()['owned'],{})
    def test_duplicates_increment_and_undo_restores(self):
        server.mutate('batch', {'rows':[self.row(quantity=2)]})
        server.mutate('batch', {'rows':[self.row(quantity=3)]})
        self.assertEqual(next(iter(server.state()['owned'].values()))['quantity'],5)
        server.mutate('undo', {})
        self.assertEqual(next(iter(server.state()['owned'].values()))['quantity'],2)
    def test_invalid_quantities_rejected(self):
        for q in [0,-1,1.5,True,1000]:
            with self.assertRaises(ValueError):server.mutate('batch', {'rows':[self.row(quantity=q)]})
        self.assertEqual(server.state()['owned'],{})
    def test_remove_last_copy(self):
        server.mutate('batch', {'rows':[self.row()]})
        server.mutate('batch', {'operation':'set','rows':[self.row(quantity=0)]})
        self.assertEqual(server.state()['owned'],{})
    def test_data_persisted_across_connections(self):
        server.mutate('track',{'id':'sv03.5','mode':'unique'})
        with server.connect() as c:
            self.assertIn('sv03.5',c.execute('SELECT body FROM state WHERE id=1').fetchone()[0])
    def test_untrack_keeps_cards_and_undo_restores_checklist(self):
        server.mutate('track',{'id':'sv03.5','mode':'unique'})
        server.mutate('batch',{'rows':[self.row()]})
        before=server.state()
        server.mutate('untrack',{'id':'sv03.5'})
        self.assertNotIn('sv03.5',server.state()['tracked'])
        self.assertEqual(server.state()['owned'],before['owned'])
        server.mutate('undo',{})
        self.assertEqual(server.state()['tracked'],before['tracked'])
        self.assertEqual(server.state()['owned'],before['owned'])
    def test_path_traversal_rejected(self):
        with self.assertRaises(ValueError):server.fetch('cards/../../file')

class CustomSetTests(unittest.TestCase):
    def test_custom_checklist_preserves_collection_and_undo(self):
        original=server.DB
        with tempfile.TemporaryDirectory() as tmp:
            server.DB=Path(tmp)/'test.sqlite3'
            try:
                server.mutate('custom',{'name':'Ponyta & Rapidash','pokemon':['Ponyta','Rapidash'],'mode':'variants'})
                saved=server.state();sid=next(iter(saved['tracked']))
                self.assertEqual(saved['owned'],{})
                cards=server.set_data(sid)['cards']
                self.assertGreater(len(cards),50)
                self.assertEqual(len(cards),len({c['id'] for c in cards}))
                self.assertTrue(any(c['name']=='Galarian Ponyta' for c in cards))
                self.assertFalse(any(c['id'].startswith('A1') for c in cards))
                server.mutate('track',{'id':sid,'mode':'unique'})
                self.assertEqual(server.state()['tracked'][sid]['cardIds'],saved['tracked'][sid]['cardIds'])
                server.mutate('undo',{})
                self.assertEqual(server.state()['tracked'][sid]['mode'],'variants')
                server.mutate('undo',{})
                self.assertEqual(server.state()['tracked'],{})
            finally:server.DB=original

if __name__=='__main__':unittest.main()
