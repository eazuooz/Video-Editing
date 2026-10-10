"""Current source choices after direct play and finer source-frame comparison."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
d=read(B/'quaternion-source-corrections-v5.json');by={s['id']:s for s in d['scenes']}
by['GA06']['selectionReason']='Use clear302–317, excluding the crash at300. Visible skier becomes a bicycle around312; hide geometry during equipment change. The next body/wheel example begins317.'
by['GA04']['selectionReason']='Bicycle wheels, not skis, are visible317–350. New-only V6 narration identifies torso and visible wheel directions; preserve all baseline material and V4/V5 takes.'
by['GA05']={'id':'GA05','sourceId':'4Odvp_TIeQU','intervals':[[147,159],[169.25,187],[372,394]],'segmentSourceIds':['4Odvp_TIeQU','4Odvp_TIeQU','_dw9jjRpanA'],'sourceGroupStartsAtLines':[0,1,3],'maximumSeconds':51.75,'selectionReason':'AG51.75s played natively to ended=true in the review player. The unused gaps147–159 and169.25–187 show jumps, orientation change and landing; the separate372–394 ski excerpt shows a clear jump/landing and downhill state. Reject broad I350–405 due crash/get-up gray screens354–370 and395–401. Make the source switches explicit; never imply one cut is the before/after of another.'}
d['scenes']=list(by.values());d['comparison']=[x for x in d['comparison'] if x.get('id') not in ['I-fine','AG','NCG-credit-required']]+[
 {'id':'I-fine','interval':[350,405],'chosen':False,'reason':'Source pages reveal crash/backtrack/get-up gray screens354–370 and395–401. Initial broad playback cannot approve the whole interval; preserve earlier record with this correction.'},
 {'id':'AG','intervals':[[147,159],[169.25,187],[372,394]],'nativeEnded':True,'nativeEndTime':51.75,'chosen':True,'beforeActionAfter':'ski approach → airborne turn → landing/downhill within each excerpt','cameraOcclusionUi':'Following camera moves; silver costume effect does not reveal game-world coordinates. Hide lines under tree foliage; exclude get-up UI. Explicit source switch label separates the two recordings.','reason':'Fewer interruptions and visible independent torso/ski directions teach endpoint versus time history more clearly than broad I.'},
 {'id':'NCG-credit-required','sourceIds':['dg9W4Ofta_E','W1UOGkmKd1g'],'chosen':False,'reason':'Publisher requires a public description credit. Current channel instruction omits public credits; keep the existing internally documented sources rather than using this conditional permission.'}
];d['finalNarrationPixelApproval']=False;write(B/'quaternion-source-corrections-v5.json',d)
m=read(B/'quaternion-on-footage-math.json')
for note in m['labels']:
 if note['scene']=='GA04':note['line']=5
write(B/'quaternion-on-footage-math.json',m)
print('Current source correction and V6 annotation cue recorded; full pixels pending')
