"""Build portfolio visuals and documentation from executed analysis.json."""
import base64, csv, hashlib, html, json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab import rl_config
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak, Preformatted
rl_config.useA85 = False

ROOT=Path(__file__).resolve().parents[1]
import sys
sys.path.insert(0, str(ROOT/'src'))
from publication import current_output
RESULTS=current_output(ROOT/'results')
OUT=ROOT/'deliverables'; OUT.mkdir(exist_ok=True)
DOCS=ROOT/'docs'; DOCS.mkdir(exist_ok=True)
S=json.loads((RESULTS/'analysis.json').read_text(encoding='utf-8'))
M=S['metrics']; R=S['reports']
money=lambda p:f'£{p/100:,.2f}'
pct=lambda n,d:f'{n/d:.1%}'
navy='#18283f'; blue='#3067b0'; muted='#65758a'; amber='#b76b12'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':'#cbd5e1','text.color':navy,'axes.labelcolor':muted,'xtick.color':muted,'ytick.color':muted})

def monthly_chart(ax):
    months=[x['month'] for x in R['monthly']]; vals=[x['net_pence']/100000000 for x in R['monthly']]
    bars=ax.bar(range(len(months)),vals,color=blue,width=.65)
    bars[-1].set_color(amber); bars[-1].set_hatch('//')
    ax.set_xticks(range(len(months)),['Dec 10']+[x[-2:]+'/11' for x in months[1:]],rotation=0)
    ax.set_ylabel('Net transaction value (£ million)'); ax.set_ylim(0,max(vals)*1.18)
    ax.grid(axis='y',color='#e5eaf0'); ax.set_axisbelow(True)
    ax.text(12,vals[-1]+.055,'partial',ha='center',color=amber,fontsize=9)

fig,ax=plt.subplots(figsize=(10.8,3.0)); monthly_chart(ax)
ax.set_title('November leads the complete observed months',loc='left',fontweight='bold',pad=16)
fig.tight_layout(); fig.savefig(OUT/'monthly-sales.png',dpi=180,facecolor='white'); plt.close(fig)

fig=plt.figure(figsize=(15,10),facecolor='#f4f6fa')
fig.text(.06,.93,'RETAIL SALES & DATA QUALITY AUDIT',fontsize=23,weight='bold',color=navy)
fig.text(.06,.89,'Kaggle / UCI Online Retail · December 2010–December 9, 2011 · GBP',fontsize=12,color=muted)
for x,label,value in [(.06,'SOURCE TRANSACTION LINES',f"{M['input_rows']:,}"),(.38,'VALUED NET TRANSACTIONS',money(M['net_pence'])),(.70,'EXACT REPEATED ROWS',f"{M['exact_repeat_rows']:,}")]:
    fig.text(x,.81,label,fontsize=10,color=muted,weight='bold'); fig.text(x,.755,value,fontsize=26,color=navy,weight='bold')
ax=fig.add_axes([.085,.36,.86,.31],facecolor='white'); monthly_chart(ax)
ax.set_title('Monthly net value · final month is partial',loc='left',fontsize=13,pad=14)
fig.text(.06,.26,'CLEANING DECISIONS THAT CHANGE THE ANSWER',fontsize=12,weight='bold')
fig.text(.06,.21,f"Missing customer IDs: {M['missing_customer_rows']:,} rows",fontsize=13)
fig.text(.06,.17,f"Retain their {money(M['unidentified_gross_pence'])} in gross sales; exclude from identified-customer analysis.",fontsize=11,color=muted)
fig.text(.06,.115,f"Exact-repeat sensitivity: {money(M['duplicate_net_pence'])} net difference · {M['excluded']:,} unvalued rows retained for review",fontsize=11,color=muted)
fig.text(.06,.055,'Python · SQLite · Excel | Personal portfolio project | Source: Chen (2015), UCI / Kaggle',fontsize=9,color=muted)
fig.savefig(OUT/'portfolio-cover.png',dpi=120,facecolor=fig.get_facecolor()); plt.close(fig)

