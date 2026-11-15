"""Bounded validation of simultaneous clean/captioned output from one composite."""
from subject_revision import *

def main():
 e=EPISODES['M26'];authorized(e);p=work(e);guard=prior.guard();reason=guard.idle_reason()
 if reason:raise RuntimeError(reason)
 ownership=str(uuid.uuid4())
 with guard.LEASE.open('x',encoding='utf8') as f:json.dump(dict(id=ownership,owner=e['slug']+'-v4-dual-preview',pid=os.getpid(),createdAt=guard.now()),f)
 try:
  # Integer-prefix seek matches production's zero-origin frame clock. A decimal
  # input seek can discard the boundary frame after microsecond rounding.
  start=150;seconds=4;frames=240;inputs,g=graph(e,start,start+seconds);prior.prepare_captions(e,p)
  shutil.copy2(ROOT/'projects'/e['slug']/'production/local/teaching-sync-v2/workings.ass',p/'workings.ass')
  ni=1+sum(x=='-i' for x in inputs);inputs+=['-ss',str(start),'-i',str(latest(e))]
  g=dual_graph(g,start);(p/'dual-preview.ffgraph').write_text(g,encoding='utf8');out=p/'dual-preview';out.mkdir(exist_ok=True)
  files=[out/'clean.mp4',out/'captioned.mp4'];args=[]
  for label,target in zip(('[vout]','[captionout]'),files):
   part=video_output(label,ni,frames,prior.encoder(),target);args+=part[:-1]+['-t',seconds,part[-1]]
  prior.command(['-ss',start,'-reinit_filter','0','-i',e['baselineOutputs']['clean'],*inputs,'-filter_complex_threads','2','-/filter_complex','dual-preview.ffgraph',*args],p,'dual-preview')
  for target in files:prior.check_stream(target,frames)
  assert prior.packet_hash(files[0],'a')==prior.packet_hash(files[1],'a')
  for target in files:
   subprocess.run([str(FF),'-v','error','-nostdin','-n','-i',str(target),'-vf','select=eq(n\\,24)','-frames:v','1',str(out/(target.stem+'-first.png'))],check=True,creationflags=prior.CREATE)
  save(HERE/'dual-output-validation.json',dict(status='technical-pass-picture-review-pending',frames=frames,resolution=[1920,1080],fps=60,sourceStart=start,seconds=seconds,files=[dict(path=str(f),sha256=sha(f)) for f in files],sameAudioPackets=True,captionedDirectFromComposite=True,noSecondGenerationCaptionEncode=True,humanReviewed=False))
  print(out,flush=True)
 finally:guard.release_lease(ownership)

if __name__=='__main__':main()
