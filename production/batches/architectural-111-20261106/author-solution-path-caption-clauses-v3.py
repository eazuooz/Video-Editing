"""Author Nar7 meaning clauses and translation-display boundaries, without clocks."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,re,sys
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'projects/shorts-leveldesign-11-05'
HELPER=Path(__file__).with_name('verify-solution-path-caption-clauses.py')
HELPER_SHA='92e7f8e2ad7b57acb3171c38aa415ec8f2381b627a5627b5f14c7521e3bb17d5'
PINS={
 'narration-final-v7.json':'0e4786acc33531b5e1df18a95f6c4a07ab85fc86c4c8f07221ae800662ccf0a1',
 'caption-clauses-v2.json':'b1629be657702b8910cbf4eafafcabbd7452a688ae0b976c04a898aadf47fc0c',
 'translated-caption-display-boundaries-v2.json':'f3d174651b0af77bf85847f76e53dec8e07c8a5d4143d936fc260f75f12e7be1',
 'voice-asr-content-review-v14.json':'aefbc0825979537ba35eac69164a613502ad0b2dda50640b53dec469982b2661',
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def require(v,message):
 if not v:raise ValueError(message)
def immutable(p,value):
 data=(json.dumps(value,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
 if p.exists():require(p.read_bytes()==data,'Preserve existing authored version: '+str(p))
 else:p.write_bytes(data)
def load():
 require(sha(HELPER)==HELPER_SHA,'Neutral measured typography helper changed')
 for name,digest in PINS.items():require(sha(PROJECT/name)==digest,'Changed authored input: '+name)
 s=importlib.util.spec_from_file_location('caption3_neutral_typography',HELPER)
 style=importlib.util.module_from_spec(s);s.loader.exec_module(style)
 return style
def wrap(cue,style,fs):
 text=cue['text']
 if not cue['emphasis']:
  if fs[500].getlength(text)<=800:cue['lines']=[text]
  else:
   options=[]
   for match in re.finditer(' ',text):
    a,b=text[:match.start()],text[match.end():]
    widths=[fs[500].getlength(a),fs[500].getlength(b)]
    if max(widths)<=800:options.append((max(widths),abs(widths[0]-widths[1]),a,b))
   require(options,'Author a shorter meaning clause: '+text)
   _,_,a,b=min(options);cue['lines']=[a,b]
 cue['measuredLineWidthsPx']=style.widths(cue,fs)
 return cue
def fresh_cues(group,ko_texts,en_specs,style,fs):
 for lang,texts in [('ko',ko_texts),('en',[row[0] for row in en_specs])]:
  require(' '.join(texts)==group[lang],'Complete new meaning group differs: '+group['id']+'/'+lang)
  rows=[];cursor=0
  for i,text in enumerate(texts,1):
   cue=dict(id=f"{group['id']}-{lang}{i}",text=text,groupCharRange=[cursor,cursor+len(text)],emphasis=[],clock=dict(startSample=None,endSample=None,startFrame=None,endFrameExclusive=None),lines=[text])
   if lang=='ko':cue['spokenLiteralAnchorKo']=text
   else:
    anchor=en_specs[i-1][1];start=group['ko'].find(anchor)
    require(start>=0,'Missing authored whole-word meaning anchor')
    cue['_localKoAnchor']=[start,start+len(anchor)]
    cue['spokenKoAnchor']=dict(text=anchor,sourceCharRange=None,boundaryScope='semantic-group',actualWordBoundaryVerified=False,selection='Complete authored Korean meaning clause; actual whole-ASR-word timing still required.')
    cue['timingBasis']='Meaning-linked translation display; no English recognition, character fractions or invented word clock.'
   rows.append(wrap(cue,style,fs));cursor+=len(text)+1
  group[lang+'Cues']=rows
def prepare():
 style=load();fs=style.fonts();narr=read(PROJECT/'narration-final-v7.json')
 qualification=read(PROJECT/'voice-asr-content-review-v14.json')
 require(qualification['numericalHold'] is False and qualification['newTargetsLiteralMatch'] is True and qualification['downstreamPreparationAllowed'] is True,'Actual revised explanations are not qualified')
 proof_pin=qualification['inputs']['immutableVoiceProof'];require(pin(proof_pin['path'])==proof_pin,'Actual qualified voice proof changed')
 proof=read(proof_pin['path']);mapping=proof['paragraphMapping']
 require(len(mapping)==51 and len(proof['reusedRawScenes'])==48,'Exact Nar7 physical mapping required')
 prior=read(PROJECT/'caption-clauses-v2.json');d=copy.deepcopy(prior)
 groups={g['id']:g for g in d['groups']}
 g=groups['P8a'];g['ko']=narr['narrationKo'][7].split(' 처음부터',1)[0];g['en']=narr['paragraphsEn'][7].split(' In this process',1)[0]
 fresh_cues(g,['길이 가장 아래쪽 줄에 이르러,','다시 아래로 향하는 경우를 보죠.','그때는 더 내려가지 않고,','현재 방을 출구로 정합니다.'],[
  ('Consider the route reaching the bottom row','길이 가장 아래쪽 줄에 이르러,'),
  ('and attempting to go farther down.','다시 아래로 향하는 경우를 보죠.'),
  ('Instead of going farther down,','그때는 더 내려가지 않고,'),
  ('the current room becomes the exit.','현재 방을 출구로 정합니다.'),
 ],style,fs)
 g=groups['P13a'];g['ko']=narr['narrationKo'][12].split(' 출구까지',1)[0];g['en']=narr['paragraphsEn'][12].split(' Connected rooms',1)[0]
 fresh_cues(g,['HD 화면의 캐릭터는 보물을 들고','발판을 지나, 출구 근처까지 내려옵니다.','큰 바위가 굴러와','캐릭터와 부딪힙니다.','충돌한 캐릭터가 쓰러지고,','출구로 가던 이동도 끝납니다.'],[
  ('In the HD footage, the character carries treasure','HD 화면의 캐릭터는 보물을 들고'),
  ('past the ledges and descends near the exit.','발판을 지나, 출구 근처까지 내려옵니다.'),
  ('A large boulder rolls into the character.','큰 바위가 굴러와 캐릭터와 부딪힙니다.'),
  ('The character falls,','충돌한 캐릭터가 쓰러지고,'),
  ('ending the movement toward the exit.','출구로 가던 이동도 끝납니다.'),
 ],style,fs)
 logical=0;ids=set();max_width=0
 for paragraph in range(1,15):
  rows=[g for g in d['groups'] if g['paragraph']==paragraph]
  for lang,source in [('ko',narr['narrationKo'][paragraph-1]),('en',narr['paragraphsEn'][paragraph-1])]:
   require(' '.join(g[lang] for g in rows)==source,'Full paragraph reconstruction changed')
   cursor=0
   for g in rows:
    previous_start=g[lang+'SourceCharRange'][0];g[lang+'SourceCharRange']=[cursor,cursor+len(g[lang])];local=0
    if lang=='ko':g['_oldKoStart']=previous_start
    for cue in g[lang+'Cues']:
     require(cue['id'] not in ids,'Duplicate clause ID');ids.add(cue['id'])
     require(g[lang][local:local+len(cue['text'])]==cue['text'],'Clause changed canonical text')
     cue['sourceCharRange']=[cursor+local,cursor+local+len(cue['text'])];cue['groupCharRange']=[local,local+len(cue['text'])]
     require(cue['clock']==dict(startSample=None,endSample=None,startFrame=None,endFrameExclusive=None),'Authoring must not assign clocks')
     if lang=='en':
      old_start=g['_oldKoStart'];new_start=g['koSourceCharRange'][0]
      if '_localKoAnchor' in cue:a,b=cue.pop('_localKoAnchor');cue['spokenKoAnchor']['sourceCharRange']=[new_start+a,new_start+b]
      else:
       a,b=cue['spokenKoAnchor']['sourceCharRange'];cue['spokenKoAnchor']['sourceCharRange']=[a-old_start+new_start,b-old_start+new_start]
      a,b=cue['spokenKoAnchor']['sourceCharRange'];require(narr['narrationKo'][paragraph-1][a:b]==cue['spokenKoAnchor']['text'],'Meaning anchor changed')
     measured=style.widths(cue,fs);require(measured==cue['measuredLineWidthsPx'],'Measured typography changed');max_width=max(max_width,*measured);local+=len(cue['text'])+1
    require(' '.join(c['text'] for c in g[lang+'Cues'])==g[lang],'Clause omission')
    cursor+=len(g[lang])+1
  for g in rows:
   a,b=g['koSourceCharRange'];physical=[r for r in mapping if r['paragraph']==paragraph and a<=r['sourceCharRange'][0] and r['sourceCharRange'][1]<=b]
   require(' '.join(r['canonicalText'] for r in physical)==g['ko'],'Meaning group split a physical canonical sentence')
   g['koLogicalSentences']=[dict(sceneId=r['sceneId'],sentenceIndexZeroBased=r['component']-1,canonicalKo=r['canonicalText'],sourceCharRange=r['sourceCharRange']) for r in physical];logical+=len(physical)
 require(logical==51,'Exact51 sentence coverage required')
 # Translation progression is authored at complete Korean-word boundaries.
 old_display=read(PROJECT/'translated-caption-display-boundaries-v2.json');by_old={g['groupId']:g for g in old_display['groups']};display=[]
 for g in d['groups']:
  start,end=g['koSourceCharRange'];old_start=g.pop('_oldKoStart')
  if g['id'] in ('P8a','P13a'):
   offsets=[start]+[c['spokenKoAnchor']['sourceCharRange'][1] for c in g['enCues']]
  else:offsets=[x-old_start+start for x in by_old[g['id']]['koDisplayBoundaryCharOffsets']]
  require(len(offsets)==len(g['enCues'])+1 and offsets[0]==start and offsets[-1]==end and all(a<b for a,b in zip(offsets,offsets[1:])),'Translation display progression differs')
  text=narr['narrationKo'][g['paragraph']-1];words=list(re.finditer(r'\S+',text));anchors=[]
  for value in offsets:
   left=next((w for w in words if w.end()==value),None);right=next((w for w in words if w.start()==value),None)
   if left is not None:
    i=words.index(left);right=words[i+1] if i+1<len(words) else None
   elif right is not None:
    i=words.index(right);left=words[i-1] if i else None
   require(value in (start,end) or left is not None or any(w.start()==value for w in words),'Display boundary inside a source word')
   anchors.append(dict(offset=value,leftWordKo=left.group() if left else None,rightWordKo=right.group() if right else None,leftWordCharRange=[left.start(),left.end()] if left else None,rightWordCharRange=[right.start(),right.end()] if right else None,reason='Authored complete-Korean-word meaning boundary; resolve only against actual whole-ASR-word endpoints.',actualSample=None,actualFrame=None))
  display.append(dict(groupId=g['id'],paragraph=g['paragraph'],enCueIds=[c['id'] for c in g['enCues']],koDisplayBoundaryCharOffsets=offsets,boundaryAnchors=anchors,semanticTimingVerified=False,reorderedMeaningAnchorsRetained=True,originalMeaningWindowsNonordered=any(x['spokenKoAnchor']['sourceCharRange'][0]>y['spokenKoAnchor']['sourceCharRange'][0] for x,y in zip(g['enCues'],g['enCues'][1:])),resolutionRule='Use literal whole observed word endpoints; no within-word interpolation, character ratios or zero-length anchor.',displayCutAuthority='Authored translation progression; actual timing/mobile review remains required.'))
 counts=dict(paragraphs=14,semanticGroups=len(d['groups']),koLogicalSentences=51,koCues=sum(len(g['koCues']) for g in d['groups']),enCues=sum(len(g['enCues']) for g in d['groups']))
 d.update(schemaVersion='11.05-caption-clauses-v3',status='Nar7 canonical meaning clauses; actual qualified V10 source, actual word timing and pixels pending',sourceNarration=pin(PROJECT/'narration-final-v7.json'),validatorSourceSHA256=sha(__file__),counts=counts,preservedPreviousCaptionClauses=pin(PROJECT/'caption-clauses-v2.json'),sourceCorrection='Explicit P8/P13 Nar7 rewrite. Other meaning-group texts and clauses preserved; changed paragraph offsets rebased.',validationContract='Exact51 physical sentence/14 paragraph reconstruction against current immutable V10 proof; measured fixed48px mixed-weight typography. No clocks/listening/pixel/human approval.',rawVoiceQualification=pin(PROJECT/'voice-asr-content-review-v14.json'))
 t=dict(schemaVersion='11.05-translated-caption-display-boundaries-v3',topicId='11.05',sourceNarration=d['sourceNarration'],captionClauses=None,scope='Nar7 full semantic translation progression, matching current51 physical sentence mapping; no fabricated clocks.',groups=display,counts=dict(groups=len(display),enCues=counts['enCues']),originalMeaningAnchorsUsedAsClock=False,actualTimingAssigned=False,actualPixelReview=False,semanticTimingVerified=False,actualListening=False,humanApproval=False,remainingReview=['Resolve each used boundary from positive whole ASR words of the exact V10 voice; reflow instead of interpolating.','Verify translated meaning, actual captioned1080/375 and moving source/cat clearance.'],platformActions=[],preservedPreviousDisplayBoundaries=pin(PROJECT/'translated-caption-display-boundaries-v2.json'))
 return d,t,dict(physicalSentences=51,paragraphs=14,semanticGroups=len(display),koCues=counts['koCues'],enCues=counts['enCues'],maxMeasuredLineWidthPx=max_width,actualClocksAssigned=False,actualPixelReview=False,humanApproval=False)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--write',action='store_true');args=ap.parse_args();d,t,summary=prepare()
 if args.write:
  cp=PROJECT/'caption-clauses-v3.json';immutable(cp,d);t['captionClauses']=pin(cp);immutable(PROJECT/'translated-caption-display-boundaries-v3.json',t)
 print(json.dumps(dict(summary,written=args.write),ensure_ascii=False))
if __name__=='__main__':main()
