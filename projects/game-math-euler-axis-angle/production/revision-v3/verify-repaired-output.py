"""Verify new masters and reuse only proven identical audio/decoded video ranges."""
from pathlib import Path
import json,hashlib,subprocess,sys,time,concurrent.futures,shutil,math
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[4];H=Path(__file__).parent;P=H.parent.parent;O=P/'production/local/revision-v3';Q=O/'qa';A=O/'before-turn-repair'
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def selected():assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
deadline=time.time()+3600
while True:
 selected();assert time.time()<deadline
 if (O/'pair-source.json').exists() and read(O/'pair-source.json')['inputs']['timelineSha256']==sha(H/'timeline.json'):break
 time.sleep(3)
print('Repaired pair ready; checking full integrity.',flush=True)
subprocess.run([sys.executable,str(H/'verify-output.py'),'integrity'],cwd=R,check=True)
integrity=read(Q/'integrity.json');old=read(A/'integrity.json');assert integrity['outputs'][1]['aacSha256']==old['outputs'][1]['aacSha256'],'Audio changed'
pair=read(O/'pair-source.json');video=pair['outputs']['captioned']['sha256'];timeline=sha(H/'timeline.json')
source=read(O/'encoded-audio-source.json');assert source['audioSha256']==sha(O/'encoded-audio.wav')
source['priorInputs']=source['inputs'];source['inputs']={'videoSha256':video,'rate':16000,'channels':1,'format':'pcm_s16le'}
source['reuseEvidence']='Exact ADTS AAC SHA256 equal in old/new clean and captioned masters; old/new integrity receipts.';save(O/'encoded-audio-source.json',source)
audio=read(Q/'audio-continuity.json');shutil.copy2(Q/'audio-continuity.json',A/'audio-continuity.json')
audio['inputs'].update(timelineSha256=timeline,encodedSha256=video,audioBuildSha256=sha(O/'audio-build.json'))
audio['reuseEvidence']={'unchangedAacSha256':integrity['outputs'][1]['aacSha256'],'timingProof':'production/revision-v3/annotation-repair.json','previousReport':'production/local/revision-v3/before-turn-repair/audio-continuity.json','noNewMeasurementsClaimed':True};save(Q/'audio-continuity.json',audio)
def decoded(label,path):
 dest=Q/(label+'-framehash.txt');sig=dest.with_suffix('.json');digest=sha(path)
 if not(sig.exists() and read(sig).get('videoSha256')==digest and dest.exists()):
  subprocess.run(['ffmpeg','-v','error','-threads','3','-i',str(path),'-an','-c:v','rawvideo','-threads','1','-f','framemd5','-y',str(dest)],check=True)
  save(sig,{'videoSha256':digest,'frameHashSha256':sha(dest)})
 return [line.split(',')[-1].strip() for line in dest.read_text().splitlines() if not line.startswith('#') and line.strip()]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
 fa=pool.submit(decoded,'before-turn',A/'euler-captioned.mp4');fb=pool.submit(decoded,'repaired',O/'euler-captioned.mp4');a,b=fa.result(),fb.result()
assert len(a)==len(b)==93100
changed=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y];assert changed
assert min(changed)>=round(770*60) and max(changed)<=round(842*60),(min(changed)/60,max(changed)/60)
report={'captionedVideoSha256':video,'oldCaptionedVideoSha256':sha(A/'euler-captioned.mp4'),'fullDecodedFramesCompared':len(a),'identicalDecodedFrames':len(a)-len(changed),'changedFrames':len(changed),'changedStart':min(changed)/60,'changedEnd':max(changed)/60,'allOtherFramesExactlyEqual':True,'audioExactlyEqual':True,'aacSha256':integrity['outputs'][1]['aacSha256'],'humanListening':'pending'}
save(Q/'repair-equivalence.json',report);print(report,flush=True)
rows=read(Q/'pixel-sample-index.json');changed_set=set(changed);selected_rows=[(i,r) for i,r in enumerate(rows) if r['frame'] in changed_set]
for i,r in selected_rows:
 subprocess.run(['ffmpeg','-v','error','-ss',str(r['time']),'-i',str(O/'euler-captioned.mp4'),'-frames:v','1','-q:v','3','-y',str(Q/f'frame-{i+1:04}.jpg')],check=True)
for page in sorted({i//8 for i,r in selected_rows}):
 chunk=rows[page*8:(page+1)*8];im=Image.new('RGB',(1920,580*math.ceil(len(chunk)/2)),(22,22,22));d=ImageDraw.Draw(im)
 for k,row in enumerate(chunk):
  x=k%2*960;y=k//2*580;im.paste(Image.open(Q/f'frame-{page*8+k+1:04}.jpg').resize((960,540)),(x,y));d.text((x+5,y+544),f"{row['time']:.2f}s | "+' / '.join(row['labels'])[:100],fill='white')
 im.save(Q/f'contact-{page:02}.jpg')
report['recheckedContactPages']=sorted({i//8 for i,r in selected_rows});report['replacedCurrentSampleCount']=len(selected_rows);save(Q/'repair-equivalence.json',report)
pixel=read(Q/'pixel-extraction.json');pixel['reusedPreviousInputs']=pixel['inputs'];pixel['inputs'].update(videoSha256=video,layoutSha256=sha(O/'caption-layout.json'),timelineSha256=timeline);pixel['reuseEvidence']='qa/repair-equivalence.json: every decoded frame compared; changed existing samples re-extracted; listed contact pages rebuilt';save(Q/'pixel-extraction.json',pixel)
print('Exact audio and unchanged decoded-frame evidence retained; inspect changed contacts:',report['recheckedContactPages'],flush=True)
