"""Freeze paired text only. Does not generate voice, access a service or write media."""
from pathlib import Path
import json, hashlib, copy
HERE=Path(__file__).resolve().parent
def read(p): return json.loads(p.read_text('utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,d): (HERE/name).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n','utf-8')
ko=read(HERE/'narration.ko.json'); en=read(HERE/'narration.en.json')
assert [(s['id'],len(s['lines'])) for s in ko['scenes']]==[(s['id'],len(s['lines'])) for s in en['scenes']]
aliases={'뿌요뿌요 테트리스 2':'뿌요뿌요 테트리스 투'}
spoken=copy.deepcopy(ko);spoken['language']='spoken-ko'
for s in spoken['scenes']:
 for i,line in enumerate(s['lines']):
  for a,b in aliases.items():line=line.replace(a,b)
  s['lines'][i]=line
save('narration.spoken-ko.json',spoken);save('caption-aliases.json',aliases)
text='\n\n'.join(line for s in spoken['scenes'] for line in s['lines'])+'\n'
(HERE/'narration.spoken-ko.txt').write_text(text,'utf-8')
save('script-readthrough.json',{
 'revision':'clarity-v3','date':'2026-10-29','status':'tts-ready-text-only',
 'wholeKoEnReadWithoutHeadings':True,'pairedParagraphCount':26,
 'claimOrderRetained':['puzzle color clue','theme/background combinations','color-vision simulation','lightness/background/pattern repairs','Mario object/action examples','grayscale visual hierarchy','flip analogy and player testing','color plus redundant clues'],
 'concreteCorrection':{'paragraph':'05-p02','removed':'touch as a necessary trigger for every flower','reason':'Directly inspected wonder-block event board shows a talking flower responding near the player; interaction wording now says approach.'},
 'necessaryConditionsRetained':['grayscale is a light/dark inspection, not exact color-vision simulation','pieces and background must both remain distinguishable','two authored same-shaped tokens are illustrative, not a claim that real Puyos lack shape clues'],
 'redundantHedgesRemoved':[],'referenceCreatorFraming':False,'headingOrCoachingTts':False,
 'files':{n:sha(HERE/n) for n in ['narration.ko.json','narration.en.json','narration.spoken-ko.json','narration.spoken-ko.txt']},
 'voiceRequest':{'provider':'ElevenLabs','voiceId':'jIRSnF8OWAsWEChVwCuK','approvedSample':'B','textFile':str(HERE/'narration.spoken-ko.txt'),'textSha256':sha(HERE/'narration.spoken-ko.txt'),'characterCount':len(text),'modelAndSettings':'Parent verified UI v4, stability .5, similarity .75; generation not performed by this script.'},
 'timing':'Unmeasured. No guessed subtitle timing. Preserve generated speech PCM after integrity/complete-text review.',
 'humanListening':'not performed','nativeVisualReview':'pending'
})
print(json.dumps({'text':str(HERE/'narration.spoken-ko.txt'),'sha256':sha(HERE/'narration.spoken-ko.txt'),'characters':len(text)},ensure_ascii=False))
