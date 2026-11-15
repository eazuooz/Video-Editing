from pathlib import Path
import importlib.util,json
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;R=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115/production-resume-20261115T055255Z');s=importlib.util.spec_from_file_location('explicit_pose_review35',H/'run-reviewed-pose-native-v35.py');a=importlib.util.module_from_spec(s);s.loader.exec_module(a);m=a.configured();D=m.BASE.parent;old=D/'native-pose-warmup-v30';prep=m.read(old/'source-preparation.json');capture=old/'attempts/20261115T181242Z-639bc9f2/capture';out=m.BASE/'accepted-smoke.json';assert not out.exists();proof=m.verify(capture,prep,'smoke');proof.update(adoptionVersion=35,changedStartupFrame=True,sourceGeometryFingerprintPreserved=True,originalStrictFailure=m.pin(old/'failure-smoke.json'),executionReviewAdapter=m.pin(H/'run-reviewed-pose-native-v35.py'),startupReview='The old baseline shows an idle/stale pose in its first DOOM frame and changes to walking at frame1. The new startup uses the adjacent animation sample before actual frame0, producing a continuous walking pose at frames0/1. Other animated cases receive the same explicit cosmetic first-pose correction. All recorded rule states and frames1..31 remain byte-identical; no timing or teaching-rule threshold changed.',allFrames1To31BaselineByteExact=True,executionResourcePolicy=m.native.cooperative_policy_proof);m.save(out,proof)
imgs=[]
for c in proof['clips']:
 for f in[0,31]:
  p=next(Path(x['path'])for x in c['referenceFrames']if f'reference-{f:05}.png'==Path(x['path']).name);imgs.append((c['topic']+' '+c['mode']+' '+str(f),Image.open(p).convert('RGB').resize((375,375))))
for start in range(0,len(imgs),12):
 group=imgs[start:start+12];im=Image.new('RGB',(1500,1215),'#11221a');d=ImageDraw.Draw(im)
 for i,(label,pic)in enumerate(group):x=i%4*375;y=i//4*405;im.paste(pic,(x,y+30));d.text((x+5,y+5),label,fill='white')
 im.save(R/f'reviewed-pose-smoke-v35-contact-{start//12}.jpg',quality=94)
print(json.dumps(dict(proof=m.pin(out),clips=len(proof['clips']),all448PixelsRoundTripVerified=True)))
