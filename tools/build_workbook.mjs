import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const require=createRequire(process.env.RETAIL_ARTIFACT_ROOT ? path.join(process.env.RETAIL_ARTIFACT_ROOT,'package.json') : import.meta.url);
const {Workbook,SpreadsheetFile}=await import(pathToFileURL(require.resolve('@oai/artifact-tool')));
const root=path.resolve(process.argv[2]);
const input=JSON.parse(await fs.readFile(path.join(root,'results/analysis.json'),'utf8'));
const wb=Workbook.create(); const review=wb.worksheets.add('Sales review'); const country=wb.worksheets.add('Country detail');
const blue='#3067B0',navy='#18283F',muted='#65758A',currency='"£"#,##0.00;[Red]("£"#,##0.00)';
for(const s of [review,country]){s.showGridLines=false; s.getRange('A1:L60').format.font={name:'Arial',size:10,color:navy};s.getRange('A1:L60').format.rowHeight=22;s.getRange('A1:H60').format.columnWidth=19;}
review.tabColor=navy;
review.getRange('A2').values=[['Retail sales & data quality audit']];review.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:navy};
review.getRange('A3').values=[['Dec 2010–Dec 9, 2011 | GBP | Personal portfolio project']];
review.getRange('A3').format.font={name:'Arial',size:10,color:muted};
review.getRange('A5:B10').values=[['Metric','Value'],['Gross positive sales',null],['Cancellation value',null],['Net transaction value',null],['Sale invoices',null],['Average sale invoice',null]];
review.getRange('A12').values=[['Reporting rules']];review.getRange('A12').format.font={bold:true};
review.getRange('A13').values=[['Exact repeated rows retained; sensitivity below.']];
review.getRange('A14').values=[['Missing customer IDs retained in sales totals.']];
review.getRange('A15').values=[['Special charge codes remain in transaction values.']];
review.getRange('A16').values=[['Net value is not profit or cash collected.']];
review.getRange('A18').values=[['Monthly inputs and calculations']];review.getRange('A18').format.font={bold:true,size:12};
review.getRange('A19').values=[['Blue values: SQL imports. Dark values: formulas. December 2011 is partial through Dec 9.']];
const headers=['Month','Gross GBP','Cancellation GBP','Net GBP','Sale invoices','Avg invoice GBP','Net no repeats GBP','Repeat impact GBP'];
review.getRange('A21:H21').values=[headers];
const start=22, end=start+input.reports.monthly.length-1;
review.getRange(`A${start}:H${end}`).values=input.reports.monthly.map(r=>[r.month+(r.month==='2011-12'?' partial':''),r.gross_pence/100,r.cancellation_pence/100,null,r.sale_invoices,null,r.deduplicated_net_pence/100,null]);
for(let row=start;row<=end;row++){
 review.getRange(`D${row}`).formulas=[[`=B${row}-C${row}`]];
 review.getRange(`F${row}`).formulas=[[`=IF(E${row}=0,"n.a.",B${row}/E${row})`]];
 review.getRange(`H${row}`).formulas=[[`=D${row}-G${row}`]];
}
review.getRange('B6:B10').formulas=[[`=SUM(B${start}:B${end})`],[`=SUM(C${start}:C${end})`],[`=SUM(D${start}:D${end})`],[`=SUM(E${start}:E${end})`],['=IF(B9=0,"n.a.",B6/B9)']];
review.getRange('A5:B5').format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'}};
review.getRange('A21:H21').format={fill:navy,font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,rowHeight:36,horizontalAlignment:'center'};
review.getRange('A6:A10').format.columnWidth=30;
review.getRange('B6:B8').setNumberFormat(currency);review.getRange('B10').setNumberFormat(currency);review.getRange('B9').setNumberFormat('#,##0');
for(const col of ['B','C','D','F','G','H'])review.getRange(`${col}${start}:${col}${end}`).setNumberFormat(currency);
review.getRange(`E${start}:E${end}`).setNumberFormat('#,##0');
for(const col of ['B','C','E','G'])review.getRange(`${col}${start}:${col}${end}`).format.font.color=blue;
review.getRange(`A${end}:H${end}`).format.fill='#FFF2DF';
review.getRange('A37').values=[['Partial month: December 2011 cannot be compared with full months.']];
review.getRange('A39').values=[['Source: Kaggle carrie1/ecommerce-data; Chen (2015), UCI Online Retail, DOI 10.24432/C5BW33.']];
review.getRange('A40').values=[['Underlying data: UCI CC BY 4.0. Mirror license label: Unknown. Method and provenance: accompanying documentation.']];
review.getRange('A39:A40').format.font={size:9,color:muted};
const chart=review.charts.add('line',[review.getRange(`A21:A${end}`),review.getRange(`D21:D${end}`)]);
chart.title='Monthly net value (GBP)';chart.titleTextStyle.typeface='Arial';chart.titleTextStyle.fontSize=12;chart.hasLegend=false;
chart.xAxis={axisType:'textAxis',textStyle:{typeface:'Arial',fontSize:9}};
chart.yAxis={numberFormatCode:'"£"0.0,,"M"',numberFormatSourceLinked:false,textStyle:{typeface:'Arial',fontSize:10}};
chart.series.items[0].line={fill:blue,style:'solid',width:2};chart.setPosition('D5','I17');
country.getRange('A2').values=[['Country detail']];country.getRange('A2').format.font={size:16,bold:true};
country.getRange('A3').values=[['Source labels retained. Import columns B, C and E in pounds, never pence. Net and share are formulas.']];
country.getRange('A5:F5').values=[['Country','Gross GBP','Cancellation GBP','Net GBP','Sale invoices','Net value share']];
const ce=5+input.reports.countries.length;
country.getRange(`A6:F${ce}`).values=input.reports.countries.map(r=>[r.country,r.gross_pence/100,r.cancellation_pence/100,null,r.sale_invoices,null]);
for(let row=6;row<=ce;row++){
 country.getRange(`D${row}`).formulas=[[`=B${row}-C${row}`]];
 country.getRange(`F${row}`).formulas=[[`=IF(SUM($D$6:$D$${ce})=0,"n.a.",D${row}/SUM($D$6:$D$${ce}))`]];
}
country.getRange('A5:F5').format={fill:navy,font:{color:'#FFFFFF',bold:true},horizontalAlignment:'center',rowHeight:32,wrapText:true};
country.getRange(`B6:D${ce}`).setNumberFormat(currency);country.getRange(`E6:E${ce}`).setNumberFormat('#,##0');country.getRange(`F6:F${ce}`).setNumberFormat('0.0%');
country.getRange('A5:A44').format.columnWidth=25;
for(const col of ['B','C','E'])country.getRange(`${col}6:${col}${ce}`).format.font.color=blue;
country.freezePanes.freezeRows(5);
review.tables.add(`A21:H${end}`,true,'MonthlyReview');country.tables.add(`A5:F${ce}`,true,'CountryReview');
// Reapply headers after table styling for predictable visual contrast.
for(const [s,range] of [[review,'A21:H21'],[country,'A5:F5']])s.getRange(range).format={fill:navy,font:{color:'#FFFFFF',bold:true},wrapText:true,horizontalAlignment:'center',rowHeight:36};
const original=review.getRange('B22').values[0][0], baseline=input.metrics.net_pence/100;
review.getRange('B22').values=[[original+100]];wb.recalculate();
const changed=review.getRange('B8').values[0][0];
if(Math.abs(changed-(baseline+100))>.005)throw Error('Input change did not propagate');
review.getRange('B22').values=[[original]];wb.recalculate();
const observed=review.getRange('B6:B10').values.flat();
if(Math.abs(observed[2]-baseline)>.005 || observed[3]!==input.metrics.sale_invoices)throw Error('Headline mismatch');
const errors=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'Final error scan'});
await fs.writeFile(path.join(root,'docs/workbook-verification.json'),JSON.stringify({engine:'Codex artifact-tool',netMatchesPython:true,invoiceCountMatchesPython:true,inputChangePropagates:true,restoredAfterTest:true,values:observed,errorScan:errors.ndjson,nativeExcelTested:false},null,2));
for(const [s,range,name] of [[review,'A1:I40','excel-sales-preview.png'],[country,'A1:F17','excel-country-preview.png']]){
 const blob=await wb.render({sheetName:s.name,range,scale:1.5,format:'png'});
 await fs.writeFile(path.join(root,'deliverables',name),new Uint8Array(await blob.arrayBuffer()));
}
const output=await SpreadsheetFile.exportXlsx(wb);await output.save(path.join(root,'deliverables/retail-sales-review.xlsx'));
console.log(JSON.stringify({net:observed[2],saleInvoices:observed[3],inputChangePropagates:true,errorScan:errors.ndjson}));
