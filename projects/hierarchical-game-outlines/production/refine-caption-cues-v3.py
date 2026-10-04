"""Short fixed-center game cues; preserve full bilingual narration and current voice."""
from pathlib import Path
import json,hashlib,re,difflib,shutil
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/hierarchical-game-outlines';WORK=BASE/'production/final-v1'
read=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
norm=lambda t:re.sub('[^a-z0-9가-힣]','',t.lower())
plan=read(WORK/'plan.json');selection=read(WORK/'cut-selection.json')
assert selection['sourceLayoutRevision']=='v3'
assert read(WORK/'source-layout-review-v2/direct-review.json')['status']=='rejected-source-layout-v2'
assert not (WORK/'caption-refinement-v3.json').exists(),'Review existing cue refinement; never repeat.'
old=read(WORK/'caption-alignment.json');approval=read(BASE/'production/voice-approval-v2.json')
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
for f in ['caption-alignment.json']:
 shutil.copy2(WORK/f,WORK/'source-layout-baseline-v2'/f)
shutil.copy2(BASE/'script/caption-units.json',WORK/'source-layout-baseline-v2/caption-units.json')
def groups(text):
 result=[];current=''
 for word in text.split():
  trial=(current+' '+word).strip()
  if current and font.getlength(trial)>620:result.append(current);current=word
  else:current=trial
 if current:result.append(current)
 assert all(font.getlength(s)<=620 for s in result),'A single word needs editorial inspection.'
 return result
def split_en(text,count):
 words=text.split();assert len(words)>=count
 result=[];left=words[:]
 for i in range(count-1):
  goal=len(' '.join(left))/(count-i)
  _,j=min((abs(len(' '.join(left[:j]))-goal),j) for j in range(1,len(left)-(count-i-1)+1))
  result.append(' '.join(left[:j]));left=left[j:]
 return result+[' '.join(left)]
entries=[];checks=[]
for scene in plan['scenes']:
 rows=[r for r in old['entries'] if r['scene']==scene['id']]
 if scene['classification']!='actual':entries.extend(rows);continue
 assert sha(ROOT/scene['voice'])==scene['audioSha256']
 asr=read(ROOT/scene['asr']);assert asr['audio_sha256']==scene['audioSha256']
 words=asr['words'];excluded=next((x for x in approval.get('timestampAlignmentExclusions',[]) if x['scene']==scene['id']),None)
 if excluded:words=words[:excluded['fromWordIndex']]
 expected=norm(''.join(r['ko'] for r in rows));recognized='';times=[]
 for wi,w in enumerate(words):
  a,b=w['timestamp'];a=float(a if a is not None else (times[-1][1] if times else 0));b=float(b if b is not None else next((v['timestamp'][0] for v in words[wi+1:] if v['timestamp'][0] is not None),scene['voiceSeconds']))
  b=min(max(a,b),scene['voiceSeconds']);chars=norm(w['text'])
  for j,ch in enumerate(chars):recognized+=ch;times.append((a+(b-a)*j/max(len(chars),1),a+(b-a)*(j+1)/max(len(chars),1)))
 match=difflib.SequenceMatcher(None,expected,recognized,autojunk=False);assert match.ratio()>.94
 mapping={block.a+j:block.b+j for block in match.get_matching_blocks() for j in range(block.size)}
 def mapped(i):
  if i in mapping:return mapping[i]
  k=min(mapping,key=lambda k:abs(k-i));return max(0,min(len(times)-1,mapping[k]+i-k))
 char_pos=0;made=[]
 for original in rows:
  pieces=groups(original['ko']);english=split_en(original['en'],len(pieces));bounds=[original['start']];pos=char_pos
  assert original['end']-original['start']>=len(pieces)*.18,'Very short cue needs manual split.'
  for i,k in enumerate(pieces[:-1]):
   pos+=len(norm(k));nominal=scene['start']+times[mapped(pos)][0]
   boundary=max(bounds[-1]+.18,min(original['end']-(len(pieces)-i-1)*.18,nominal))
   bounds.append(boundary)
  bounds.append(original['end'])
  for i,(k,e) in enumerate(zip(pieces,english)):
   made.append({**original,'ko':k,'en':e,'start':bounds[i],'end':bounds[i+1],'captionRefinement':'single line, pixel-measured width target620; current ASR word boundaries within preserved original cue bounds'})
  char_pos+=len(norm(original['ko']))
 assert char_pos==len(expected)
 assert norm(''.join(r['ko'] for r in made))==expected
 assert ' '.join(r['en'] for r in made)==' '.join(r['en'] for r in rows)
 checks.append({'scene':scene['id'],'currentAudioSha256':scene['audioSha256'],'oldCues':len(rows),'shortCues':len(made),'allKoreanWordsPreserved':True,'allEnglishWordsPreserved':True,'wordMatch':match.ratio(),'timing':'Current ASR word boundaries; outer original cue timing preserved. Final render/temporal QA pending.'})
 entries.extend(made)
assert entries==sorted(entries,key=lambda r:r['start'])
write(WORK/'caption-alignment.json',{**old,'entries':entries,'cues':len(entries),'captionRevision':'v3-full-screen-single-line-game-cues'})
def stamp(t):
 n=round(t*1000);return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'
for lang in ['ko','en']:
 (WORK/f'captions.{lang}.srt').write_text('\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n'+c[lang] for i,c in enumerate(entries))+'\n',encoding='utf-8')
write(BASE/'script/caption-units.json',[[r['scene'],r['paragraph'],r['ko'],r['en']] for r in entries])
write(WORK/'caption-refinement-v3.json',{'createdAt':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'sourceSelectionSha256':sha(WORK/'cut-selection.json'),'fullScreenGameRetained':True,'fixedCenter':[960,970],'style':'boxed-white-forest-v1','gameCueWidthTarget':620,'gameLines':1,'totalCues':len(entries),'scenes':checks,'allActualPixelsReviewed':False,'allPptPixelsReviewed':False,'finalVideoApproved':False})
print(json.dumps({'cues':len(entries),'actualCues':sum(x['shortCues'] for x in checks),'fullScreen':True,'finalApproved':False}))
