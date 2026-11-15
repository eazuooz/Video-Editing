from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;ROOT=H.parents[2];D=ROOT/'shared/output/original-tech-twelve-20261115';rows=[]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def pin(p):return dict(path=str(p.resolve()),sha256=hashlib.sha256(p.read_bytes()).hexdigest())
def write(p,s):assert not p.exists(),p;p.write_text(s,'utf8')
for x in read(H/'native-film-bindings-source-review-v33.json')['bindings']:
 prior=Path(x['path']);d=read(prior);base=D/'remaining-seven/native-reviewed-pose-v35';d.update(nativeFullProofPath=str(base/'accepted-full.json'),nativeVisualReviewPath=str(base/'full-visual-review-v35.json'),priorBindings=pin(prior),startupPoseReview=pin(base/'smoke-visual-review-v35.json'));out=prior.parent/'film-inputs-v37.json';write(out,json.dumps(d,ensure_ascii=False,indent=2)+'\n');rows.append(pin(out))
for source,target in [('run-lesson-film-v33-cooperative-v19.py','run-lesson-film-v37-cooperative-v19.py'),('finalize-local-bundle-v33.py','finalize-local-bundle-v37.py')]:
 s=(H/source).read_text(encoding='utf8').replace("P/('production/film-inputs-v33.json'if","P/('production/film-inputs-v37.json'if(P/'production/film-inputs-v37.json').exists()else'production/film-inputs-v33.json'if");write(H/target,s)
write(H/'native-film-bindings-source-review-v37.json',json.dumps(dict(bindings=rows,actualNativeFullComplete=False,changedFirstPoseExplicitlyReviewed=True,voicePcmAndMeaningOrderPreserved=True,finalFilmComplete=False),indent=2)+'\n');print('Prepared7 reviewed-pose full-output bindings and matching renderer/finalizer')
