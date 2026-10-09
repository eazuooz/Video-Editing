from pathlib import Path
from datetime import datetime,timezone
import hashlib,json,os
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import psutil
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).parent/'revision-balatro60-v2'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
out=ROOT/'shared/output/presenting-game-scores/revision-balatro60-v2/credit-composition-v7'
assert not out.exists(), 'Preserve completed composition review'
approval=read(BASE/'description-credit-approval-v1.json')
assert approval['userAnswer']=='응 넣어' if 'userAnswer' in approval else '응 넣어' in json.dumps(approval,ensure_ascii=False)
old=read(BASE/'native-actions-sample-direct-review-v3.json')
cuts=[('04','three-kind-extra-card',354,364),('04','enhanced-two-pair',668,681),('05','pair',240,246),('05','round-accumulate',1103,1114),('07','full-house',395,411),('08','diamond-full-house',998,1010),('08','decimal-mult',1286,1296),('09','straight-400',1255,1266),('09','enhanced-704',1213,1224),('10','debuff-diamond',1399,1409)]
assert sum(b-a for _,_,a,b in cuts)==110
samples={}
for board in old['boards']:
 for e in board['entries']:samples[(e['interval'],e['sourceFrame'])]=e
intervals={x['id']:x for x in old['intervals']}
font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
creditFont=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
labelFont=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
out.mkdir(parents=True)
entries=[]; selected=[]
for ch,ident,a,b in cuts:
 iv=intervals[ident];assert iv['preflightStartSeconds']<=a<b<=iv['preflightEndSecondsExclusive']
 assert sha(Path(iv['ptsRecord']))==iv['ptsRecordSha256']
 selected.append({'id':ident,'chapter':ch,'sourceStartFrame':a*60,'sourceEndFrameExclusive':b*60,'sourceFirstPts':a*15360,'sourceEndPtsExclusive':b*15360,'timebase':'1/15360','frames':(b-a)*60,'seconds':b-a,'normalSpeed':True,'loop':False,'slowdown':False,'claim':iv['claim'],'observations':iv['observations'],'nativePtsEvidence':iv['ptsRecord'],'nativePtsEvidenceSha256':iv['ptsRecordSha256']})
 for second in range(a,b):
  e=samples[(ident,second*60)];src=Path(e['path']);assert sha(src)==e['sha256'];assert e['sourcePts']==second*15360
  im=Image.open(src).convert('RGB');proxy_size=im.size
  assert proxy_size==(948,533), 'Existing reviewed source QA proxy dimensions changed'
  im=im.resize((1920,1080),Image.Resampling.LANCZOS)
  canvas=im.filter(ImageFilter.GaussianBlur(28)).point(lambda x:int(x*.30))
  canvas.paste(im.resize((1600,900),Image.Resampling.LANCZOS),(160,0))
  d=ImageDraw.Draw(canvas)
  d.rectangle((12,320,148,499),fill=(0,0,0))
  for n,line in enumerate(['Footage:','Squeaky','Whale','Gameplay','Archive']):d.text((18,328+n*29),line,font=creditFont,fill='white')
  lines=['카드의 반응 뒤에 숫자가 커지고','강조되는 모습을 보세요.'];width=max(d.textbbox((0,0),t,font=font)[2] for t in lines)+44;height=146
  x=960-width/2;y=970-height/2
  d.rectangle((x+14,y+14,x+width+14,y+height+14),fill='#073c32');d.rectangle((x,y,x+width,y+height),fill='white',outline='#161b18',width=3)
  for n,t in enumerate(lines):d.text((960,y+12+n*62),t,font=font,fill='#080b09',anchor='mt')
  p=out/f'{ident}-{second:04}.jpg';canvas.save(p,quality=93)
  entries.append({'cut':ident,'chapter':ch,'sourceFrame':second*60,'sourcePts':second*15360,'sourceInput':e,'proxyInputSize':list(proxy_size),'rescaledQaProxyNotFullNativePixels':True,'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'finalCue':False})
boards=[]
for start in range(0,len(entries),6):
 group=entries[start:start+6];board=Image.new('RGB',(1920,810),'#1b1b1b');d=ImageDraw.Draw(board)
 for k,e in enumerate(group):
  x=(k%3)*640;y=(k//3)*405;board.paste(Image.open(ROOT/e['path']).resize((640,360)),(x,y));d.text((x+5,y+362),f"{e['cut']} native f{e['sourceFrame']} PTS{e['sourcePts']}",font=labelFont,fill='white')
 p=out/f'board-{len(boards)+1:03}.jpg';board.save(p,quality=94);boards.append({'path':p.relative_to(ROOT).as_posix(),'sha256':sha(p),'entries':group,'directlyRead':False})
proof={'schemaVersion':1,'preparedAt':datetime.now(timezone.utc).isoformat(),'actualPid':os.getpid(),'createTime':psutil.Process().create_time(),'cpuThreads':2,'gpuJobs':0,'sourceSamplesReused':len(entries),'newSourceExtraction':0,'proxyInputSize':[948,533],'rescaledQaProxyNotFullNativePixels':True,'sourceCrop':False,'videoRect':[160,0,1600,900],'sameFrameBlurFill':True,'captionCenter':[960,970],'onscreenCredit':'Footage: Squeaky Whale Gameplay Archive','descriptionApproval':'projects/presenting-game-scores/production/revision-balatro60-v2/description-credit-approval-v1.json','cuts':selected,'selectedBalatroFrames':6600,'boards':boards,'allCompositionSamplesDirectlyRead':False,'preparedCaptionNotFinalCues':True,'finalPixelsApproved':False,'sourceAdopted':False,'publicRightsApproved':False,'researchChanges':0,'newGitImages':0,'preservedFailedV6':{'exitCode':1,'reason':'Existing source QA samples are 948x533 proxies, not 1920x1080 pixels. No images created before the assertion.','path':'shared/output/presenting-game-scores/revision-balatro60-v2/credit-composition-v6','imagesCreated':0}}
(BASE/'credit-composition-review-plan-v7.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps({'samples':len(entries),'boards':len(boards),'BalatroFrames':6600,'newNativeExtraction':0,'researchChanges':0}))
