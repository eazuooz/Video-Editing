"""Manual source-frame wing endpoints. Preserve rejected broad source drafts."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
tracks={
'GA02':{'source':'_dw9jjRpanA','start':94,'step':.5,'interval':[94,108],'pages':3,'points':[(212,283,432,215),(219,279,451,226),(198,246,416,300),(192,281,439,240),(198,254,429,247),(200,263,387,241),(235,250,383,247),(244,245,387,252),(220,215,332,303),(213,238,356,289),(268,299,421,185),(340,318,463,149),(260,275,506,208),(211,247,445,270),(211,222,403,290),(214,227,397,312),(191,193,307,340),(226,278,375,277),(221,275,401,246),(220,259,408,238),(310,326,447,184),(230,259,425,250),(259,267,442,224),(266,280,417,222),(230,258,419,254),(227,254,411,247),(253,311,437,221)],'spec':{'revealAtLine':1,'showScreenReference':False,'showProjectedAngle':False}},
'GA08':{'source':'4Odvp_TIeQU','start':475,'step':.5,'interval':[475,497],'pages':3,'points':[(112,277,416,287),(100,235,385,325),(237,222,390,262),(300,225,418,248),(265,250,398,253),(268,258,404,252),(235,246,416,271),(218,240,409,258),(218,243,421,244),(227,242,420,252),(223,242,410,256),(217,227,407,275),(220,215,385,291),(248,277,426,239),(230,254,424,251),(283,261,420,216),(276,280,462,211),(231,248,436,255),(295,241,435,242),(298,252,430,235),(272,244,425,260),(278,242,420,262),(248,244,452,272),(219,196,347,316),(220,226,364,319)],'spec':{'revealAtLine':1,'showScreenReference':False,'showProjectedAngle':False}},
'GB07':{'source':'4Odvp_TIeQU','start':546,'step':.5,'interval':[542,552],'pages':2,'points':[(132,274,418,255),(218,251,412,247),(262,245,415,243),(257,207,377,268),(248,207,402,294),(301,272,436,224),(302,313,432,164),(247,319,462,157),(249,265,487,281),(213,268,475,297),(316,311,513,218),(220,270,467,268),(210,191,420,327)],'spec':{'revealAtLine':1,'showScreenReference':False,'showProjectedAngle':False}}
}
registry=read(B/'quaternion-annotation-tracks.json')
for ident,x in tracks.items():
 source_file=('shared/output/game-math-part2-teaching-revision/sources/' if x['source']=='_dw9jjRpanA' else 'shared/output/game-math-part2-full-series/sources/')+x['source']+'.mp4'
 k=[{'t':x['start']+i*x['step'],'left':[ax,ay],'right':[bx,by]} for i,(ax,ay,bx,by) in enumerate(x['points'])]
 name=ident.lower()+'-landmarks.json';write(B/name,{'id':ident,'sourceId':x['source'],'sourceFile':source_file,'interval':x['interval'],'coordinatePixels':[800,450],'keyframes':k,'trackedInterval':[k[0]['t'],k[-1]['t']],'authoringPagesReviewed':x['pages'],'trackingMethod':'manual half-second endpoints; fast intermediate banks require direct moving review','meaning':'visible wing-tip span in camera projection; no measured game-world angle','movingPixelApproval':False})
 registry['scenes'][ident]={'landmarks':(B/name).relative_to(ROOT).as_posix(),**x['spec'],'movingPixelApproval':False}
write(B/'quaternion-annotation-tracks.json',registry)
print('Three observed wing tracks; final motion/caption approval remains pending')
