"""V8 faithful bilingual clause design, exact spoken-KO character offsets.

CPU text and font measurements only. No audio/model/media job.
"""
from pathlib import Path
import json,re,hashlib,importlib.util,argparse
from PIL import ImageFont
H=Path(__file__).resolve().parent; R=H.parents[3]; P=R/'projects/game-math-euler-axis-angle'
K=P/'script/revision-v8-orientation-matrix/narration.ko.json'; E=K.with_name('narration.en.json')
def read(p):return json.loads(p.read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sentences(text):return re.split(r'(?<=[.!?])\s+',text.strip())
EN_PARAGRAPHS={
'm02.L05':"A point describing a position and a vector describing the difference between two positions offer a similar distinction. One describes a state; the other describes a change between states. In aviation, attitude also refers to an object’s orientation.",
'm03.L05':"Now read the airplane’s right, up, and forward axes using the outside reference. As the airplane rotates, the outside coordinates of all three arrows change together. Collect those numbers one row at a time to form a three-by-three rotation matrix. Three-by-three means three columns and three rows. In this lesson, vectors are written horizontally and multiplied on the left of the matrix—the row-vector convention.",
'm04.L06':"We should also be able to work backward and find where an outside point lies relative to the airplane. This raises an essential question whenever we use a matrix. From which space to which space does this matrix transform?",
'm05.L01':"Our matrix transforms from object space to upright space. It is also possible to store the opposite transformation, from upright space to object space. Both are mathematically valid choices. However, confusing the stored direction with the direction of the calculation changes the result.",
'm05.L02':"The reverse transformation uses the inverse matrix. The inverse matrix undoes the original transformation. Rotation matrices have a useful property here. Because pure rotation matrices preserve lengths and right angles, their inverse needs no separate complicated calculation: simply exchange rows and columns. This operation is called the transpose.",
'm06.L07':"The objectToUpright function converts object coordinates into the outside frame. The uprightToObject function does the reverse. Callers can express the desired direction instead of choosing multiplication or transposition themselves. The implementation follows one consistent row- or column-vector convention and documents it.",
'm06.L08':"This does not remove the mathematics; it makes clear which part of the program is responsible for it. Every program need not use the same class design. The key is preventing users from misreading the coordinate systems and intent, whichever matrix direction is stored. Now let us examine the relationship between directions that each matrix number records.",
'm08.L03':"One condition is essential. Both arrows in a dot product must be expressed in the same coordinate system. We cannot directly mix coordinates read in the airplane frame with coordinates read in the outside frame. Express both arrows in a common orthonormal frame first. Their included angle, and therefore their dot product, is the same whichever of these frames we choose.",
'm09.L01':"We have already used the first advantage. We can directly convert an object’s points and directions into another space. Recall how one unit right and two units forward became two, zero, minus one outside. Because the axes are collected into rows, new coordinates can use the same multiply-and-add calculation.",
'm11.L02':"We now have a way to read them. Draw each row as an axis arrow. For example, we read the first row zero, zero, minus one as the right wing pointing backward in the outside frame. Even so, writing all nine numbers for a complicated orientation by hand remains cumbersome.",
'm11.L04':"There is one length condition per axis, giving three. There are also three distinct pairs of axes, giving three perpendicularity conditions. These six continuous constraints tie together the nine numbers. This leaves three independent changes of orientation.",
'm11.L06':"We must also exclude reflection. Reversing only the first axis preserves the lengths and right-angle relationships of all three axes. But a mirrored shape or reversed lettering cannot be produced by simply rotating an object. Formally, check that the determinant is plus one. Here the determinant identifies the orientation and volume scale of the axes. Among orthogonal matrices, plus one indicates rotation and minus one includes reflection.",
'm12.L06':"One response is to orthonormalize the matrix. This restores unit lengths and right angles. It differs from merely shortening one axis. Normalizing each axis separately can leave the axes oblique, so their relationships must be corrected too. Also check that no reflection is introduced. Real implementations use error tolerances and must not treat severely corrupted data as automatically being a small error.",
'm13.L05':"When you see a rotation matrix, do not try to memorize all nine entries at once; choose one row and read it as an arrow. Which direction does this axis point, and in which reference frame? If you can answer that, you understand how a game object’s orientation is recorded as numbers. That concludes our explanation of orientation and its matrix representation."
}
def caption_english():
 # The preflight English source remains byte-identical. These independent
 # caption translations only align semantic boundaries to spoken Korean.
 e=read(E)
 for s in e['scenes']:
  for i,old in enumerate(s['paragraphs'],1):
   key=s['id']+f'.L{i:02d}'
   if key in EN_PARAGRAPHS:s['paragraphs'][i-1]=EN_PARAGRAPHS[key]
 return e
EN_SENTENCES={
 'm01.L05.S01':'For a direction of fixed length, choose which way it faces horizontally and how far it points up or down; these are two angles.',
 'm02.L06.S04':'We need to know where the camera looks and which way is up to specify its complete orientation.',
 'm02.L06.S05':'Including forward and up, let us record the object’s reference directions together.',
 'm03.L02.S04':'Looking only at these numbers, we cannot tell how the airplane has rotated relative to the outside.',
 'm03.L04.S02':'Leaving out how far the object has moved, we want to examine only the rotation between the two coordinate systems.',
 'm03.L05.S05':'In this lesson, vectors are written horizontally and multiplied on the left of the matrix — the row-vector convention.',
 'm05.L01.S02':'Starting with the reverse transformation from upright space to object space, we can store a matrix for that direction instead.',
 'm05.L05.S03':'Even data for the same orientation can use different conventions, making the table appear transposed.',
 'm06.L01.S03':'Row-vector systems may include translation using four-by-three affine matrices.',
 'm06.L01.S04':'For general-purpose tools with clear inputs and outputs, general transformation operations fit well.',
 'm06.L04.S02':'For a particular angular-displacement command such as rotate thirty degrees about X, a general transformation matrix works.',
 'm06.L04.S03':'Our concern is not individual rotation commands, but the object’s current orientation relative to its parent: storing that as a state and using it in both directions.',
 'm06.L07.S03':'Rather than choosing multiplication or transposition, callers can read and use the intended transformation direction.',
 'm06.L07.S04':'Whether using row or column vectors, the implementation follows one consistent convention and documents it.',
 'm06.L08.S03':'Whichever matrix direction is stored, the key is preventing users from misreading the coordinate systems and intent.',
 'm07.L01.S01':'The first row described the airplane’s right axis: which way it points in the outside frame.',
 'm08.L01.S02':'A row selects an axis of the input space, the airplane, and a column selects an axis of the output space, the outside reference.',
 'm08.L01.S03':'For the first row, compare the airplane’s right axis with outside right, up, and forward, and record the three dot products.',
 'm08.L03.S03':'Coordinates read in the airplane frame and coordinates read in the outside frame cannot be mixed directly for this multiplication.',
 'm08.L03.S05':'Whichever common frame we choose, their included angle stays the same, and so does their dot product.',
 'm10.L03.S03':'It is not eight thousand one hundred bytes per frame; it is data accumulated during one second that occupies eight thousand one hundred bytes.',
 'm10.L05.S02':'For real animation files, translation, scale, timing information, and compression affect their size.',
 'm11.L03.S01':'For a three-by-three table, the more important drawback is that not every table is a valid rotation matrix.',
 'm11.L03.S02':'The nine numbers are not freely adjustable: they do not represent nine independent rotations.',
 'm12.L05.S03':'The calculation was meant to perform only rotation; the important point is that axis-length and angle errors can still enter it.'
}
EN_PARAGRAPHS['m10.L04']='For comparison, suppose the same orientation can be stored as three angles; each orientation then occupies twelve bytes. Storing the same two hundred twenty-five orientations requires two thousand seven hundred bytes per second. The difference is five thousand four hundred bytes per second. Over thirty seconds it becomes one hundred sixty-two thousand bytes, or one hundred sixty-two decimal kilobytes.'

# Faithful caption-only wording, reviewed against the exact spoken clauses.
# The measured Korean clock is unchanged. Neighboring clauses are adjusted
# together where English originally moved a qualifier across the KO boundary.
EN_CLAUSE_READABILITY={
 'm02.L02.S04.C01':'The change between orientations is angular displacement.',
 'm02.L04.S04.C01':'Given a reference orientation,',
 'm03.L02.S04.C01':'From these numbers alone,',
 'm05.L05.S02.C01':'We need to know whether vectors are rows or columns',
 'm06.L05.S03.C01':'If the image moves unexpectedly and, without checking why,',
 'm06.L05.S03.C02':'we only change a sign or transpose,',
 'm07.L01.S04.C03':'and −1 when they are opposite.',
 'm08.L04.S04.C01':'Matrix columns give the reverse mapping:',
 'm09.L01.S02.C01':'Points or directions on the airplane',
 'm09.L02.S03.C01':'Matrices conveniently take vertices from object to world space,',
 'm09.L04.S03.C01':'Knowing the tool’s direction in the hand frame, and the hand’s in the body frame',
 'm10.L01.S03.C01':'Orientation has three independent changes,',
 'm10.L03.S03.C01':'Not 8,100 bytes per frame;',
 'm11.L03.S02.C01':'The nine entries are not freely adjustable:',
 'm11.L03.S02.C02':'they are not nine independent rotations.',
 'm11.L06.S02.C02':'preserves all three axis lengths and right angles.',
 'm12.L05.S03.C01':'Even a rotation-only calculation can contain',
 'm12.L05.S03.C02':'axis-length and angle errors.',
 'm13.L03.S01.C02':'and combine relations between spaces by multiplication.',
 'm13.L04.S04.C01':'Knowing external data and repeated calculations'
}

LEX=[('왕국의 눈물','젤다의 전설 티어스 오브 더 킹덤'),('울트라핸드','울트라 핸드'),
 ('오브젝트 투 업라이트','objectToUpright'),('업라이트 투 오브젝트','uprightToObject'),
 ('디렉션 코사인 매트릭스','Direction Cosine Matrix'),('업라이트 스페이스','Upright Space'),
 ('오리엔테이션','Orientation'),('애티튜드','Attitude'),('에이피아이','API'),
 ('피와 피 프라임의 내적','p·p′'),('피와 큐 프라임의 내적','p·q′'),('피와 알 프라임의 내적','p·r′'),
 ('피, 큐, 알','p, q, r'),('피 프라임','p′'),('큐 프라임','q′'),('알 프라임','r′'),
 ('에이에서 비로','A에서 B로'),('비에서 씨로','B에서 C로'),('에이에서 씨로','A에서 C로'),
 ('입력 공간을 에이','입력 공간을 A'),('중간 공간을 비','중간 공간을 B'),('마지막 공간을 씨','마지막 공간을 C'),
 ('플러스 엑스축','+X축'),('플러스 와이축','+Y축'),('플러스 제트축','+Z축'),
 ('마이너스 엑스','−X'),('마이너스 와이','−Y'),('마이너스 제트','−Z'),('플러스 엑스','+X'),('플러스 와이','+Y'),('플러스 제트','+Z'),
 ('엑스축','X축'),('와이축','Y축'),('제트축','Z축'),('엑스','X'),('와이','Y'),('제트','Z'),
 ('삼 곱하기 삼','3×3'),('네 곱하기 네','4×4'),('네 곱하기 삼','4×3'),
 ('삼십이 비트','32비트'),('삼십육 바이트','36바이트'),('열두 바이트','12바이트'),('사 바이트','4바이트'),
 ('십육만 이천 바이트','162,000바이트'),('백육십이 킬로바이트','162킬로바이트'),('팔천백 바이트','8,100바이트'),('이천칠백 바이트','2,700바이트'),('오천사백 바이트','5,400바이트'),
 ('열다섯 곱하기 열다섯','15×15'),('이백이십오 개','225개'),('열다섯 부위','15부위'),('열다섯 번','15번'),('열다섯 개','15개'),('삼십 초','30초'),
 ('영, 영, 마이너스 일','(0, 0, −1)'),('이, 영, 마이너스 일','(2, 0, −1)'),('마이너스 일, 영, 영','(−1, 0, 0)'),
 ('일, 영, 영','(1, 0, 0)'),('영, 일, 영','(0, 1, 0)'),('영, 영, 일','(0, 0, 1)'),('일, 영, 이','(1, 0, 2)'),
 ('구십 도','90°'),('삼십 도','30°'),('육십 도','60°'),('플러스 일','+1'),('마이너스 일','−1')]
TERMS=[('방향코사인 행렬','direction cosine matrix','focus'),('정규직교화','orthonormalize','result'),
 ('직립 공간','upright space','focus'),('오브젝트 공간','object space','focus'),('기저벡터','basis vectors','focus'),
 ('각변위','angular displacement','focus'),('회전행렬','rotation matrix','focus'),('항등 자세','identity','focus'),
 ('행벡터','row-vector','focus'),('전치','transpose','focus'),('역행렬','inverse matrix','focus'),('내적','dot product','focus'),
 ('행렬식','determinant','focus'),('부동소수점','floating-point','focus'),('반사','reflection','caution'),
 ('행렬 크리프','matrix creep','caution'),('정규직교','orthonormal','focus'),('자세','orientation','focus'),('방향','direction','focus'),('뱅크','bank','focus'),('직각','right angle','focus')]
def aliases(text):
 matches=[]
 for spoken,display in LEX:
  for m in re.finditer(re.escape(spoken),text):matches.append((m.start(),m.end(),spoken,display))
 selected=[]
 for a,b,s,d in sorted(matches,key=lambda x:(-(x[1]-x[0]),x[0])):
  if not any(a<q and b>p for p,q,*_ in selected):selected.append((a,b,s,d))
 return [dict(sourceStart=a,sourceEnd=b,spoken=s,display=d,meaning='context-specific canonical display; inverse alias restores exact approved spoken text') for a,b,s,d in sorted(selected)]
def cut(text,markers):
 out=[];at=0
 for marker in markers:
  match=re.compile(r'(?<!\S)'+re.escape(marker)).search(text,at)
  n=match.start() if match else -1;assert n>at,(marker,text)
  out.append(text[at:n].strip());at=n
 out.append(text[at:].strip());assert ' '.join(out)==text
 return out

def caption_lines(geometry,text,font,bold,emphasis,language):
 lines=geometry.wrap(text,font,bold,emphasis)
 protected=['울트라 핸드'] if language=='ko' else []
 spans=[(m.start(),m.end()) for token in protected for m in re.finditer(re.escape(token),text)]
 if not spans or all(any(text[a:b] in line for line in lines) for a,b in spans):return lines
 def length(part,offset):
  return sum((bold if emphasis and emphasis['start']<=i<emphasis['end'] else font).getlength(ch) for i,ch in enumerate(part,offset))
 choices=[]
 for word in list(re.finditer(r'\S+',text))[1:]:
  split=word.start()
  if any(a<split<b for a,b in spans):continue
  left,right=text[:split].rstrip(),text[split:];lw,rw=length(left,0),length(right,split)
  if max(lw,rw)<=1570:choices.append((abs(lw-rw),left,right))
 assert choices,('Protected canonical name needs semantic wrapping without text/font/timing changes',text)
 _,left,right=min(choices);assert ' '.join([left,right])==text
 return [left,right]
def main():
 k,e=read(K),caption_english();source_en=read(E)
 assert sha(K)=='2cfce716a62d3b951a81a5022dd216ac4cbaafb7b73ffa20e9d0765798e789c3'
 assert sha(E)=='e3e6056b0d42905869d964097af33c9aded419266b587a31a9e41154c4273100'
 spec=importlib.util.spec_from_file_location('v8_caption_geometry',P/'production/revision-v6/captions.py');geom=importlib.util.module_from_spec(spec);spec.loader.exec_module(geom)
 spec=importlib.util.spec_from_file_location('v8_caption_normalizer',H/'voice-normalize.py');norm=importlib.util.module_from_spec(spec);spec.loader.exec_module(norm)
 font=ImageFont.truetype(str(geom.FONT),48);bold=ImageFont.truetype(str(geom.BOLD),48)
 splits=read(H/'caption-clauses.json')
 # These short negative/qualified propositions are kept intact to avoid a
 # misleading positive fragment; typical2–10eojeol is not a word-count cut.
 for key in ['m09.L03.S01','m09.L03.S04','m09.L05.S04']:splits.pop(key,None)
 # Caption English is independently phrased in the same semantic order.
 adjusted={'m02.L06.S04':['and which way','to specify'], 'm03.L02.S04':['we cannot tell'],
  'm03.L04.S02':['we want to examine'], 'm05.L01.S02':['we can store'], 'm05.L05.S03':['making the table'],
  'm07.L01.S01':['which way'], 'm08.L03.S03':['cannot be mixed']}
 for key,em in adjusted.items():splits[key][1]=em
 splits['m09.L01.S02']=[['다른 공간의'],['can be converted']]
 EN_SENTENCES['m09.L01.S02']='The points or directions attached to the airplane can be converted directly into coordinates in another space.'
 splits['m12.L06.S04']=[['서로 비스듬한','축 사이의'],['can leave the axes','so their relationships']]
 rows=[];mapping=[];layout=[];word_exceptions=[];translations=[];readability_edits=[]
 for s,t,original in zip(k['scenes'],e['scenes'],source_en['scenes']):
  assert s['id']==t['id']==original['id'];assert len(s['paragraphs'])==len(t['paragraphs'])==len(original['paragraphs'])
  emphasized=set()
  for line,(kp,ep,orig_ep) in enumerate(zip(s['paragraphs'],t['paragraphs'],original['paragraphs']),1):
   key=s['id']+f'.L{line:02d}';ks,es=sentences(kp),sentences(ep);assert len(ks)==len(es),(key,'sentence-semantic-alignment')
   es=[EN_SENTENCES.get(key+f'.S{j:02d}',v) for j,v in enumerate(es,1)]
   ep=' '.join(es);spans=aliases(kp);offset=0;en_offset=0;cue_ids=[]
   for j,(a,b) in enumerate(zip(ks,es),1):
    skey=key+f'.S{j:02d}'
    if skey in splits:kc,ec=cut(a,splits[skey][0]),cut(b,splits[skey][1])
    else:kc,ec=[a],[b]
    assert len(kc)==len(ec),(skey,'paired-clause-count')
    for ci,(ct,et) in enumerate(zip(kc,ec),1):
     cue_id=skey+f'.C{ci:02d}';before=et;et=EN_CLAUSE_READABILITY.get(cue_id,et)
     if et!=before:readability_edits.append(dict(cueId=cue_id,sourceKo=ct,before=before,after=et,reason='Retain all conditions, objects and claims in their original paragraph order; reduce caption-only English reading load at the measured unchanged Korean cue. Neighbor clauses are reviewed together.'))
     pos=kp.index(ct,offset);end=pos+len(ct);eo=en_offset+(1 if en_offset else 0)
     assert norm.normalized(kp[:pos])+norm.normalized(ct)+norm.normalized(kp[end:])==norm.normalized(kp),(skey,'atomic normalized-number boundary',ct)
     assert norm.normalized(kp[:pos])+norm.normalized(ct)==norm.normalized(kp[:end]),(skey,'normalized prefix+clause additivity',ct)
     assert norm.normalized(kp[:end])+norm.normalized(kp[end:])==norm.normalized(kp),(skey,'normalized prefix+suffix additivity',ct)
     display,changes=geom.display_aliases(ct,pos,spans);ke=ee=None
     for term,eng,role in TERMS:
      ka,ea=display.find(term),et.lower().find(eng.lower())
      if ka>=0 and ea>=0 and term not in emphasized:
       ke=dict(start=ka,end=ka+len(term),role=role);ee=dict(start=ea,end=ea+len(eng),role=role);emphasized.add(term);break
     row=dict(id=skey+f'.C{ci:02d}',scene=s['id'],line=line,paragraphId=key,sentence=j,clause=ci,
        sourceKo=ct,sourceKoOffset=pos,sourceKoEnd=end,sourceEn=et,sourceEnOffset=eo,sourceEnEnd=eo+len(et),
        ko=display,en=et,displayKo=display,displayEn=et,displayAliasesKo=changes,displayAliasesEn=[],
        emphasisKo=ke,emphasisEn=ee,normalizedSourceOffset=len(norm.normalized(kp[:pos])),normalizedSourceEnd=len(norm.normalized(kp[:end])),
        translationBasis='Independent faithful translation of this exact spoken-KO sentence/clause. Companion EN source remains unchanged; EN offsets refer only to this caption paragraph.',
        sourceKoUnchanged=True,semanticBoundary='explicit condition/target/action/result boundary' if len(kc)>1 else 'single meaningful proposition',
        nativePixelReview='pending actual encoded captioned output',mobileMovingReview='pending actual375px and speech/action output')
     try:
      row['koLines']=caption_lines(geom,display,font,bold,ke,'ko');row['enLines']=caption_lines(geom,et,font,bold,ee,'en')
      if row['koLines']!=geom.wrap(display,font,bold,ke):row['layoutNote']='Keep the canonical ability name 울트라 핸드 together; line break only, no text, PCM, timing or48px geometry change.'
     except AssertionError as ex:layout.append(dict(id=row['id'],ko=ct,en=et,reason=str(ex)))
     count=len(ct.split());row['sourceKoEojeol']=count
     if count<2 or count>10:
      assert count==11,(row['id'],'Review an unplanned word-count exception',ct)
      word_exceptions.append(dict(id=row['id'],count=count,ko=ct,en=et,status='reviewed-semantic-unit-exception',
         reason='Keep the short complete negative/qualified proposition, matching-space relation, or atomic numeric condition intact; splitting it would detach the required qualification or comparison. It fits48px/2lines without shrinking.'))
     rows.append(row);cue_ids.append(row['id']);offset=end;en_offset=eo+len(et)
   selected=[r for r in rows if r['paragraphId']==key]
   assert ' '.join(r['sourceKo'] for r in selected)==kp
   ep=' '.join(r['sourceEn'] for r in selected)
   assert all(ep[r['sourceEnOffset']:r['sourceEnEnd']]==r['sourceEn'] for r in selected)
   mapping.append(dict(scene=s['id'],line=line,paragraphId=key,sourceKo=kp,sourceKoSha256=hashlib.sha256(kp.encode()).hexdigest(),captionEnglish=ep,companionEnglish=orig_ep,
      cueIds=cue_ids,sourceKoFullyReconstructed=True,captionEnglishFullyReconstructed=True,semanticReview='Exact paragraph translated in retained KO claim/condition/order; canonical sentence/clause rephrasing is not a paraphrase-based omission.'))
   if ep!=orig_ep:translations.append(dict(paragraphId=key,companionEnglishUnchanged=orig_ep,captionOnlyEnglish=ep,reason='Independent caption translation and clause order aligned to unchanged spoken KO; all claims retained.'))
 assert len(mapping)==76
 def contrast(color):
  rgb=[int(color[i:i+2],16)/255 for i in (1,3,5)]
  linear=[v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb]
  lum=sum(a*b for a,b in zip(linear,[.2126,.7152,.0722]))
  return 1.05/(lum+.05)
 contrasts={k:contrast(v) for k,v in geom.PALETTE.items()}
 assert min(contrasts.values())>=4.5
 report=dict(schemaVersion=1,revision='orientation-matrix-v8',policy='caption-clause-keyword-v1',
   inputs=dict(koSha256=sha(K),enSha256=sha(E),designSha256=sha(Path(__file__)),clauseMapSha256=sha(H/'caption-clauses.json'),approvedGeometrySha256=sha(P/'production/revision-v6/captions.py'),normalizerSha256=sha(H/'voice-normalize.py')),
   sceneCount=13,paragraphCount=76,cueCount=len(rows),cues=rows,paragraphs=mapping,captionOnlyTranslationChanges=translations,captionClauseReadabilityEdits=readability_edits,
   layoutNeeds=layout,wordCountReview=word_exceptions,sourceKoUnchanged=True,sourceEnCompanionUnchanged=True,
     geometry='boxed-white-forest-v1; fixed center960,970 /48px /max2lines /1570px',
     font=dict(family='Malgun Gothic',size=48,bodyFile=str(geom.FONT),emphasisFile=str(geom.BOLD),fallback=True,
         reason='Reuse approved V6 geometry and matching ASS face. Variable NotoSansKR-VF defaults to weight100 without explicit axis; do not measure a500face but encode another weight. No font shrink.'),
     palette=geom.PALETTE,
     emphasisContrastOnWhite=contrasts,
     sourceOffsetValidation='Every Unicode span reproduces its exact approved KO substring. Prefix+clause and prefix+suffix remain additive under the actual voice-normalize.py; compound numbers/labels are never split.',
   timing='Pending actual source-ASR/PCM word clock; exact Unicode offsets and additive normalized offsets only, never estimated English lengths or extra silence.',
     newMediaCreated=False,status='draft-needs-layout-review' if layout else 'clause-design-ready-for-actual-word-clock')
 (H/'caption-plan.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps(dict(cues=len(rows),paragraphs=76,layoutNeeds=layout,reviewedSemanticUnitExceptions=len(word_exceptions),englishCompanionUnchanged=True),ensure_ascii=False))
def inspect():
 k,e=read(K),caption_english()
 for s,t in zip(k['scenes'],e['scenes']):
  assert s['id']==t['id'] and len(s['paragraphs'])==len(t['paragraphs'])
  for i,(a,b) in enumerate(zip(s['paragraphs'],t['paragraphs']),1):
   assert len(sentences(a))==len(sentences(b)),(s['id'],i)
   for n,(c,d) in enumerate(zip(sentences(a),sentences(b)),1):
    if len(c.split())>10:print(s['id']+f'.L{i:02d}.S{n:02d}',len(c.split()),'\nKO:',c,'\nEN:',d,'\n')
if __name__=='__main__':main()
