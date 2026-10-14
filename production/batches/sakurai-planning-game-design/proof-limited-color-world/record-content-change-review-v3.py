"""Record directly read new quaternion preparation without editing foreign work."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4];P=Path(__file__).resolve().parent
NODE='C:/Users/eazuo/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
rp=ROOT/'production/batches/sakurai-planning-game-design/preflight/limited-color-world.json'
r=json.loads(rp.read_text(encoding='utf-8'));old=json.loads((P/'duplicate-history-approved54-v2.json').read_text(encoding='utf-8'))
oldhash={i['path']:i['sha256'] for i in old['inputFiles']};changed=[i for i in r['inputFiles'] if i['sha256']!=oldhash.get(i['path'])]
assert len(changed)==3 and all(i['path'].startswith('projects/game-math-quaternion-teaching-additions-v2/') for i in changed)
for i in r['inputFiles']:assert sha(ROOT/i['path'])==i['sha256']
ax=P/'studio-quaternion-current-v3.ax.txt';text=ax.read_text(encoding='utf-8');assert '03OXtik2nes' in text and '예약됨' in text and '고화질 완료' in text and '최소 회전 각도' in text
out=P/'content-studio-change-review-v3.json';assert not out.exists()
d={'schemaVersion':3,'slug':'limited-color-world','recordedAt':datetime.now(timezone.utc).isoformat(),'previousFullRelatedReview':'content-studio-direct-review-v2.json','preservedPreviousReport':'duplicate-history-approved54-v2.json','projects':55,'inputs':384,'inputsDigest':r['inputsDigest'],'changedFilesFullBodiesDirectlyRead':changed,'allChangedKoEn33ScenesAndManifestRead':True,'comparison':'New additive teaching narration explains imaginary unit, complex multiplication, quaternion components, half angle, normalization, dot/cross, logarithm/exponential and two-sided vector rotation; 25 bridging scenes connect the existing26 quaternion topics. Orientation algebra and body/world conventions differ from preserving essential gameplay information when hues are difficult to distinguish. Its axis colors are diagram notation, not a color-perception/accessibility lesson.','currentStudio':{'actualId':'03OXtik2nes','url':'https://studio.youtube.com/video/03OXtik2nes/edit','fullTitleDescriptionAnd19ChapterEntriesRead':True,'observedStatus':'예약됨','sdHdObserved':True,'ax':str(ax.relative_to(ROOT)).replace('\\','/'),'axSha256':sha(ax)},'newAdditiveProjectStandaloneUploadAllowed':False,'newAdditiveProjectActualId':None,'absenceFromChannelNotInferred':True,'decision':'distinct','foreignFilesOrSettingsModified':0,'newProjectScriptTtsMcOrFootageAdoption':False}
out.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
args=[NODE,'scripts/review-video-duplicates.cjs','limited-color-world','--decision','distinct','--reason','Full11 related KOEN/outline/manifest review plus all3 new quaternion teaching files33 scenes: orientation algebra is distinct from hue-independent essential gameplay cues, brightness/shape/pattern and perceptual inspection. See content-studio-direct-review-v2.json and content-studio-change-review-v3.json.','--studio-evidence',str(out.relative_to(ROOT)).replace('\\','/')]
a=subprocess.run(args,cwd=ROOT,capture_output=True,text=True,encoding='utf-8');assert a.returncode==0,a.stdout+a.stderr
b=subprocess.run([NODE,'scripts/review-video-duplicates.cjs','limited-color-world','--check'],cwd=ROOT,capture_output=True,text=True,encoding='utf-8');assert b.returncode==0,b.stdout+b.stderr
print(json.dumps({'projects':55,'inputs':384,'digest':r['inputsDigest'],'decisionExit':a.returncode,'checkExit':b.returncode}))
