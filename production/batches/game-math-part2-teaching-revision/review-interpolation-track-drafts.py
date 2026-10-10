"""Create direct image review sheets; detection is never pixel approval."""
from pathlib import Path
import json,bisect
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[3];B=Path(__file__).parent
D=B/'interpolation-tracks';O=ROOT/'shared/output/game-math-part2-teaching-revision/interpolation-track-authoring'
read=lambda p:json.loads(p.read_text(encoding='utf8'))
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',16)
for path in sorted(D.glob('*-board.json')):
    track=read(path);previous=None
    for key in track['keyframes']:
        points=np.array(key['wheel'])
        if previous is not None and key['t']-previous['t']<.15:
            old=np.array(previous['wheel'])
            if np.linalg.norm(points-old)>np.linalg.norm(points[::-1]-old):points=points[::-1]
        elif tuple(points[0])>tuple(points[1]):points=points[::-1]
        key['wheel']=points.tolist();previous=key
    track['endpointOrder']='Nearest continuous projected endpoints; reset after an unobserved gap. No front/back inference.'
    path.write_text(json.dumps(track,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def at(track,t,keys):
    frames=track['keyframes'];times=[x['t'] for x in frames]
    if len(frames)<2 or t<times[0] or t>times[-1] or any(a<=t<=b for a,b in track.get('hideIntervals',[])):return None
    j=min(len(frames)-2,max(0,bisect.bisect_right(times,t)-1));a,b=frames[j:j+2];u=(t-a['t'])/(b['t']-a['t'])
    return {k:np.array(a[k])*(1-u)+np.array(b[k])*u for k in keys}
for folder in sorted(O.glob('IG*')):
    record=read(folder/'frames.json');body=read(D/(folder.name.lower()+'-torso.json'));board=read(D/(folder.name.lower()+'-board.json'));images=[]
    for row in record['records']:
        im=Image.open(ROOT/row['frame']).convert('RGB');draw=ImageDraw.Draw(im);t=row['t']
        p=at(body,t,['upper','lower']);q=at(board,t,['wheel'])
        if p:draw.line([tuple(p['lower']),tuple(p['upper'])],fill='#ef5350',width=4)
        if q:draw.line([tuple(x) for x in q['wheel']],fill='#42a5f5',width=4)
        im=im.crop((200,70,650,420));draw=ImageDraw.Draw(im)
        for x in range(250,650,50):draw.text((x-200,0),str(x),font=font,fill='white',stroke_width=1,stroke_fill='black')
        for y in range(100,420,50):draw.text((0,y-70),str(y),font=font,fill='white',stroke_width=1,stroke_fill='black')
        images.append(im)
    for page in range((len(images)+8)//9):
        sheet=Image.new('RGB',(1350,1125),'white');draw=ImageDraw.Draw(sheet)
        for cell,(im,row) in enumerate(zip(images[page*9:(page+1)*9],record['records'][page*9:(page+1)*9])):
            x=cell%3*450;y=cell//3*375;sheet.paste(im,(x,y+25));draw.text((x+3,y+3),f"{folder.name} t{row['t']:.3f} CPU draft",font=font,fill='black')
        sheet.save(folder/f'body-board-draft-{page+1}.jpg',quality=95)
print('Independent endpoint continuity and review sheets saved; no pixel approvals granted.')
