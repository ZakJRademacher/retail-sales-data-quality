import csv, importlib.util, sqlite3, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('pipeline',ROOT/'src/pipeline.py')
p=importlib.util.module_from_spec(spec); spec.loader.exec_module(p)

def row(**kw):
    d=dict(zip(p.FIELDS,['536365','85123A','TEST PRODUCT','6','12/1/2010 8:26','2.55','17850','United Kingdom']))
    d.update(kw); return d

class CleaningTests(unittest.TestCase):
    def test_sale_amount(self):
        self.assertEqual(p.normalize(row(),2)['amount_pence'],1530)
    def test_cancel_preserved(self):
        d=p.normalize(row(InvoiceNo='c536365',Quantity='-6'),2)
        self.assertEqual((d['kind'],d['amount_pence']),('cancellation',-1530))
    def test_sign_mismatch_excluded(self):
        self.assertEqual(p.normalize(row(Quantity='-1'),2)['reason'],'invoice_quantity_sign_mismatch')
    def test_positive_cancellation_excluded(self):
        self.assertEqual(p.normalize(row(InvoiceNo='C123'),2)['kind'],'excluded')
    def test_missing_customer_retained(self):
        self.assertEqual(p.normalize(row(CustomerID=''),2)['kind'],'sale')
    def test_nonfinite_price(self):
        self.assertEqual(p.normalize(row(UnitPrice='NaN'),2)['reason'],'invalid_numeric')
    def test_zero_price_excluded(self):
        self.assertEqual(p.normalize(row(UnitPrice='0'),2)['reason'],'nonpositive_price')
    def test_fractional_quantity(self):
        self.assertEqual(p.normalize(row(Quantity='1.5'),2)['reason'],'invalid_numeric')
    def test_invalid_date(self):
        self.assertEqual(p.normalize(row(InvoiceDate='2/30/2011 9:00'),2)['reason'],'invalid_date')
    def test_us_date_format(self):
        self.assertTrue(p.normalize(row(InvoiceDate='12/9/2011 8:26'),2)['invoice_date'].startswith('2011-12-09'))
    def test_subpenny_rounding(self):
        self.assertEqual(p.normalize(row(Quantity='3',UnitPrice='.335'),2)['amount_pence'],101)
    def test_large_order_not_arbitrarily_trimmed(self):
        self.assertEqual(p.normalize(row(Quantity='80000'),2)['kind'],'sale')
    def test_end_to_end_repeats_and_reconciliation(self):
        with tempfile.TemporaryDirectory(dir=ROOT/'tests') as temp:
            dest=Path(temp); f=dest/'input.csv'
            records=[row(),row(),row(InvoiceNo='C1',Quantity='-1'),row(Quantity='-2'),row(UnitPrice='0')]
            with f.open('w',newline='',encoding='latin1') as stream:
                w=csv.DictWriter(stream,p.FIELDS); w.writeheader(); w.writerows(records)
            s=p.run(f,dest/'out'); m=s['metrics']
            self.assertNotIn('retrieved',s)
            self.assertTrue(s['processed_at_utc'].endswith('+00:00'))
            self.assertEqual(s['reference_snapshot_retrieved'],'2026-10-15')
            self.assertEqual(m['exact_repeat_rows'],1)
            self.assertEqual(m['net_pence'],2805)
            self.assertEqual(m['deduplicated_net_pence'],1275)
            self.assertTrue(all(s['checks'].values()))
            self.assertEqual(m['input_rows'],5)
            # Same output path can be rebuilt without accumulating duplicate records.
            second=p.run(f,dest/'out'); self.assertEqual(second['metrics'],s['metrics'])

if __name__=='__main__': unittest.main(verbosity=2)