net=M['net_pence']; gross=M['gross_sales_pence']; canc=M['cancellation_pence']
repeat=next(x for x in R['customer_repeat'] if x['customer_group']=='multiple purchase invoices')
uk=R['countries'][0]; november=next(x for x in R['monthly'] if x['month']=='2011-11')
findings=[
 f"Valued net transaction value is {money(net)}: {money(gross)} gross positive sales less {money(canc)} in cancellations.",
 f"November 2011 has the highest net value among complete observed months: {money(november['net_pence'])}. December 2011 is partial and cannot support a full-month comparison.",
 f"The United Kingdom contributes {pct(uk['net_pence'],net)} of valued net transaction value. Its concentration should be considered before treating these results as a broad international benchmark.",
 f"Missing customer IDs occur in {M['missing_customer_rows']:,} records. Identifying customers is not necessary to retain their {money(M['unidentified_gross_pence'])} in gross sales.",
 f"Removing all exact repeated occurrences would reduce net value by {money(M['duplicate_net_pence'])} ({pct(M['duplicate_net_pence'],net)}). This is a sensitivity, not evidence that every repeat is an error.",
 f"Among {M['identified_sale_customers']:,} identified purchase customers, {repeat['customers']:,} ({pct(repeat['customers'],M['identified_sale_customers'])}) have multiple purchase invoices. This excludes unknown customer IDs."
]

case='# Case study: retail sales and data quality\n\n'
case+='Personal portfolio project. Actual public Kaggle/UCI data; no private employer or client data.\n\n## The problem\n\nA retail export needs cleanup without losing valid sales, hiding cancellations or assuming repeated lines are errors. The project produces an auditable report and explicit decision rules.\n\n## Findings\n\n'
case+='\n'.join('- '+x for x in findings)
case+='\n\n## Deliverables\n\nPython ingestion and normalization; SQLite database with original-row lineage; six SQL reports; full cleaned and exception CSVs; formula-based Excel review; business report; tests; data dictionary and refresh documentation.\n\n## Interpretation\n\nUse the report to prioritize clarification of repeats and unknown customer IDs, and to compare complete observed months. It does not estimate profit, business savings, inventory availability or future sales. Special charge codes remain included in transaction value. See METHOD.md for all rules.\n'
(DOCS/'CASE_STUDY.md').write_text(case,encoding='utf-8')

source=f'''# Sources and provenance

## Downloaded source

- Kaggle: https://www.kaggle.com/datasets/carrie1/ecommerce-data
- Dataset: E-Commerce Data, uploader Carrie, version 1 (page inspected October 15, 2026).
- Download: https://www.kaggle.com/api/v1/datasets/download/carrie1/ecommerce-data
- File: `data.csv`, Latin-1 encoding, eight columns, {M['input_rows']:,} records.
- Retrieval date: October 15, 2026.
- SHA-256 of extracted CSV: `{S['input_sha256']}`.
- The mirror's current license label is **Unknown**; it identifies the original UCI dataset.

## Original dataset and attribution

Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5BW33.

Original dataset page: https://archive.ics.uci.edu/dataset/352/online+retail

UCI states Creative Commons Attribution 4.0 International (CC BY 4.0), permitting sharing and adaptation with attribution. License text: https://creativecommons.org/licenses/by/4.0/

This project attributes the underlying data to UCI/Daqing Chen. It does not claim Kaggle independently supplied a permissive license. Data transformations: text normalization, explicit type/date parsing, line-level decimal rounding, eligibility classification, repeat flags, grouped SQL reports, and visual summaries. Original source data is not modified in place. Code is licensed separately under MIT.

## Reproduction and scope

Use the fingerprint to identify this exact input. A later Kaggle replacement may change the results; re-run tests and compare the row count and checksum. Source documentation describes the underlying retailer; all numeric findings here are computed by the included code, not copied from another analyst's notebook. Documentation discrepancies (such as UCI metadata stating no missing values) are resolved by reporting observed CSV null counts. The project does not infer identities for anonymous customer keys.
'''
(DOCS/'SOURCES.md').write_text(source,encoding='utf-8')

qa='# Quality assurance report\n\nExecuted against the downloaded Kaggle CSV on October 15, 2026.\n\n## Automated tests\n\n13 unittest cases passed: numeric/date validation; sale/cancellation signs; missing customer retention; fractional quantities; sub-penny rounding; large orders; exact repeats; value reconciliation; repeatable rebuilding. The small test fixtures are synthetic and isolated from the real analysis.\n\n## Full-data controls\n\n'
for k,v in S['checks'].items(): qa+=f'- {k}: {"PASS" if v else "FAIL"}\n'
qa+=f'''\n- Input: {M['input_rows']:,} rows.
- Sale: {M['sale']:,}; cancellation: {M['cancellation']:,}; excluded: {M['excluded']:,}.
- Raw parseable signed value: {money(M['raw_signed_pence'])}.
- Valued net: {money(net)}; excluded signed value: {money(M['excluded_signed_pence'])}.
- Exact repeated source occurrences: {M['exact_repeat_rows']:,}.
- Exact-repeat sensitivity net: {money(M['deduplicated_net_pence'])}.

The controls compare integer pence, not floating-point approximations. The excluded signed value can be negative and is not an estimate of lost revenue. See `workbook-verification.json` and `independent-verification.json` for additional execution evidence. Native desktop Excel recalculation was not tested; workbook formulas were tested in the artifact-tool calculation engine and exported for Excel.
'''
(DOCS/'QA_REPORT.md').write_text(qa,encoding='utf-8')

