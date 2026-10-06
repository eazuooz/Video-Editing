import hashlib,json,pathlib
from PIL import Image,ImageDraw,ImageFont
ROOT=pathlib.Path(__file__).resolve().parents[4]
BASE=pathlib.Path(__file__).resolve().parent
state=json.loads((BASE/'decode-execution-v1.json').read_text(encoding='utf-8'))
assert state['status']=='decoded-discovery-awaiting-direct-review'
assert state['allSourceFullDecode'] and all(x['fullDecodeExitCode']==0 for x in state['results'])
out=ROOT/'shared/output/familiar-game-rules/research/discovery-v1/boards'
assert not out.exists(), 'Existing boards: inspect and reuse instead of repeating.'
out.mkdir()
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
records=[]
for source in state['results']:
    files=sorted((ROOT/source['discovery']['directory']).glob('*.jpg'))
    assert len(files)==source['discovery']['frameCount']
    step=source['discovery']['intervalSeconds']
    for offset in range(0,len(files),6):
        board=Image.new('RGB',(1920,1710),'white'); draw=ImageDraw.Draw(board)
        tiles=[]
        for local,p in enumerate(files[offset:offset+6]):
            index=int(p.stem)-1; t=index*step
            image=Image.open(p); assert image.size==(960,540)
            x=(local%2)*960;y=(local//2)*570
            board.paste(image,(x,y+30));draw.text((x+10,y+4),f'{source["videoId"]}  discovery index {index+1}  nominal {t}s',font=font,fill='black')
            tiles.append({'frame':str(p.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'nominalSeconds':t,'timingPrecision':'coarse fps-filter discovery, not final in/out approval'})
        target=out/f'{source["videoId"]}-{offset//6+1:02}.jpg';board.save(target,quality=95)
        records.append({'board':str(target.relative_to(ROOT)).replace('\\','/'),'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'tiles':tiles,'directlyRead':False})
result={'schemaVersion':1,'slug':'familiar-game-rules','sourceFullDecode':True,'boardCount':len(records),'frameCount':sum(len(x['tiles']) for x in records),'boards':records,'directActionReview':False,'actualCutApproval':False,'imagesGitPolicy':'local-only'}
(BASE/'discovery-boards-v1.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'boards':result['boardCount'],'frames':result['frameCount'],'imagesGitPolicy':'local-only'}))
