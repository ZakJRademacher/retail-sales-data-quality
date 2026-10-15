"""Download the public Kaggle mirror; no API token is stored or required."""
import hashlib, io, json, urllib.request, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://www.kaggle.com/api/v1/datasets/download/carrie1/ecommerce-data'
if __name__=='__main__':
    raw=ROOT/'data/raw'; raw.mkdir(parents=True,exist_ok=True)
    with urllib.request.urlopen(URL,timeout=120) as response: payload=response.read()
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        # Extract only the expected member; never trust archive paths.
        content=archive.read('data.csv')
    (raw/'data.csv').write_bytes(content)
    manifest={'source':'https://www.kaggle.com/datasets/carrie1/ecommerce-data','download_url':URL,
              'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content)}
    (raw/'download_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps(manifest,indent=2))
