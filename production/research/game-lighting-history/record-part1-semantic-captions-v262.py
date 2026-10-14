"""Seal direct bilingual paragraph comparison separately from encoded pixel approval."""
from pathlib import Path
from datetime import datetime,timezone
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[3];P=ROOT/'projects/game-lighting-history-04/production'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PP=P/'part1-final-input-plan-v240.json';LP=P/'part1-caption-layout-v243.json';plan=read(PP);layout=read(LP)
assert layout['planSha256']==sha(PP) and layout['allTextPreserved'] and layout['cueCount']==335
ordered=sorted(plan['paragraphs'],key=lambda p:min(q['fromFrame'] for q in p['koCues']))
assert len(ordered)==77 and layout['maximumLines']==2 and layout['center']==[960,970]
for track in layout['tracks']:
 assert sha(ROOT/track['path'])==track['sha256'] and track['all77ParagraphTextsPreserved']
assert [t['cueCount'] for t in layout['tracks']]==[335,409]
assert next(t for t in layout['tracks'] if t['language']=='en')['englishTimingsMeasured'] is False
def srt_rows(path):
 rows=[]
 def sec(value):
  h,n,s,ms=re.split('[:,]',value);return int(h)*3600+int(n)*60+int(s)+int(ms)/1000
 for block in path.read_text('utf-8-sig').strip().split('\n\n'):
  lines=block.splitlines();a,b=lines[1].split(' --> ')
  rows.append({'id':int(lines[0]),'start':sec(a),'end':sec(b),'text':''.join(lines[2:])})
 return rows
tracks={t['language']:srt_rows(ROOT/t['path']) for t in layout['tracks']}
compact=lambda s:re.sub(r'\s+','',s)
records=[{'id':p['id'],'ko':p['ko'],'en':p['en'],
 'literalTextPairSha256':hashlib.sha256(json.dumps([p['ko'],p['en']],ensure_ascii=False).encode()).hexdigest(),
 'bothCompleteParagraphsDirectlyRead':True,'claimsExamplesConditionsAndConclusionAligned':True,
 'fromFrame':min(q['fromFrame'] for q in p['koCues']),'toFrame':max(q['toFrame'] for q in p['koCues'])} for p in ordered]
for p,row in zip(ordered,records):
 ids={lang:[q['id'] for q in p[lang+'Cues']] for lang in ['ko','en']}
 a=tracks['ko'][ids['ko'][0]-1]['start'];b=tracks['ko'][ids['ko'][-1]-1]['end']
 for lang in ['ko','en']:
  selected=[tracks[lang][i-1] for i in ids[lang]]
  assert compact(''.join(c['text'] for c in selected))==compact(p[lang]),p['id']
  assert abs(selected[0]['start']-a)<=.002 and abs(selected[-1]['end']-b)<=.002,p['id']
 row.update(start=a,end=b,koCues=ids['ko'],enCues=ids['en'],directlyReadBothFullTexts=True)
for lang in ['ko','en']:
 assert [i for p in records for i in p[lang+'Cues']]==list(range(1,len(tracks[lang])+1))
record={'reviewedAt':datetime.now(timezone.utc).isoformat(),'planSha256':sha(PP),'layoutSha256':sha(LP),'paragraphs':records,'approved':True,
 'status':'approved-semantic-paragraph-alignment','manualSemanticReview':True,'allParagraphTextsRetained':True,
 'captions':[{'language':t['language'],'path':t['path'],'sha256':t['sha256'],'cues':t['cueCount']} for t in layout['tracks']],
 'scope':'Directly reread all77 complete independent KO/EN paragraphs in chronological order. This approves semantic correspondence, not final burned pixels or spoken pronunciation.',
 'numericChecks':['16 illustrative shadow cells and5 resident cells are not game measurements.','8x4=32;4x2=8;one-quarter internal pixels does not imply one-quarter frame time.','UV0,0 /1,0 /0,1 and weights0.5,0.25,0.25 produce0.25,0.25 under equal perspective denominators.'],
 'conditionChecks':['Virtual shadow depth, virtual surface-texture data and ordinary texture pools are distinct.','Horizon detail reconstruction, Outer displayed frames, Cyberpunk lighting reconstruction and Fortnite diagnostics answer different questions.','Cyberpunk source combines processing stages; FPS is not an isolated ray-reconstruction gain.','2014 Rivalry is an engine demonstration, not a fifth game or proof of a later mobile-deferred implementation.','Unavailable compiler statistics are missing measurements, not a low shader cost.'],
 'koCueCount':335,'enCueCount':409,'allOriginalAndAddedParagraphsPreserved':True,'englishAudioPresent':False,'englishTimingsMeasured':False,
 'englishTimingMethod':'Independent English captions use the corresponding measured Korean paragraph intervals; no English audio timing is claimed.',
 'allEncodedPixelsReviewed':False,'finalMixedAsrApproved':False,'qaApproved':False,'uploaded':False,'humanWholeListening':'pending','humanPronunciation':'pending','newGitImages':0}
(P/'part1-semantic-caption-review-v262.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf8')
print(json.dumps({'semanticParagraphsReviewed':77,'koCues':335,'enCues':409,'encodedPixelsApproved':False}))
