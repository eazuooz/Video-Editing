"""One evidenced menu-direction correction, preserving the other 76 paragraphs."""
from pathlib import Path
from datetime import datetime, timezone
import json, hashlib, copy, psutil, subprocess, math
from PIL import ImageFont
R=Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-04/production'
rd=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rel=lambda p:p.relative_to(R).as_posix()
stamp=lambda:datetime.now(timezone.utc).isoformat()
ex=rd(P/'part1-vt-direction-take-asr-execution-v308.json')
assert ex['status']=='complete' and ex['exitCode']==0
w=ex['worker'];assert not psutil.pid_exists(w['pid']) or abs(psutil.Process(w['pid']).create_time()-w['createTime'])>.01
tts=rd(P/'part1-vt-direction-retry-tts-execution-v307.json');take=tts['results'][0]
assert tts['exitCode']==0 and take['technicalTailGatePassed'] and sha(R/take['path'])==take['sha256']
ko=rd(R/'projects/game-lighting-history-04/script/physical-part1-vt-direction.ko.v305.json')['scenes'][0]['lines'][0]
en=rd(R/'projects/game-lighting-history-04/script/physical-part1-vt-direction.en.v305.json')['scenes'][0]['lines'][0]
results=[]
for row in ex['results']:
 assert sha(R/row['path'])==row['sha256']
 d=rd(R/row['path']);assert not d['expectedTextUsedAsPrompt']
 results.append(dict(row, fullText=d['text'], fullTextDirectlyCompared=True, allWordEndingsAndTimestampsDirectlyCompared=True))
selection=dict(reviewedAt=stamp(),selectedForPrivateTechnicalProduction=True,selectedTake=take,ko=ko,en=en,
 rawAndCompleteContext=results,actualObservation='Raw and complete three-paragraph context retain the whole corrected direction, affected texture/material list and reader-input qualification. Raw words 0.00-15.00: 변환/읽습니다, 일반→가상/바꿉니다, 이어서/나옵니다, 자산/입력도/보세요. Complete context 26.08-41.04 repeats the same new paragraph once; previous UV-stack and following tile/border paragraphs remain complete. Here context punctuation differences and 여기에/여기의 recognition are preserved as lexical recognition differences; no missing or unsolicited farewell content. Technical tail passes independently, never used as content approval.',
 historicalError={'boards':[93,94,95],'direction':'old narration virtual→ordinary contradicted actual Convert to Virtual Texture; dependent-list cue preceded its visible dialog'},
 sourceReview={'tabId':'77','reviewPage':'production/research/game-lighting-history/local/part1-vt-conversion-review-v306.html','normalPlaybackRate':1,'fullCandidateActuallyPlayed':True,'candidateSeconds':[207,223.1666667],'directNativePixels':['211s Convert to Virtual Texture menu visible','214s menu has closed, asset browser','217s Convert To VT Textures dialog with textures/materials list'],'selectedInFrame':12450,'selectedOutFrame':13420,'selectedSeconds':[207.5,223.6666667],'reason':'Move the cut5.5s later: direction narration2.86-5.76s occurs over conversion menu; affected assets6.20-9.38s leads into the dialog at approximately214.3s. Loading tail around228s excluded.'},
 finalMixedAsrApproved=False,allFinalPixelsReviewed=False,humanWholeListening='pending',humanPronunciation='pending',newGitImages=0)
sp=P/'part1-vt-direction-direct-review-v309.json';assert not sp.exists();sp.write_text(json.dumps(selection,ensure_ascii=False,indent=2)+'\n','utf8')
oldp=P/'part1-final-input-plan-v288.json';old=rd(oldp);new=copy.deepcopy(old)
row=next(x for x in new['paragraphs'] if x['id']==take['id']);row.update(ko=ko,en=en,pcm={k:take[k] for k in ['path','sha256','sampleRate','samples']})
texts={'ko':['변환 메뉴에서는 이름의 방향부터 읽습니다.','여기서는 일반 텍스처를 가상 텍스처로 바꿉니다.','이어서 영향을 받는 텍스처와 머티리얼이 함께 나옵니다.','자산 하나의 표시만 바꾸는 일이 아니라, 그\n자산을 읽는 입력도 맞아야 한다는 점을 보세요.'],
 'en':['Read the conversion direction\nin the menu:','ordinary textures are being\nconverted to virtual textures.','Next, the dialog lists affected\ntextures and materials.','The asset and the shader inputs\nthat read it must agree.']}
