from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];D=ROOT/'shared/output/original-tech-twelve-20261115'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,s):assert not p.exists(),p;p.write_text(s,'utf8')
slugs=['shorts-spiderman-swing-anchor','shorts-control-destruction-pipeline','shorts-returnal-particle-tentacles','shorts-ratchet-dimension-streaming','shorts-doom-push-forward-healing','shorts-botw-chemistry-rules','shorts-mariokart8-spin-boost']
rows=[]
for slug in slugs:
 P=ROOT/'projects'/slug;prior=P/('production/film-inputs-v27.json'if(P/'production/film-inputs-v27.json').exists()else'production/film-inputs-v10.json');d=read(prior);base=D/'remaining-seven/native-pose-warmup-v30';d.update(nativeFullProofPath=str(base/'accepted-full.json'),nativeVisualReviewPath=str(base/'full-visual-review-v30.json'),actualNativeFullReady=False,priorBindings=pin(prior),nativePoseWarmupSource=pin(H/'native-pose-warmup-v30/source-review.json'));out=P/'production/film-inputs-v33.json';write(out,json.dumps(d,ensure_ascii=False,indent=2)+'\n');rows.append(pin(out))
s=(H/'run-lesson-film-v27-cooperative-v19.py').read_text(encoding='utf8');s=s.replace("P/('production/film-inputs-v27.json'if", "P/('production/film-inputs-v33.json'if(P/'production/film-inputs-v33.json').exists()else'production/film-inputs-v27.json'if");write(H/'run-lesson-film-v33-cooperative-v19.py',s)
s=(H/'finalize-local-bundle-v27.py').read_text(encoding='utf8');s=s.replace("P/('production/film-inputs-v27.json'if", "P/('production/film-inputs-v33.json'if(P/'production/film-inputs-v33.json').exists()else'production/film-inputs-v27.json'if");write(H/'finalize-local-bundle-v33.py',s)
write(H/'native-film-bindings-source-review-v33.json',json.dumps(dict(bindings=rows,existingSourceAndMediaPreserved=True,actualNativeFullComplete=False,finalFilmComplete=False,change='Explicit future native pose-corrected full identity; source order, voice and caption timings remain bound exactly.'),indent=2)+'\n');print('Prepared7 explicit future native bindings; no capture readiness claimed')
