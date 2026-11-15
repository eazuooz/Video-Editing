"""Pure frame layout for the new lock-on film. No import-time media work.

Samples are design evidence only. Native frames are read from an actual pilot
or full capture; missing frames never loop or fall back to invented pictures.
The sign animation is a separately authored2D explanation, not game footage.
"""
from pathlib import Path
import argparse,hashlib,json,math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3]
PROJECT=ROOT/'projects/shorts-oot-ninja-show-z-targeting'
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')/PROJECT.name
FONT=Path('C:/Windows/Fonts/NotoSansKR-VF.ttf');BOLD=Path('C:/Windows/Fonts/malgunbd.ttf')
TOKENS=dict(background='#000000',ink='#f5f5f5',title='#e8cf83',relation='#73c7c2',changed='#f39a4b',problem='#ef8585')
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def font(size,bold=False):
    f=ImageFont.truetype(str(BOLD if bold else FONT),size)
    if not bold and hasattr(f,'set_variation_by_name'):f.set_variation_by_name('Medium')
    return f
def wrap(text,f,width=800):
    words=text.split();lines=[];line=''
    for w in words:
        trial=(line+' '+w).strip()
        if f.getlength(trial)<=width:line=trial
        else:
            if not line:raise ValueError('One token exceeds fixed caption width: '+w)
            lines.append(line);line=w
    if line:lines.append(line)
    if len(lines)>2:raise ValueError('Split the semantic clause; do not shrink fixed captions: '+text)
    return lines
