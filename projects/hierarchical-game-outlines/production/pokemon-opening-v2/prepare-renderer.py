from pathlib import Path
import json,sys
sys.stdout.reconfigure(encoding='utf-8')
P=Path(__file__).resolve().parent;PREV=P.parent/'reference-preserving-v1';ROOT=P.parents[3]
s=(PREV/'render-reference.cjs').read_text(encoding='utf-8')
s=s.replace("production/reference-preserving-v1'","production/pokemon-opening-v2'")
s=s.replace('reference-reel-plan-v1.json','pokemon-opening-plan-v2.json').replace('reference-explanations-v1.tsx','pokemon-opening-v2.tsx')
s=s.replace("const revision=process.argv[3]", "const control=JSON.parse(fs.readFileSync(path.join(ROOT,'shared/publishing/video-production-control.json'),'utf8'));if(control.selectedVideo!==slug||!control.newProductionAuthorization.fullProductionAuthorized)throw Error('Current selected-video authorization required');\nconst revision=process.argv[3]")
(P/'render-pokemon.cjs').write_text(s,encoding='utf-8')
for n in ['captions.py']:(P/n).write_bytes((PREV/n).read_bytes())
print('Prepared selected-opening renderer; existing eight scene renders preserved.')
