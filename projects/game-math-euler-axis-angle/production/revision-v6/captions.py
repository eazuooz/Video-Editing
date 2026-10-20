"""Clause-paired KO/EN captions from measured word timing, no audio or models.

Complete translated sentences are paired before optional meaningful clause
splits. Every original paragraph is retained; both languages share cue times.
SRT stays plain text. JSON provides a single semantic emphasis span per cue.
"""
from pathlib import Path
import argparse,hashlib,json,math,re,runpy,sys
from PIL import ImageFont
R=Path(__file__).resolve().parents[4];P=R/'projects/game-math-euler-axis-angle';H=Path(__file__).parent
O=P/'production/local/revision-v6';V=O/'voice';C=O/'captions'
FONT=Path('C:/Windows/Fonts/malgun.ttf');BOLD=Path('C:/Windows/Fonts/malgunbd.ttf')
PALETTE={'focus':'#0b6b66','result':'#1a7f37','caution':'#b42318'}
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sentences(s):return re.split(r'(?<=[.!?])\s+',s.strip())

# Each split is placed BEFORE the specified exact text, not at a word count.
# The paired boundaries retain the same condition/action/result meaning.
SPLITS={
 'v6-01.L03.S01':(['오일러 각으로'],['and carefully']),
 'v6-10.L04.S01':(['고정 축을 따라'],['as applying']),
 'v6-11.L04.S01':(['계속 위를 향하는'],['it used']),
 'v6-13.L03.S01':(['완성된 물체에서'],['rather than']),
 'v6-14.L02.S01':(['다른 프로그램의'],["into another program's"]),
 'v6-14.L03.S01':(['같은 회전을'],['and then read']),
 'v6-16.L01.S01':(['서로 따로'],['we need']),
 'v6-19.L01.S01':(['헤딩과 뱅크를','피치를'],['heading and bank','with pitch']),
 'v6-25.L06.S01':(['경계인'],['so mapping']),
 'v6-27.L04.S02':(['완전한 정규화를'],['it is not']),
 'v6-28.L02.S01':(['하나의 세 숫자'],['with one three-number']),
 'v6-28.L04.S01':(['회전을 계산하는'],['from the representation']),
 'v6-29.L05.S02':(['짐벌 락 자체와'],['but do not']),
 'v6-30.L04.S01':(['거리와 방향'],['and it preserves']),
 'v6-35.L03.S01':(['같은 축의 회전량을'],['scaling rotation']),
 'v6-35.L06.S01':(['계산에서도'],['we must distinguish']),
 'v6-39.L06.S01':(['그에 대응하는'],['or use a corresponding']),
 'v6-40.L03.S01':(['같은 좌표계로'],['can be added']),
 'v6-40.L06.S01':(['순간 각속도의 합을','벡터라는'],['and instantaneous','prevents confusion']),
 'v6-41.L07.S02':(['축·각에서는'],['and distinguish endpoint'])}
TERMS=[('오일러 각','Euler angles'),('항등 자세','identity orientation'),('왼손 좌표계','left-handed coordinate system'),
 ('헤딩','heading'),('피치','pitch'),('뱅크','bank'),('내재적 회전','intrinsic rotations'),('외재적 회전','extrinsic rotation'),
 ('행벡터','row vector'),('회전 행렬','rotation matrix'),('양자화','quantization'),('국소적','local'),('정규형','canonical form'),
 ('짐벌 락','gimbal lock'),('선형 보간','linear interpolation'),('floor','floor'),('라디안','radians'),('랩 함수','wrap function'),
 ('지수 사상','exponential map'),('회전벡터','rotation vector'),('단위벡터','unit vector'),('정규화','normalization'),('자유도','degrees of freedom'),('각속도','angular velocity')]
def cut_at(text,markers):
 out=[];at=0
 for marker in markers:
  found=text.find(marker,at);assert found>at,(marker,text)
  out.append(text[at:found].strip());at=found
 out.append(text[at:].strip());assert ' '.join(out)==text.strip()
 return out
