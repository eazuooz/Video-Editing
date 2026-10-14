from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
src=B/'observe-motion-four-voice-resource-v6.py';dst=B/'observe-motion-four-voice-resource-v7.py'
assert not dst.exists()
code=src.read_text('utf-8-sig').replace("out=R/'voice-retry-resource-verification-v6.json'","out=R/'voice-retry-resource-verification-v7.json'").replace("previousObservation='voice-retry-resource-verification-v5.json'","previousObservation='voice-retry-resource-verification-v6.json'")
compile(code,str(dst),'exec');dst.write_text(code,'utf-8')
print('New read-only observation prepared; previousfalse preserved; no voice request.')