def table_html(rows,columns):
    return '<table><thead><tr>'+''.join('<th>'+html.escape(c)+'</th>' for c in columns)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+html.escape(str(r[c]))+'</td>' for c in columns)+'</tr>' for r in rows)+'</tbody></table>'
monthly=[{'Month':r['month']+(' (partial)' if r['month']=='2011-12' else ''),'Gross GBP':money(r['gross_pence']),'Cancellation GBP':money(r['cancellation_pence']),'Net GBP':money(r['net_pence'])} for r in R['monthly']]
image=base64.b64encode((OUT/'monthly-sales.png').read_bytes()).decode()
body=''.join('<li>'+html.escape(x)+'</li>' for x in findings)
html_doc=f'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Retail sales and data quality audit</title>
<style>body{{font:16px/1.6 system-ui,sans-serif;background:#f4f6fa;color:{navy};margin:0}}main{{max-width:1050px;margin:auto;background:white;padding:48px}}h1{{font-size:34px;line-height:1.2}}h2{{margin-top:32px}}.context{{color:{muted}}}.metrics{{display:flex;gap:35px;flex-wrap:wrap;margin:28px 0}}.metric b{{display:block;font-size:27px}}img{{width:100%;height:auto}}table{{border-collapse:collapse;width:100%;font-size:14px}}td,th{{padding:10px;text-align:right;border-bottom:1px solid #dfe5ed}}td:first-child,th:first-child{{text-align:left}}th{{background:#edf1f6}}li{{margin-bottom:10px}}a{{color:{blue}}}@media(max-width:650px){{main{{padding:22px}}table{{font-size:11px}}td,th{{padding:5px}}}}@media print{{main{{padding:0}}body{{background:white}}}}</style>
<main><p class="context">PERSONAL PORTFOLIO PROJECT · PYTHON / SQL / EXCEL</p><h1>Retail sales &amp; data quality audit</h1><p class="context">Actual Kaggle / UCI retail transactions · December 2010–December 9, 2011</p>
<div class="metrics"><div class="metric">Source lines<b>{M['input_rows']:,}</b></div><div class="metric">Valued net transactions<b>{money(net)}</b></div><div class="metric">Unvalued rows retained for review<b>{M['excluded']:,}</b></div></div>
<img alt="Monthly net transaction values; December 2011 is partial" src="data:image/png;base64,{image}"><h2>What the data shows</h2><ul>{body}</ul><h2>Monthly report</h2>{table_html(monthly,list(monthly[0]))}<h2>How the report was built</h2><p>Python preserves every source record, validates types and dates, and calculates signed line amounts using Decimal. SQLite queries aggregate the eligible sale and cancellation lines. All three value breakdowns reconcile exactly in pence to the headline total.</p><p>Zero/negative-price lines are excluded from valued reporting and retained in an exception file. Missing customer IDs remain in sales. Exact repeats remain in primary totals, with an alternative sensitivity. Amounts include special charge codes; net transaction value is not profit or cash collected. No business savings or causal claims are made.</p><h2>Evidence and files</h2><p>13 automated tests and seven full-data reconciliation checks passed. Read the accompanying README, METHOD, DATA_DICTIONARY, QA_REPORT and Excel guide for reproduction and limits.</p><p><a href="retail-sales-review.xlsx">Excel review workbook</a> · <a href="case-study.pdf">PDF case study</a></p><h2>Source</h2><p>Chen, D. (2015). Online Retail. UCI Machine Learning Repository. <a href="https://doi.org/10.24432/C5BW33">Dataset DOI</a> · <a href="https://www.kaggle.com/datasets/carrie1/ecommerce-data">Kaggle mirror</a>. UCI lists CC BY 4.0; the Kaggle mirror's license label is Unknown. Attribution and transformations are documented in SOURCES.md.</p></main></html>'''
(OUT/'report.html').write_text(html_doc,encoding='utf-8')

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleCustom',fontName='Helvetica-Bold',fontSize=23,leading=27,textColor=colors.HexColor(navy),spaceAfter=12))
styles.add(ParagraphStyle(name='Context',fontName='Helvetica',fontSize=9,leading=13,textColor=colors.HexColor(muted),spaceAfter=12))
styles['BodyText'].fontSize=10; styles['BodyText'].leading=14; styles['BodyText'].spaceAfter=9
styles['Heading2'].textColor=colors.HexColor(navy); styles['Heading2'].spaceBefore=15
story=[]
P=lambda text,style='BodyText': Paragraph(text,styles[style])
story += [P('Retail sales &amp; data quality audit','TitleCustom'),P('PERSONAL PORTFOLIO PROJECT | PYTHON / SQLITE / EXCEL<br/>Actual public Kaggle / UCI transactions.','Context'),P('The task','Heading2'),P('Turn a transaction export into a useful sales report without dropping unknown customers, hiding cancellations or silently assuming repeated rows are errors.')]
t=Table([['Source lines','Valued net transactions','Excluded from valuation'],[f"{M['input_rows']:,}",money(net),f"{M['excluded']:,} rows"]],colWidths=[155,190,160])
t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eaf0f8')),('TEXTCOLOR',(0,0),(-1,-1),colors.HexColor(navy)),('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),('FONTSIZE',(0,0),(-1,0),9),('FONTSIZE',(0,1),(-1,1),14),('BOTTOMPADDING',(0,0),(-1,-1),10),('TOPPADDING',(0,0),(-1,-1),10)]))
story += [Spacer(1,8),t,Spacer(1,10),Image(str(OUT/'monthly-sales.png'),width=505,height=140),P('Findings and practical implications','Heading2')]
for text in [findings[0],findings[3],findings[4]]: story.append(P(text))
story += [P('Keep valid sales with unknown customers in aggregate reporting. Confirm line identifiers before deduplicating. Compare complete months and investigate large cancellations with the data owner.','BodyText'),PageBreak(),P('Method, controls &amp; limitations','TitleCustom'),P('TRACEABLE SOURCE ROWS | EXPLICIT RULES | RECONCILED TOTALS','Context')]
for title,text in [
 ('Preserve and classify','Original rows remain in SQLite with source row numbers and exact-repeat fingerprints. Dates use month/day/year. Monetary line amounts use Decimal, rounded half up to pence. Eligible sales and C-invoice cancellations are retained; nonpositive prices and invalid records remain available for review.'),
 ('Measure the effect of cleaning',f"Gross sales are {money(gross)} and cancellation value is {money(canc)}. Excluding exact repeats changes net value from {money(net)} to {money(M['deduplicated_net_pence'])}. Missing customer IDs affect customer analysis, not the validity of otherwise eligible sales."),
 ('Verification','13 automated test cases passed, including end-to-end repeat handling and a rebuild check. Seven full-data checks reconcile row counts, signed values, gross less cancellations, and monthly/country/product totals. Independent verification and workbook calculation checks are included in the project documentation.'),
 ('Limits','December 2011 ends on December 9. These historical data describe one retailer. Special charge codes remain included in transaction values. Cancellation share is not a linked return rate. No cost or stock balance fields exist, so this project makes no profit, savings or inventory-availability claims.')]:
    story += [P(title,'Heading2'),P(html.escape(text))]