def wrap(text,font,bold,emphasis):
 def length(part,offset):
  total=0.;cursor=offset
  for char in part:
   f=bold if emphasis and emphasis['start']<=cursor<emphasis['end'] else font
   total+=f.getlength(char);cursor+=1
  return total
 if length(text,0)<=1570:return [text]
 words=list(re.finditer(r'\S+',text));options=[]
 for word in words[1:]:
  a=text[:word.start()].rstrip();b=text[word.start():]
  aw,bw=length(a,0),length(b,word.start())
  if max(aw,bw)<=1570:options.append((abs(aw-bw),a,b))
 assert options,f'Clause needs a meaningful additional paired split; do not shrink/delete:{text}'
 _,a,b=min(options);return [a,b]
def display_aliases(text,source_offset,spans):
 result='';at=0;mapping=[];source_end=source_offset+len(text)
 for span in spans:
  if span['sourceEnd']<=source_offset or span['sourceStart']>=source_end:continue
  assert source_offset<=span['sourceStart']<span['sourceEnd']<=source_end,'A canonical token must not be split between cues'
  a,b=span['sourceStart']-source_offset,span['sourceEnd']-source_offset
  assert text[a:b]==span['spoken'];result+=text[at:a];start=len(result);result+=span['display'];end=len(result);at=b
  mapping.append(dict(sourceStart=a,sourceEnd=b,displayStart=start,displayEnd=end,spoken=span['spoken'],display=span['display'],meaning=span['meaning']))
 result+=text[at:];restored=result
 for span in reversed(mapping):
  assert restored[span['displayStart']:span['displayEnd']]==span['display']
  restored=restored[:span['displayStart']]+span['spoken']+restored[span['displayEnd']:]
 assert restored==text,'Every display alias must restore the exact spoken/source text'
 return result,mapping
