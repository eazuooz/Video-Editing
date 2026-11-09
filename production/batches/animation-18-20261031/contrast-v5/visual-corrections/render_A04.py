"""A04 actual axe-pose analysis, same narration/oldclock, no new source or audio."""
from pathlib import Path
import json,subprocess
from PIL import Image,ImageDraw
from render_A01 import H,R,sha,rel,read,text,outlined,encode,BG,WHITE,YELLOW,TEAL
O=H/'local/visual-corrections/A04';O.mkdir(parents=True,exist_ok=True)
def main():
    control=read(R/'shared/publishing/video-production-control.json')['animationContrastRevision20261108'];assert control['renderAuthorized']and'A04'in control['episodes']
    src=H/'footage/team-b/local/hades-training.mp4';im=Image.new('RGB',(1920,1080),BG);d=ImageDraw.Draw(im)
    text(d,(55,35),'도끼 높이와 몸의 자세',60,YELLOW);text(d,(55,111),'Hades II (Early Access v0.90437)',32,WHITE);text(d,(1480,117),'실제 프레임 분석',30,WHITE)
    crop=(740,240,1180,570);scale=780/440
    for i,(t,label,color)in enumerate([(40.1,'들어올리기 전',YELLOW),(40.55,'도끼를 들어올림',TEAL)]):
        source=Image.open(O/('hades-40.1.png'if i==0 else'pose-40.55.png')).convert('RGB');x=85+i*930;y=230
        im.paste(source.crop(crop).resize((780,585)),(x,y));d=ImageDraw.Draw(im);text(d,(x,170),label,44,color)
        # Editorial focus follows observed weapon pixels; no hidden joint measurement.
        box=(990,438,1076,491)if i==0 else(985,304,1030,406)
        mapped=tuple(int((v-crop[k%2])*scale+(x if k%2==0 else y))for k,v in enumerate(box));outlined(d,mapped,color)
        # Retain the complete original image/UI alongside the closer crop.
        im.paste(source.resize((300,169)),(x+20,250));d=ImageDraw.Draw(im);d.rectangle((x+19,249,x+320,419),outline=color,width=3)
        text(d,(x,823),f'관찰 시점 {t:.2f}초',32,WHITE)
    design=O/'hades-closeup-design.png';im.save(design);movie=O/'A04-correction-004677-004922-hades-closeup.mp4';encode(movie,245,lambda f:im)
    timing=H/'baseline-sentence-timing.json';row={'id':'A04-correction-004677-004922-hades-closeup','kind':'authored-explanation','startFrame':4677,'endFrame':4922,'newFrames':245,'picture':rel(movie),'pictureSha256':sha(movie),'sourceStartFrame':0,'sourceVerified':True,'expectedUnderlyingExplanationIds':[],'narrationEvidence':{'path':rel(timing),'sha256':sha(timing),'sentenceIds':['013']},'mediaSegments':[{'kind':'still-analysis','offsetFrame':0,'frames':245,'sourceKey':'hades-training','sourceLocalIn':40.1,'sourceLocalOut':40.55,'sourceFrameTimes':[40.1,40.55],'sourceSha256':sha(src),'nativeFrames':0}],'visualEvidence':{'source':rel(src),'sourceSha256':sha(src),'originalFrameTimes':[39.5,40.1],'adoptedFrameTimes':[40.1,40.55],'actualObservation':'37.5–43.25 at0.25s and40.45/40.55/40.65 inspected.40.1 shows low axe,40.55 clear raised axe before40.65 impact effect. Previous39.5/40.1 were both low poses.','sourceFrames':[rel(O/'hades-40.1.png'),rel(O/'pose-40.55.png')],'focus':'Actual axe position; torso/feet remain visible in closer unchanged-aspect crop with full-frame context inset.','cropXYXY':list(crop),'newGameMechanicOrInternalMeasurementClaim':False},'reason':'Make the narrated preparation posture visible at mobile size using two observed poses from the same cleared source.','captionSafeBottomY':892,'newAudio':False,'newTts':False}
    result={'schemaVersion':1,'episode':'A04','clock':'relations-v4','readyForAssembly':True,'pictureEdits':[row],'sourceCode':rel(Path(__file__)),'sourceCodeSha256':sha(__file__),'humanFullWatch':False,'patchQa':'Actual current ASS sample generated separately; final rebuilt master review pending.'}
    (H/'visual-corrections/A04.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n','utf8')
    ass=H/'local/final-audio/A04/captions/captions.provisional.ko.ass';out=O/'hades-closeup-actual-ass.png'
    subprocess.run(['ffmpeg','-v','error','-threads','1','-ss','1.5','-i',str(movie),'-vf',f"setpts=PTS+81.366667/TB,ass='{rel(ass)}'",'-frames:v','1','-fps_mode','passthrough','-threads','1','-y',str(out)],check=True)
    Image.open(out).resize((375,211),Image.Resampling.LANCZOS).save(O/'hades-closeup-actual-ass-375.png')
    print(rel(H/'visual-corrections/A04.json'),flush=True)
if __name__=='__main__':main()