class Composer:
    def __init__(self):
        self.title=font(76,True);self.label=font(34,True);self.body=font(42);self.caption=font(48)
        for p in read(PROJECT/'planning/caption-clauses-v1.json')['paragraphs']:
            for ko,en in p['clauses']:wrap(ko,self.caption);wrap(en,self.caption)
        provenance=read(ROOT/'shared/assets/branding/cat-reactions-v1/provenance.json');self.cats={}
        for row in provenance['assets']:
            p=ROOT/row['path'];assert sha(p)==row['sha256'];self.cats[row['pose']]=Image.open(p).convert('RGBA')
    def base(self,label):
        im=Image.new('RGB',(1080,1920),TOKENS['background']);d=ImageDraw.Draw(im)
        for text,y,c in [('닌자쇼에서 찾은',145,TOKENS['ink']),('젤다 락온의 비밀',240,TOKENS['title'])]:
            d.text((492,y),text,font=self.title,anchor='mm',fill=c)
        d.text((492,348),label,font=self.label,anchor='mm',fill=TOKENS['relation']);return im
    def captioned(self,im,text):
        if not text:return im
        lines=wrap(text,self.caption);d=ImageDraw.Draw(im);width=max(d.textlength(x,font=self.caption)for x in lines)+44;height=len(lines)*62+22
        x=492-width/2;y=1600-height/2
        d.rectangle((round(x+14),round(y+14),round(x+width+14),round(y+height+14)),fill='#073c32')
        d.rectangle((round(x),round(y),round(x+width),round(y+height)),fill='white',outline='#161b18',width=3)
        for i,line in enumerate(lines):d.text((492,y+11+31+i*62),line,font=self.caption,fill='#080b09',anchor='mm')
        return im
    def native(self,mode,view,frame,caption='',capture_kind='pilot'):
        proof=read(MEDIA/'native-v1'/('accepted-'+capture_kind+'.json'));assert proof['actualUnityCapture']
        p=Path(proof['capture'])/mode/view/f'{frame:05}.png';assert p.is_file(),'Exact captured frame missing'
        trace=read(p.parent/'trace.json');assert trace['fingerprint']==proof['fingerprint'];row=next(x for x in trace['frames']if x['frame']==frame)
        labels={'target-relative':'해설용 모형 · 상대 중심 이동','free-movement':'해설용 모형 · 같은 입력, 고정된 이동축','turn-taking-intents':'해설용 모형 · 공격 참여 차례','simultaneous-intents':'해설용 모형 · 동시 행동 비교'}
        im=self.base(labels[mode]);im.paste(Image.open(p).convert('RGB').resize((984,984),Image.Resampling.LANCZOS),(0,396));d=ImageDraw.Draw(im)
        # Projected points come from this exact rendered frame, rather than a
        # guessed screen location or a camera-origin visibility claim.
        if row['model']['targetRelative']:
            hx,hy=row['heroScreenX']*984,396+(1-row['heroScreenY'])*984
            tx,ty=row['targetScreenX']*984,396+(1-row['targetScreenY'])*984
            if all(math.isfinite(x)for x in [hx,hy,tx,ty])and 20<tx<964 and 420<ty<1340:
                d.ellipse((tx-47,ty-47,tx+47,ty+47),outline=TOKENS['relation'],width=7)
                label='현재 상대'
                if mode=='turn-taking-intents':label='이번 차례의 상대'
                lx=max(170,min(814,tx));ly=max(470,ty-120);box=d.textbbox((lx,ly),label,font=self.label,anchor='mm');d.rectangle((box[0]-12,box[1]-8,box[2]+12,box[3]+8),fill='black');d.text((lx,ly),label,font=self.label,fill=TOKENS['relation'],anchor='mm')
        d.text((44,1412),'플레이어 시점'if view=='player'else'관찰자 시점',font=self.label,fill=TOKENS['ink'])
        return self.captioned(im,caption),dict(sourcePath=str(p),traceFrame=row,bodyRect=[0,396,984,984],finalFilm=False)
    def sign(self,seconds,caption=''):
        im=self.base('해설용 도식 · 표지판과 몸의 방향');d=ImageDraw.Draw(im)
        for x in range(80,950,80):d.line((x,480,x,1320),fill='#142326',width=2)
        for y in range(480,1350,80):d.line((64,y,920,y),fill='#142326',width=2)
        cx,cy=530,880;radius=230;u=max(0,min(1,seconds/5));angle=-math.pi*.75+u*math.pi*1.8
        x=cx+radius*math.cos(angle);y=cy+radius*math.sin(angle)
        d.rectangle((cx-86,cy-48,cx+86,cy+48),fill='#615036',outline=TOKENS['title'],width=5)
        d.text((cx,cy),'표지판',font=self.body,fill='white',anchor='mm')
        d.ellipse((cx-radius,cy-radius,cx+radius,cy+radius),outline='#587576',width=4)
        d.ellipse((x-30,y-30,x+30,y+30),fill=TOKENS['relation'])
        # Tangential facing makes the alignment problem visible; no claim of
        # observed Mario input, collision or developer-original numeric values.
        dx,dy=-math.sin(angle),math.cos(angle);tip=(x+100*dx,y+100*dy)
        d.line((x,y,*tip),fill=TOKENS['changed'],width=10)
        d.polygon([tip,(tip[0]-26*dx+13*dy,tip[1]-26*dy-13*dx),(tip[0]-26*dx-13*dy,tip[1]-26*dy+13*dx)],fill=TOKENS['changed'])
        d.text((492,1260),'위치가 가까워도, 몸의 방향은 따로 맞춰야 합니다.',font=self.label,fill=TOKENS['ink'],anchor='mm')
        return self.captioned(im,caption),dict(kind='authored2Dsign-alignment',seconds=seconds,player=[x,y],facing=[dx,dy],notGameTelemetry=True,finalFilm=False)
def main():
    p=argparse.ArgumentParser();p.add_argument('--samples',type=Path);a=p.parse_args();c=Composer()
    if a.samples:
        a.samples.mkdir(parents=True,exist_ok=False);records=[]
        for key,request in [('relative',('target-relative','player',360,'옆으로 움직여도 상대를 바라봅니다.')),('turns',('turn-taking-intents','player',240,'한 명이 싸우는 동안'))]:
            im,e=c.native(*request);out=a.samples/(key+'.png');im.save(out);im.resize((375,667),Image.Resampling.LANCZOS).save(a.samples/(key+'-375.png'));records.append(dict(image=str(out),**e))
        im,e=c.sign(2,'표지판을 향해 몸을 맞추려다');out=a.samples/'sign.png';im.save(out);im.resize((375,667),Image.Resampling.LANCZOS).save(a.samples/'sign-375.png');records.append(dict(image=str(out),**e))
        (a.samples/'samples.json').write_text(json.dumps(dict(designSamples=True,finalFilm=False,records=records),ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(a.samples)
    else:print(json.dumps(dict(clauseFontsMeasured=True,modelStarted=False,finalFilm=False)))
if __name__=='__main__':main()
