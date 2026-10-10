"""Observed 800x450 source pixels; independent draft tracks, never world axes."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
tracks={
'GA03':{'start':130,'interval':[130,166],'pairs':[(302,163,302,232),(293,151,290,246),(340,173,365,267),(265,175,236,245),(261,158,261,228),(302,171,260,227),(300,185,263,248),(290,174,304,246),(308,192,292,254),(284,176,271,240),(301,178,284,233),(317,141,324,211),(240,186,245,271),(277,180,271,256),(302,164,292,251),(284,162,277,225),(279,159,290,231),(300,162,305,270)],'spec':{'revealAtLine':0,'showWheel':False,'showScreenReference':False}},
'GB01':{'start':166,'interval':[166,196],'pairs':[(270,162,269,234),(277,168,277,250),(289,145,295,223),(270,166,265,238),(278,159,279,226),(291,158,276,220),(272,210,225,246),(263,186,262,247),(278,205,224,259),(296,187,252,245),(303,169,269,219),(296,197,307,277),(279,182,286,259),(279,207,281,297),(270,158,276,240),(270,157,279,234),(280,154,286,229),(285,170,290,247)],'spec':{'revealAtLine':0,'showWheel':False,'showScreenReference':True}},
'GA07':{'start':56,'interval':[56,80],'pairs':[(256,178,250,242),(283,154,286,226),(280,141,276,212),(258,170,240,253),(249,199,252,277),(270,162,270,246),(264,168,262,246),(296,191,302,242),(296,205,289,264),(283,133,279,210),(292,180,297,237),(277,213,271,265),(275,196,270,245),(290,172,267,215),(278,171,283,251),(293,217,260,258),(287,187,289,256),(298,181,283,249)],'wheels':[(260,310,245,385),(268,298,245,388),(257,256,249,312),(252,323,225,399),(258,334,236,384),(268,289,253,352),(267,310,256,374),(288,304,258,383),(266,329,231,374),(274,251,270,316),(276,310,253,378),(260,309,261,367),(255,295,234,369),(256,275,211,328),(281,299,288,366),(254,321,218,361),(302,328,282,394),(269,316,230,380)],'hideIntervals':[[56,56.8]],'spec':{'revealAtLine':0,'showWheel':True,'showScreenReference':False}}
}
registry=read(B/'quaternion-annotation-tracks.json')
for ident,x in tracks.items():
 k=[]
 for index,(ux,uy,lx,ly) in enumerate(x['pairs']):
  r={'t':x['start']+index,'upper':[ux,uy],'lower':[lx,ly]}
  if 'wheels' in x:
   ax,ay,bx,by=x['wheels'][index];r['wheel']=[[ax,ay],[bx,by]]
  k.append(r)
 name=ident.lower()+'-landmarks.json'
 d={'id':ident,'sourceId':'_dw9jjRpanA','sourceFile':'shared/output/game-math-part2-teaching-revision/sources/_dw9jjRpanA.mp4','interval':x['interval'],'trackedInterval':[k[0]['t'],k[-1]['t']],'coordinatePixels':[800,450],'keyframes':k,'hideIntervals':x.get('hideIntervals',[]),'trackingMethod':'manually read source-frame pages1–2 at one-second boundaries; moving intermediates require review','meaning':'visible upper back and lower torso/cape base; screen projection only, not game-world or engine measurements','authoringPagesReviewed':2,'movingPixelApproval':False}
 write(B/name,d);registry['scenes'][ident]={'landmarks':(B/name).relative_to(ROOT).as_posix(),**x['spec'],'movingPixelApproval':False}
registry['all25ActualScenesReady']=False;write(B/'quaternion-annotation-tracks.json',registry)
print('Three additional observed tracks; moving pixels and narration review pending')