def plans():
 ko_file=P/'script/revision-v6-article-flow/narration.ko.json';en_file=P/'script/revision-v6-article-flow/narration.en.json'
 ko,en=read(ko_file),read(en_file);rows=[];mapping=[]
 alias_file=H/'caption-aliases.json';alias=read(alias_file)
 assert alias['sourceHashes']==dict(ko=sha(ko_file),en=sha(en_file)),'Canonical span map must be re-reviewed if source text changes'
 alias_by={(x['language'],x['scene'],x['line']):x for x in alias['entries']}
 font=ImageFont.truetype(str(FONT),48);bold=ImageFont.truetype(str(BOLD),48)
 for scene,translation in zip(ko['scenes'],en['scenes']):
  assert scene['id']==translation['id'];assert len(scene['lines'])==len(translation['lines'])
  emphasized=set()
  for number,(k,e) in enumerate(zip(scene['lines'],translation['lines']),1):
   per_language={}
   for language,text in [('ko',k),('en',e)]:
    entry=alias_by.get((language,scene['id'],number))
    if entry:assert entry['sourceText']==text and entry['sourceTextSha256']==hashlib.sha256(text.encode('utf8')).hexdigest()
    per_language[language]=entry['spans'] if entry else []
   sk,se=sentences(k),sentences(e);assert len(sk)==len(se),(scene['id'],number)
   cue_ids=[];ko_offset=en_offset=0
   for sno,(ks,es) in enumerate(zip(sk,se),1):
    key=f'{scene["id"]}.L{number:02}.S{sno:02}'
    if key in SPLITS:kc,ec=[cut_at(text,markers) for text,markers in zip([ks,es],SPLITS[key])]
    else:kc,ec=[ks],[es]
    assert len(kc)==len(ec)
    for part,(source_kt,source_et) in enumerate(zip(kc,ec),1):
     ko_offset=k.index(source_kt,ko_offset);en_offset=e.index(source_et,en_offset)
     kt,aliases_ko=display_aliases(source_kt,ko_offset,per_language['ko']);et,aliases_en=display_aliases(source_et,en_offset,per_language['en'])
     emphasis_ko=emphasis_en=None
     # A definition's first meaningful term is highlighted only once per
     # scene and only when an equivalent English phrase is actually present.
     if not emphasized:
      for term,eng in TERMS:
       ka,ea=kt.find(term),et.lower().find(eng.lower())
       if ka>=0 and ea>=0:
        emphasis_ko=dict(start=ka,end=ka+len(term),role='focus');emphasis_en=dict(start=ea,end=ea+len(eng),role='focus');emphasized.add(term);break
     if scene['id']=='v6-41' and number==4 and '플러스 이십 도' in kt and 'positive 20 degrees' in et:
      a=kt.index('플러스 이십 도');b=et.index('positive 20 degrees');emphasis_ko=dict(start=a,end=a+len('플러스 이십 도'),role='result');emphasis_en=dict(start=b,end=b+len('positive 20 degrees'),role='result')
     kid=f'{key}.C{part:02}';cue_ids.append(kid)
     rows.append(dict(id=kid,scene=scene['id'],line=number,sentence=sno,clause=part,ko=kt,en=et,displayKo=kt,displayEn=et,
      sourceKo=source_kt,sourceEn=source_et,sourceKoOffset=ko_offset,sourceEnOffset=en_offset,
      displayAliasesKo=aliases_ko,displayAliasesEn=aliases_en,inverseDisplayAliasesRestoreExactSource=True,
      koLines=wrap(kt,font,bold,emphasis_ko),enLines=wrap(et,font,bold,emphasis_en),
      emphasisKo=emphasis_ko,emphasisEn=emphasis_en,semanticBoundary='paired complete sentence' if len(kc)==1 else 'explicit paired condition/action/result clause',
      nativePixelReview='pending',mobileMovingReview='pending'))
     ko_offset+=len(source_kt);en_offset+=len(source_et)
   assert ' '.join(r['sourceKo'] for r in rows if r['scene']==scene['id'] and r['line']==number)==k
   assert ' '.join(r['sourceEn'] for r in rows if r['scene']==scene['id'] and r['line']==number)==e
   mapping.append(dict(scene=scene['id'],line=number,cueIds=cue_ids))
 assert len(mapping)==250
 glossary=[]
 for term in alias['glossary']:
  mentions=[r['id'] for r in rows if term['ko'] in r['sourceKo']]
  definitions=[r['id'] for r in rows if r['scene']==term['firstScene'] and term['ko'] in r['sourceKo']]
  glossary.append(dict(term,firstMentionCueId=mentions[0] if mentions else None,definitionCueId=definitions[0] if definitions else None,displayRoute='Canonical Korean/English name and plain meaning in same-scene definition chip; subtitles retain original spoken explanation with exact canonical symbol/API spellings.'))
 symbols=[]
 for symbol in alias['symbolGlossary']:
  candidates=[r['id'] for r in rows if r['scene']==symbol['firstScene'] and r['line']==symbol['firstSourceLine'] and all(t in r['ko'] for t in symbol['displayMatch'])]
  assert candidates,('Canonical symbol first appearance must be visible',symbol['symbol'])
  symbols.append(dict(symbol,firstAppearanceCueId=candidates[0]))
 return dict(schemaVersion=1,policy='caption-clause-keyword-v1',inputs=dict(koSha256=sha(ko_file),enSha256=sha(en_file),fontSha256=sha(FONT),boldFontSha256=sha(BOLD),implementationSha256=sha(Path(__file__)),canonicalAliasMapSha256=sha(alias_file)),
  sceneCount=41,paragraphCount=250,cueCount=len(rows),sameSemanticBilingualCueTimes=True,allParagraphsRetained=True,
  palette=PALETTE,font=dict(file=str(FONT),boldFile=str(BOLD),size=48,maximumTextWidth=1570,lineHeight=62),
  cues=rows,paragraphMap=mapping,glossary=glossary,symbolGlossary=symbols,
  spokenDisplayProof='Exact inverse of every line-specific display span restores every original cue and all250KO/EN paragraphs; timing uses unchanged sourceKo and original PCM/ASR.',
  sourceReconstructionFields=['sourceKo','sourceEn'],displayTextFields=['displayKo','displayEn','koLines','enLines'],canonicalAliasMap='production/revision-v6/caption-aliases.json',
  noGlobalKoreanAliases=True,pixelReview='pending actual encoded output',humanPaceListening='pending')