times=[(0,165),(172,355),(372,573),(582,914)];words=[(0,4),(5,10),(11,17),(18,31)]
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
chars=0
for lang in ['ko','en']:
 for i,c in enumerate(row[lang+'Cues']):
  c.update(text=texts[lang][i],fromFrame=23085+times[i][0],toFrame=23085+times[i][1])
  if lang=='ko':
   widths=[font.getlength(t) for t in c['text'].split('\n')];assert len(widths)<=2 and max(widths)+44<=1340
   c.update(lineWidths=widths,boxWidth=math.ceil(max(widths)+44),timingDirectlyReviewed=True,pixelsReviewed=False,wordAnchorEvidence='v308 raw whole words0-31 and complete three-paragraph context directly compared',recognizerWordIndices=list(words[i]),sourceCharacters=[chars,chars+len(c['text'].replace('\n',' '))])
   c['from']=times[i][0]/60;c['to']=times[i][1]/60;chars+=len(c['text'].replace('\n',' '))+1
  else:c.update(koSentenceIndices=[i],enSentenceIndices=[0 if i<2 else i-1],timingMethod='Direct semantic comparison against corrected KO whole word anchors; English reading splits, not English ASR')
  index=next(k for k,x in enumerate(new[lang+'Cues']) if x['id']==c['id']);new[lang+'Cues'][index]=copy.deepcopy(c)
cut=next(x for x in new['cuts'] if x.get('paragraphId')==take['id']);cut.update(pcm={**row['pcm'],'firstSample':0,'exclusiveEndSample':take['samples']},proposedCuts=[{'inFrame':12450,'outFrame':13420}],preserveFullPcm=True)
assert len([1 for a,b in zip(old['paragraphs'],new['paragraphs']) if a==b])==76
assert len([1 for a,b in zip(old['cuts'],new['cuts']) if a==b])==93
for k in ['actualFrames','explanationFrames','bodyFrames','finalFrames','ratioErrorFrames','chapterRanges','branding','membership']:assert new[k]==old[k]
new.update(preparedAt=stamp(),vtDirectionCorrection={'directReview':{'path':rel(sp),'sha256':sha(sp)},'oldPlan':{'path':rel(oldp),'sha256':sha(oldp)},'changedParagraph':take['id'],'changedFrameRange':[23085,24055],'allOther76ParagraphsUnchanged':True,'allOther93CutsUnchanged':True,'allOriginal36PcmUnchanged':True,'retainedSlotFrames':970,'newPcmSeconds':15.44,'naturalTailFrames':43.6},allFinalPixelsReviewed=False,finalMixedAsrApproved=False)
new['bindings'].append({'path':rel(sp),'sha256':sha(sp)})
dest=P/'part1-final-input-plan-v309.json';assert not dest.exists();dest.write_text(json.dumps(new,ensure_ascii=False,indent=2)+'\n','utf8')
cs=R/'production/research/game-lighting-history/prepare-part1-captions-v309.py';assert not cs.exists()
cs.write_text((R/'production/research/game-lighting-history/prepare-part1-captions-v288.py').read_text('utf8').replace('input-plan-v288','input-plan-v309').replace('part1-captions-v288','part1-captions-v309').replace('caption-layout-v288','caption-layout-v309'),'utf8')
subprocess.run([__import__('sys').executable,'-X','utf8',str(cs)],cwd=R,check=True)
print(json.dumps({'plan':rel(dest),'sha256':sha(dest),'unchangedParagraphs':76,'newPcmSeconds':15.44,'wholeRuntimeFrames':new['finalFrames'],'finalApproval':False}))
