"""Make a compact, shareable bundle; retain full generated data locally."""
import csv, hashlib, json, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sample=ROOT/'data/sample'; sample.mkdir(parents=True,exist_ok=True)
with (ROOT/'results/cleaned_lines.csv').open(encoding='utf-8-sig',newline='') as stream:
    reader=csv.reader(stream)
    with (sample/'cleaned_example_1000.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.writer(f); writer.writerow(next(reader))
        for i,row in enumerate(reader):
            if i==1000: break
            writer.writerow(row)
manifest=[]
for directory in ['src','sql','tests','tools','docs','deliverables','data/sample','.github']:
    for file in sorted((ROOT/directory).rglob('*')):
        if file.is_file() and '__pycache__' not in file.parts and not file.name.endswith('.inspect.ndjson') and file.name!='package-manifest.json':
            manifest.append(file)
for file in sorted(ROOT.glob('*')):
    if file.is_file(): manifest.append(file)
for file in sorted((ROOT/'results').glob('*')):
    if file.suffix=='.json' or (file.suffix=='.csv' and file.name!='cleaned_lines.csv'):
        manifest.append(file)
entries=[{'path':f.relative_to(ROOT).as_posix(),'bytes':f.stat().st_size,'sha256':hashlib.sha256(f.read_bytes()).hexdigest()} for f in manifest]
manifest_file=ROOT/'docs/package-manifest.json'
manifest_file.write_text(json.dumps({'files':entries,'large_files_omitted':['data/raw/*','results/retail.sqlite','results/cleaned_lines.csv'],'rebuild':'See README.md'},indent=2),encoding='utf-8')
if manifest_file not in manifest: manifest.append(manifest_file)
target=ROOT.parent/'retail-data-portfolio.zip'
with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
    for file in sorted(set(manifest)):
        archive.write(file,'retail-data-project/'+file.relative_to(ROOT).as_posix())
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
print(json.dumps({'zip':str(target),'files':len(set(manifest)),'bytes':target.stat().st_size},indent=2))