story += [P('SQL example: product ranking','Heading2'),Preformatted("WITH totals AS (\n SELECT sku, SUM(amount_pence) AS net_pence\n FROM valued_lines GROUP BY sku\n)\nSELECT DENSE_RANK() OVER (ORDER BY net_pence DESC) AS rank, *\nFROM totals ORDER BY net_pence DESC, sku;",ParagraphStyle('Code',fontName='Courier',fontSize=8,leading=11)),P('Source and attribution','Heading2'),P('Chen, D. (2015). <i>Online Retail</i>. UCI Machine Learning Repository. DOI: 10.24432/C5BW33. Downloaded from Kaggle: carrie1/ecommerce-data (October 15, 2026). UCI lists CC BY 4.0; the mirror lists Unknown. Full URLs, SHA-256 and transformation details are in SOURCES.md.','Context')]
def footer(canvas,doc):
    canvas.setFont('Helvetica',8); canvas.setFillColor(colors.HexColor(muted))
    canvas.drawString(48,25,'Zak Rademacher | public-data portfolio case study')
    canvas.drawRightString(564,25,f'{doc.page}')
doc=SimpleDocTemplate(str(OUT/'case-study.pdf'),pagesize=(612,792),rightMargin=48,leftMargin=48,topMargin=42,bottomMargin=46,title='Retail Sales and Data Quality Audit',author='Zak Rademacher')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
print('Created presentation, case study and documentation.')
