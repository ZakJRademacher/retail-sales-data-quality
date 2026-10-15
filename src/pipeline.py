"""Reproducible Kaggle retail audit. Python 3.10+, standard library only."""
from __future__ import annotations
import argparse, csv, hashlib, json, sqlite3
from collections import Counter
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

FIELDS = ['InvoiceNo','StockCode','Description','Quantity','InvoiceDate','UnitPrice','CustomerID','Country']
ROOT = Path(__file__).resolve().parents[1]

def normalize(raw: dict, row_id: int) -> dict:
    """Keep missing customer IDs; reject unvalued/ambiguous lines, never guess."""
    out = dict(row_id=row_id, invoice=raw['InvoiceNo'].strip().upper(),
               sku=raw['StockCode'].strip().upper(), description=raw['Description'].strip(),
               country=raw['Country'].strip(), customer=raw['CustomerID'].strip() or None,
               invoice_date=None, quantity=None, unit_price=None, amount_pence=None,
               kind='excluded', reason=None)
    try:
        q = Decimal(raw['Quantity'].strip())
        p = Decimal(raw['UnitPrice'].strip())
        if not q.is_finite() or not p.is_finite() or q != q.to_integral_value():
            raise ValueError('nonfinite or fractional quantity')
        out['quantity'] = int(q)
        out['unit_price'] = str(p)
        out['amount_pence'] = int((q*p*100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError, OverflowError):
        out['reason'] = 'invalid_numeric'
    try:
        out['invoice_date'] = datetime.strptime(raw['InvoiceDate'].strip(), '%m/%d/%Y %H:%M').isoformat(sep=' ')
    except ValueError:
        out['reason'] = out['reason'] or 'invalid_date'
    if not out['invoice'] or not out['sku'] or not out['country']:
        out['reason'] = out['reason'] or 'missing_required_key'
    if out['reason']:
        return out
    if p <= 0:
        out['reason'] = 'nonpositive_price'
    elif q == 0:
        out['reason'] = 'zero_quantity'
    elif (out['invoice'].startswith('C') and q > 0) or (not out['invoice'].startswith('C') and q < 0):
        out['reason'] = 'invoice_quantity_sign_mismatch'
    else:
        out['kind'] = 'cancellation' if q < 0 else 'sale'
    return out

def export_query(db, query, dest):
    cur = db.execute(query)
    columns = [x[0] for x in cur.description]
    rows = [dict(zip(columns, row)) for row in cur.fetchall()]
    with dest.open('w', newline='', encoding='utf-8-sig') as f:
        w = csv.DictWriter(f, columns); w.writeheader(); w.writerows(rows)
    return rows

def run(input_path: Path, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    db_path = output/'retail.sqlite'
    # Rebuild only the named generated database, never touch input.
    db = sqlite3.connect(db_path)
    db.executescript('DROP TABLE IF EXISTS lines; DROP TABLE IF EXISTS raw_rows;')
    db.execute('''CREATE TABLE raw_rows(row_id INTEGER PRIMARY KEY, raw_json TEXT NOT NULL,
        fingerprint TEXT NOT NULL, is_repeat INTEGER NOT NULL CHECK(is_repeat IN (0,1)))''')
    db.execute('''CREATE TABLE lines(row_id INTEGER PRIMARY KEY REFERENCES raw_rows(row_id),
        invoice TEXT, sku TEXT, description TEXT, country TEXT, customer TEXT,
        invoice_date TEXT, quantity INTEGER, unit_price TEXT, amount_pence INTEGER,
        kind TEXT NOT NULL CHECK(kind IN ('sale','cancellation','excluded')), reason TEXT)''')
    seen=set(); raw_batch=[]; line_batch=[]; counts=Counter()
    with input_path.open(encoding='latin1',newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != FIELDS:
            raise ValueError(f'Expected columns in order: {FIELDS}; got {reader.fieldnames}')
        for row_id, raw in enumerate(reader, start=2):
            if None in raw or any(v is None for v in raw.values()):
                raise ValueError(f'Malformed CSV record at source row {row_id}')
            payload=json.dumps(raw,ensure_ascii=False,separators=(',',':'))
            fingerprint=hashlib.sha256(payload.encode('utf-8')).hexdigest()
            repeat=int(fingerprint in seen); seen.add(fingerprint)
            line=normalize(raw,row_id)
            raw_batch.append((row_id,payload,fingerprint,repeat))
            line_batch.append(tuple(line[k] for k in ['row_id','invoice','sku','description','country','customer','invoice_date','quantity','unit_price','amount_pence','kind','reason']))
            counts['input_rows']+=1; counts['exact_repeat_rows']+=repeat
            counts['missing_customer_rows']+=int(not line['customer'])
            counts['missing_description_rows']+=int(not line['description'])
            if len(raw_batch)>=3000:
                db.executemany('INSERT INTO raw_rows VALUES (?,?,?,?)',raw_batch)
                db.executemany('INSERT INTO lines VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',line_batch)
                raw_batch.clear(); line_batch.clear()
        db.executemany('INSERT INTO raw_rows VALUES (?,?,?,?)',raw_batch)
        db.executemany('INSERT INTO lines VALUES (?,?,?,?,?,?,?,?,?,?,?,?)',line_batch)
    db.executescript('''CREATE INDEX IF NOT EXISTS lines_date ON lines(invoice_date);
        CREATE INDEX IF NOT EXISTS lines_customer ON lines(customer);
        DROP VIEW IF EXISTS valued_lines;
        CREATE VIEW valued_lines AS SELECT l.*,r.is_repeat FROM lines l JOIN raw_rows r USING(row_id)
          WHERE l.kind <> 'excluded';''')
    db.commit()
    reports={}
    for sql in sorted((ROOT/'sql').glob('*.sql')):
        reports[sql.stem]=export_query(db,sql.read_text(encoding='utf-8'),output/(sql.stem+'.csv'))
    counts.update(dict(db.execute('SELECT kind,COUNT(*) FROM lines GROUP BY kind').fetchall()))
    counts['raw_signed_pence']=db.execute('SELECT COALESCE(SUM(amount_pence),0) FROM lines').fetchone()[0]
    counts['excluded_signed_pence']=db.execute("SELECT COALESCE(SUM(amount_pence),0) FROM lines WHERE kind='excluded'").fetchone()[0]
    counts['net_pence']=db.execute('SELECT COALESCE(SUM(amount_pence),0) FROM valued_lines').fetchone()[0]
    counts['duplicate_net_pence']=db.execute('SELECT COALESCE(SUM(amount_pence),0) FROM valued_lines WHERE is_repeat=1').fetchone()[0]
    counts['deduplicated_net_pence']=counts['net_pence']-counts['duplicate_net_pence']
    counts['gross_sales_pence']=db.execute("SELECT COALESCE(SUM(amount_pence),0) FROM valued_lines WHERE kind='sale'").fetchone()[0]
    counts['cancellation_pence']=-db.execute("SELECT COALESCE(SUM(amount_pence),0) FROM valued_lines WHERE kind='cancellation'").fetchone()[0]
    counts['sale_invoices']=db.execute("SELECT COUNT(DISTINCT invoice) FROM valued_lines WHERE kind='sale'").fetchone()[0]
    counts['identified_sale_customers']=db.execute("SELECT COUNT(DISTINCT customer) FROM valued_lines WHERE kind='sale'").fetchone()[0]
    counts['unidentified_gross_pence']=db.execute("SELECT COALESCE(SUM(amount_pence),0) FROM valued_lines WHERE kind='sale' AND customer IS NULL").fetchone()[0]
    counts['start_date'],counts['end_date']=db.execute('SELECT MIN(invoice_date),MAX(invoice_date) FROM lines').fetchone()
    assertions={
      'row_partition': counts['input_rows']==sum(counts[x] for x in ['sale','cancellation','excluded']),
      'signed_value_reconciliation': counts['raw_signed_pence']==counts['net_pence']+counts['excluded_signed_pence'],
      'monthly_matches_net': sum(x['net_pence'] for x in reports['monthly'])==counts['net_pence'],
      'country_matches_net': sum(x['net_pence'] for x in reports['countries'])==counts['net_pence'],
      'product_matches_net': sum(x['net_pence'] for x in reports['products'])==counts['net_pence'],
      'gross_less_cancellations': counts['gross_sales_pence']-counts['cancellation_pence']==counts['net_pence'],
      'duplicate_sensitivity': counts['net_pence']-counts['duplicate_net_pence']==counts['deduplicated_net_pence'],
    }
    summary={'metrics':dict(counts),'checks':assertions,'reports':reports,
             'input_sha256':hashlib.sha256(input_path.read_bytes()).hexdigest(),
             'source':'https://www.kaggle.com/datasets/carrie1/ecommerce-data',
             'retrieved':'2026-10-15','currency':'GBP','rounding':'per line, half up to pence'}
    (output/'analysis.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
    export_query(db,'SELECT * FROM valued_lines ORDER BY row_id',output/'cleaned_lines.csv')
    export_query(db,"SELECT row_id,invoice,sku,invoice_date,quantity,unit_price,amount_pence,reason FROM lines WHERE kind='excluded' ORDER BY row_id",output/'exceptions.csv')
    db.close()
    if not all(assertions.values()):
        raise AssertionError(assertions)
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,default=ROOT/'data/raw/data.csv')
    p.add_argument('--output',type=Path,default=ROOT/'results')
    a=p.parse_args(); s=run(a.input,a.output)
    print(json.dumps({'metrics':s['metrics'],'checks':s['checks']},indent=2))