def timestamp(seconds):
 value=round(seconds*1000);h,value=divmod(value,3600000);m,value=divmod(value,60000);s,ms=divmod(value,1000)
 return f'{h:02}:{m:02}:{s:02},{ms:03}'
def ass_time(seconds):
 value=round(seconds*100);h,value=divmod(value,360000);m,value=divmod(value,6000);s,cs=divmod(value,100)
 return f'{h}:{m:02}:{s:02}.{cs:02}'
def rectangle(x,y,w,h):return f'm {x:.2f} {y:.2f} l {x+w:.2f} {y:.2f} {x+w:.2f} {y+h:.2f} {x:.2f} {y+h:.2f}'
ASS_HEADER='''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Text,Malgun Gothic,48,&H00090B08,&H00090B08,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,0,0,5,0,0,0,1
Style: Box,Malgun Gothic,48,&H00FFFFFF,&H00FFFFFF,&H00181B16,&H00000000,0,0,0,0,100,100,0,0,1,3,0,7,0,0,0,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
def ass(captions,language):
 font=ImageFont.truetype(str(FONT),48);bold=ImageFont.truetype(str(BOLD),48);events=[];geometry=[]
 for cue in captions:
  lines=cue[language+'Lines'];emphasis=cue['emphasis'+language.title()];offset=0;widths=[];rendered=[]
  for text in lines:
   a=max(0,emphasis['start']-offset) if emphasis else 0;b=min(len(text),emphasis['end']-offset) if emphasis else 0
   if emphasis and 0<=a<b<=len(text):
    color=PALETTE[emphasis['role']].lstrip('#');bgr=color[4:6]+color[2:4]+color[0:2]
    encoded=text[:a]+r'{\b1\1c&H'+bgr+r'&}'+text[a:b]+r'{\b0\1c&H090B08&}'+text[b:]
    measured=font.getlength(text[:a])+bold.getlength(text[a:b])+font.getlength(text[b:])
   else:encoded=text;measured=font.getlength(text)
   assert measured<=1570+1e-6
   widths.append(measured);rendered.append(encoded);offset+=len(text)+1
  width=max(widths)+44;height=len(lines)*62+22;x=960-width/2;y=970-height/2
  assert x>=150 and y>=880 and y+height+14<=1060
  when=f'{ass_time(cue["start"])},{ass_time(cue["end"])}'
  assert ass_time(cue['start'])!=ass_time(cue['end']),'Zero-centisecond cue needs word-context review'
  events.append(f'Dialogue: 10,{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\bord0\\1c&H323C07&\\p1}}'+rectangle(x+14,y+14,width,height))
  events.append(f'Dialogue: 11,{when},Box,,0,0,0,,{{\\an7\\pos(0,0)\\p1}}'+rectangle(x,y,width,height))
  for i,text in enumerate(rendered):events.append(f'Dialogue: 12,{when},Text,,0,0,0,,{{\\an5\\pos(960,{970+(i-(len(lines)-1)/2)*62:.2f})}}'+text)
  geometry.append(dict(id=cue['id'],start=cue['start'],end=cue['end'],widths=widths,box=[x,y,width,height],emphasis=emphasis))
 (O/f'captions.{language}.ass').write_text(ASS_HEADER+'\n'.join(events)+'\n',encoding='utf8')
 return geometry
def main():
 arg=argparse.ArgumentParser();arg.add_argument('--plan-only',action='store_true');args=arg.parse_args()
 assert read(R/'shared/publishing/video-production-control.json')['selectedVideo']==P.name
 design=plans();save(H/'caption-plan.json',design)
 if args.plan_only:
  print('Bilingual semantic clause plan:',design['cueCount'],'cues;250paragraphs retained; no timing/media written');return
 timeline=read(H/'timeline.json');alignment=read(V/'voice-alignment.json')
 assert timeline['inputs']['alignmentSha256']==sha(V/'voice-alignment.json')
 assert design['inputs']['koSha256']==timeline['inputs']['koSha256']
 old=sys.argv[:];sys.argv=[sys.argv[0],P.name]
 try:helpers=runpy.run_path(str(R/'production/batches/game-math-part2-full-series/align.py'),run_name='v6_caption_math_normalization')
 finally:sys.argv=old
 normalize=helpers['normalized'];scenes={s['id']:s for s in timeline['scenes']};raw={s['id']:s for s in alignment['scenes']}
 spoken=read(H/'voice-input.ko.json');source_ko=read(P/'script/revision-v6-article-flow/narration.ko.json')
 source={s['id']:s for s in source_ko['scenes']};speech={s['id']:s for s in spoken['scenes']};offsets={};previous=0.;captions=[]
 for row in design['cues']:
  sid,line=row['scene'],row['line'];scene=scenes[sid];data=raw[sid]['lines'][line-1]
  key=(sid,line);offset=offsets.get(key,0);display=row['sourceKo']
  # The only lexical display/speech alias is lowercase e, pronounced 이.
  # Both are a single normalized character; canonical display is preserved.
  timing_text=display.replace('소문자 e','소문자 이') if sid=='v6-32' and line==1 else display
  count=len(normalize(timing_text));assert count>0
  starts,ends=data['characterStarts'],data['characterEnds'];assert offset+count<=len(starts),(row['id'],offset,count,len(starts))
  a,b=starts[offset],ends[offset+count-1];offsets[key]=offset+count
  def mapped(t):
   sample=round(t*scene['sampleRate']);shift=sum(x['insertFrames'] for x in scene['pauseInsertions'] if x['sourceSample']<=sample)
   return scene['startFrame']/60+t+shift/60
  begin,end=mapped(a),mapped(b);assert end>begin and begin>=previous-.002,(row['id'],begin,end,previous)
  assert begin>=2 and end<=timeline['temporalContract']['outroStartFrame']/60,'No captions over branding/member outro'
  # A cue ends with its actual speech; it never stays over a demonstration
  # hold or displays a confirmation answer before that answer is spoken.
  cue=dict(row,start=begin,end=end,rawStart=a,rawEnd=b,startFrame=math.floor(begin*60+1e-8),endFrame=math.ceil(end*60-1e-8))
  captions.append(cue);previous=end
 for (sid,line),offset in offsets.items():assert offset==len(raw[sid]['lines'][line-1]['characterStarts']),(sid,line,'caption text/timing mismatch')
 C.mkdir(parents=True,exist_ok=True)
 for lang in ['ko','en']:
  blocks=[]
  for i,cue in enumerate(captions,1):blocks.append(f'{i}\n{timestamp(cue["start"])} --> {timestamp(cue["end"])}\n'+ '\n'.join(cue[lang+'Lines']))
  (O/f'captions.{lang}.srt').write_text('\n\n'.join(blocks)+'\n',encoding='utf8')
 result=dict(design);result.update(cues=captions,timelineSha256=sha(H/'timeline.json'),alignmentSha256=sha(V/'voice-alignment.json'),
  temporalOrigin='global final video including2s branding',manualSrtPlainText=True,captionBox='boxed-white-forest-v1',
  captionGeometry=dict(x=960,y=970,fontSize=48,lineHeight=62,maxLines=2,padding=[22,11],border=3,shadowOffset=[14,14]),
  outputs={lang:dict(file=(O/f'captions.{lang}.srt').relative_to(R).as_posix(),sha256=sha(O/f'captions.{lang}.srt')) for lang in ['ko','en']})
 geometry={lang:ass(captions,lang) for lang in ['ko','en']}
 save(C/'caption-layout.json',dict(style='boxed-white-forest-v1',policy='caption-clause-keyword-v1',rows=geometry,fontSha256=sha(FONT),boldFontSha256=sha(BOLD),timelineSha256=result['timelineSha256'],pixelReview='pending actual encoded output'))
 save(C/'captions.json',result);save(C/'caption-alignment-review.json',dict(inputs=result['inputs'],timelineSha256=result['timelineSha256'],outputs=result['outputs'],paragraphs=result['paragraphMap'],sameCueCountAndTimes=True,all250ParagraphsRetained=True,pixelReview='pending'))
 print('Measured bilingual clause captions:',len(captions),'same-time cues;250paragraphs retained; no caption boxes during observations')
if __name__=='__main__':main()
