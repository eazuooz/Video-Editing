"""Propose source/action/PCM timing together. No render, mix or caption approval."""
from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,math
import numpy as np,soundfile as sf
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
read=lambda p:json.loads(p.read_text(encoding='utf8'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
target=BASE/'measured-edit-v2';assert not target.exists(),'Preserve previous measured edit.'
target.mkdir();m=read(BASE/'measured-voice-v2.json');mapping=read(BASE.parent/'sources/action-map.json');bank=read(ROOT/mapping['bank']);by={c['id']:c for c in bank['cuts']}
def shot(id,a=None,z=None,suffix=''):
 c=dict(by[id]);c['bankCutId']=id;c['id']=id+suffix;c['classification']='actual';c['sourceInSeconds']=a if a is not None else c['sourceInSeconds'];c['sourceOutSeconds']=z if z is not None else c['sourceOutSeconds'];c['frames']=round((c['sourceOutSeconds']-c['sourceInSeconds'])*60);c['seconds']=c['frames']/60;c['speed']=1;c['finalApproved']=False
 assert c['frames']>0 and c['sourceInSeconds']>=by[id]['sourceInSeconds']-.0001 and c['sourceOutSeconds']<=by[id]['sourceOutSeconds']+.0001
 return c
study={'id':'potion-state-study','classification':'explanation','frames':360,'seconds':6,'visibleAction':'White2.5D comparison of selected potion entries, completed label and missing-materials warning; observation summary rather than invented successful payment.','sourceReference':{'videoId':'xNUn4fn4br8','from':40,'to':42},'sourceTimeCountedAsActual':False,'finalApproved':False}
groups={
 '02':[[shot('ammo-01'),shot('ammo-06')],[shot('ammo-11')],[shot('overview-03')],[shot('shatter-03'),shot('overview-04')]],
 '04':[[shot('ammo-03'),shot('ammo-08'),shot('ammo-02')],[shot('ammo-04'),shot('ammo-05')],[shot('shatter-04'),study],[shot(i) for i in ['bounty-01','bounty-02','bounty-08','bounty-09','bounty-10','bounty-11']]+[shot('ammo-09',43,44,'-head')],[shot('ammo-09',44,49,'-tail'),shot('ammo-10')]],
 '06':[[shot(i) for i in ['ammo-12','ammo-13','ammo-14','coop-01','coop-fit-combat-01','shatter-02','bounty-03','bounty-12','bounty-13']]],
 '08':[[shot('ranch-02',23,29,'-pet-milk'),shot('ranch-03'),shot('ranch-05'),shot('ranch-05b')],[shot('appearance-01'),shot('appearance-03')],[shot('ranch-02',29,34,'-other-collection'),shot('ranch-02',21,23,'-care')],[shot('base-02'),shot('coop-fit-base-01'),shot('overview-07')]],
 '10':[[shot(i) for i in ['base-01','shatter-06','bounty-04','bounty-05','bounty-14','bounty-15','bounty-16','bounty-17','bounty-18','overview-05','shatter-07','improved-combat-01']]],
 '12':[[shot(i) for i in ['overview-02','overview-01','ammo-15','coop-02','wool-01','wool-06-brick','wool-02','wool-07','wool-03','wool-04','overview-06','shatter-08','bounty-06','bounty-07']]]
}
rate=24000;scenes=[];cursor=120
for s in m['scenes']:
 sid=s['id'];segments=[];audio=[];pcm_cursor=0;output=0
 def add_pcm(a,z):
  global output
  assert z>=a
  if z>a:audio.append({'kind':'preserved-current-PCM','fromSample':a,'toSample':z,'outputFromSample':output,'outputToSample':output+z-a});output+=z-a
 def add_gap(n,reason):
  global output
  assert n>=0
  if n:audio.append({'kind':'inserted-silence','samples':n,'outputFromSample':output,'outputToSample':output+n,'reason':reason});output+=n
 def current_quiet(seconds,lo,hi):
  x,sr=sf.read(ROOT/s['audio'],dtype='float32');assert sr==rate
  win=round(.016*rate);candidates=[]
  for k in range(round(lo*rate),round(hi*rate),24):
   q=x[k-win//2:k+win//2];r=float(np.sqrt(np.mean(q*q)));candidates.append((r+abs(k/rate-seconds)*.0005,k,r))
  _,p,r=min(candidates);assert r<.012,'No sufficiently quiet sentence gap'
  return p,r
 if s['classification']=='explanation':
  # Preserve all actual explanation PCM; only the newly added post-speech gap differs.
  tail=23 if sid=='01' else 44 if sid=='13' else 43
  frames=s['minimumSpeechFrames']+tail;add_pcm(0,s['samples']);add_gap(frames*400-output,'Standard post-speech scene transition; essential explanation unchanged.')
  paragraph_ends=[p['pcmToSample']/rate for p in s['paragraphs']];paragraph_ends[-1]=frames/60
  segments=[{'id':'explanation-'+sid,'classification':'explanation','frames':frames,'seconds':frames/60}]
 else:
  for group in groups[sid]:segments.extend(group)
  frames=sum(c['frames'] for c in segments)
  if sid in ['02','04','08']:
   paragraph_ends=[];slots=[sum(c['frames'] for c in g) for g in groups[sid]]
   # Speech ends need not equal a shot change. Carry complete PCM across a
   # nearby meaningful transition rather than cutting the last syllable.
   if sid=='04':slots[2]+=7;slots[4]-=7
   if sid=='08':slots[2]-=12;slots[3]+=12
   assert len(slots)==len(s['paragraphs'])
   for p,nframes in zip(s['paragraphs'],slots):
    before=output
    if sid=='08' and p['paragraph']==1:
     join,r=current_quiet(6.44,6.335,6.525);add_pcm(p['pcmFromSample'],join);add_gap(round(1.7*rate),'Finish the feed-selection shot before the narrated mounted movement.');add_pcm(join,p['pcmToSample'])
    else:add_pcm(p['pcmFromSample'],p['pcmToSample'])
    desired=before+nframes*400;assert desired>=output,f'{sid} paragraph{p["paragraph"]} needs more measured source time'
    add_gap(desired-output,'Observe the already named distinct action/selection at normal source speed; no loop/idle extension.');paragraph_ends.append(output/rate)
  else:
   after=1 if sid in ['06','10'] else 2
   gap=round((5.66 if sid=='06' else 1.5 if sid=='10' else 5.64)*rate)
   boundary=s['paragraphs'][after-1]['pcmToSample'];add_pcm(0,boundary);add_gap(gap,'Align the next narrated action with its actual source transition.');add_pcm(boundary,s['samples']);assert output<=frames*400
   add_gap(frames*400-output,'Close the current observation before the following explanation.');paragraph_ends=[p['pcmToSample']/rate+(gap/rate if p['paragraph']>=after else 0) for p in s['paragraphs']];paragraph_ends[-1]=frames/60
  assert output==frames*400
 local=0
 for c in segments:c['startFrame']=cursor+local;c['localFromFrame']=local;local+=c['frames'];c['endFrameExclusive']=cursor+local
 # Entire current PCM must occur once in its original order; inserted gaps are separate.
 kept=[a for a in audio if a['kind']=='preserved-current-PCM'];assert kept[0]['fromSample']==0 and kept[-1]['toSample']==s['samples'];assert all(a['toSample']==b['fromSample'] for a,b in zip(kept,kept[1:]));assert sum(a['toSample']-a['fromSample'] for a in kept)==s['samples']
 scenes.append({**{k:s[k] for k in ['id','title','audio','audioSha256','samples','sampleRate']},'startFrame':cursor,'frames':frames,'seconds':frames/60,'segments':segments,'pcmPlacement':audio,'paragraphEnds':paragraph_ends,'speechEvidence':s['paragraphs'],'allCurrentPcmPreserved':True,'sourceActionCaptionApproval':False});cursor+=frames
cuts=[c for s in scenes for c in s['segments'] if c['classification']=='actual'];actual=sum(c['frames'] for c in cuts);explanation=sum(c['frames'] for s in scenes for c in s['segments'] if c['classification']=='explanation')
for source in bank['sources']:
 chosen=sorted([c for c in cuts if c['sourceId']==source['videoId']],key=lambda c:c['sourceInSeconds'])
 for a,z in zip(chosen,chosen[1:]):assert a['sourceOutSeconds']<=z['sourceInSeconds']+.00001,'No repeated source footage'
assert abs(actual-explanation*1.5)<=1
result={'schemaVersion':1,'status':'measured-source-and-current-PCM-proposal-awaiting-every-caption-and-source-frame-review','createdAt':datetime.now(timezone.utc).isoformat(),'fps':60,'width':1920,'height':1080,'brandingFrames':120,'membershipFrames':600,'scenes':scenes,'actualFrames':actual,'explanationFrames':explanation,'bodyFrames':actual+explanation,'finalFrames':cursor+600,'body60_40ErrorFrames':actual-1.5*explanation,'actualSourceCuts':len(cuts),'sources':bank['sources'],'inputHashes':{'voiceMeasurement':sha(BASE/'measured-voice-v2.json'),'sourceBank':sha(ROOT/mapping['bank']),'currentVoiceReview':sha(BASE/'voice-approval-v2.json')},'sourceReallocation':{'bounty01and02':'Move to04 before the pickups/machine/prompt, matching its other-trailer sentence.','overview07':'Move the short portal-return action to08 as a movement/function contrast;12 asks a catalogue question without claiming an exact return unlock.','ranch02':'Split distinct source intervals once: daytime petting/milking before feed/riding; nighttime separate collection and earlier care under the function comparison. Nighttime icons are not milk or proof of animal unlocks.','shatter01':'Omit the3s general combat; material/research/crafting actions already illustrate04.','potion':'2s actual UI then6s independent white2.5D observation comparison counted as explanation.'},'original52ParagraphsRetained':True,'all7ExplanationPcmPreserved':True,'sourceAudio0':True,'agentGames0':True,'noLoopsOrSlowing':True,'finalTimingApproved':False,'finalFixedCaptionApproval':False,'finalMixBuilt':False,'humanWholeListening':'pending','finalPublicRights':'pending'}
(target/'plan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({'actualFrames':actual,'explanationFrames':explanation,'finalFrames':cursor+600,'actualSeconds':actual/60,'explanationSeconds':explanation/60,'finalSeconds':(cursor+600)/60,'ratioErrorFrames':result['body60_40ErrorFrames'],'scenes':[{'id':s['id'],'seconds':s['seconds']} for s in scenes]}))
