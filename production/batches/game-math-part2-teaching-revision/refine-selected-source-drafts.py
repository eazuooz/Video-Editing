"""Apply fine-frame findings without changing any original script/audio."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
p=B/'quaternion-source-corrections-v5.json';d=read(p)
x=next(s for s in d['scenes'] if s['id']=='GA05')
x.update(intervals=[[147,159],[169.25,179.1],[180.1,187],[372,394]],segmentSourceIds=['4Odvp_TIeQU']*3+['_dw9jjRpanA'],sourceGroupStartsAtLines=[0,1,None,3],maximumSeconds=50.75)
x['selectionReason']+=' Fine-frame correction: source contact page3 shows get-up179.1–180.1; exclude it and label the discontinuous excerpt. Both remaining portions in this narrated group are independent visible actions.'
if not any(s['id']=='GA05old-fine' for s in d['comparison']):d['comparison'].append({'id':'GA05old-fine','interval':[169.25,187],'chosen':False,'reason':'Broad native AG playback had a brief gray get-up179.1–180.1, exposed by half-second pages. Exclude these frames; record this as a correction, not a whole-window approval.'})
write(p,d)
# Extend observed traces to the clear late portions, retaining hidden intervals.
updates={
'gb03-landmarks.json':(573,[(300,150,300,236),(295,151,309,255),(296,129,293,222),(298,156,314,231),(299,160,306,243),(283,172,322,275),(283,189,319,273),(290,184,327,278),(285,168,286,253),(285,158,269,228),(287,190,278,287),(308,207,263,263),(310,161,299,222),(300,193,275,269),(307,193,290,285),(300,166,290,215),(283,187,283,259),(295,206,260,255),(291,155,298,227),(301,155,303,219),(294,182,281,248),(296,160,278,233)]),
'gb04-landmarks.json':(668,[(294,165,272,238),(292,149,294,228),(293,189,243,262),(280,192,226,279),(292,155,273,228),(290,165,281,239),(294,190,270,265),(290,191,246,267),(290,193,318,265),(303,160,320,230),(286,193,297,259),(294,208,305,280),(292,184,283,280),(299,169,292,260),(277,186,307,206),(291,192,291,270),(294,161,310,249),(294,155,297,231),(299,193,261,277),(312,164,262,240),(284,188,314,258),(288,180,289,270),(290,198,250,283),(286,166,283,244),(284,196,291,292),(292,182,267,255),(274,270,297,216),(250,207,230,295),(285,263,281,218),(260,207,244,270),(292,180,313,267),(291,173,305,246),(291,170,289,242)]),
'ga05new-landmarks.json':(380.5,[(293,226,307,319),(292,182,290,258),(313,212,307,284),(304,156,299,242),(300,198,273,277),(308,187,303,256),(308,192,306,281),(309,201,301,282),(306,181,275,258),(317,184,287,269),(307,182,279,253),(304,180,279,257),(310,150,285,248),(311,175,266,229),(304,181,309,276)])}
for file,(start,points) in updates.items():
 p=B/file;v=read(p);v['keyframes']=[k for k in v['keyframes'] if k['t']<start]+[{'t':start+i,'upper':[ux,uy],'lower':[lx,ly]} for i,(ux,uy,lx,ly) in enumerate(points)]
 v['hideIntervals']+=([[677.4,678.7],[681.6,683.2],[693.6,697.7]] if file.startswith('gb04') else [[588,590.7],[591.2,592.7]] if file.startswith('gb03') else [[380.2,381.8],[392.5,393.8]])
 write(p,v)
late=[(290,176,320,264),(293,173,311,266),(299,186,306,266),(290,166,294,246),(293,165,304,254),(299,196,299,285),(311,198,281,292),(296,186,272,282),(313,205,277,290),(295,184,269,275),(296,150,254,242),(303,185,268,259),(312,183,240,253),(313,184,301,289),(311,163,306,244),(291,192,292,277),(300,195,269,278),(289,195,289,282)]
p=B/'gb03late-landmarks.json';write(p,{'id':'GB03late','sourceFile':'shared/output/game-math-part2-teaching-revision/sources/_dw9jjRpanA.mp4','coordinatePixels':[800,450],'keyframes':[{'t':603+i,'upper':[ux,uy],'lower':[lx,ly]} for i,(ux,uy,lx,ly) in enumerate(late)],'hideIntervals':[[612.5,615.5],[619.6,620]],'trackingMethod':'manual source pages; fast bank/foliage hidden; moving review pending','movingPixelApproval':False})
reg=read(B/'quaternion-annotation-tracks.json');reg['scenes']['GB03']['landmarkSources'].append(p.relative_to(ROOT).as_posix());write(B/'quaternion-annotation-tracks.json',reg)
print('Fine-frame source correction and extended editable tracks saved; moving approval false')
