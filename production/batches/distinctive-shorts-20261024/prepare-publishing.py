"""Prepare only the five delivered masters authorized on 2026-10-25.
No network/platform operation. The additional sixth Short has no approved master yet.
"""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[3];B=Path(__file__).parent
def read(p):return json.loads(p.read_text(encoding='utf8'))
def save(p,d):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.datetime.now(datetime.timezone.utc).isoformat()
user='하나씩 날짜 맞춰서 올려줘 예약날짜는 오늘부터 저녁 5시야~'
extra='그리고 포털의 순간이동 관련된것도 쇼츠 하나 만들어줘~6편으로 그리고 업로드해줘'
batch=read(B/'batch.json');defaults=read(R/'shared/publishing/youtube-defaults.json')
footerKo=(R/defaults['description']['channelDefaultSnapshot']).read_text(encoding='utf8').split('📚 수업 노트')[0].strip()
footerEn='YamYamCoding — game programming with DirectX, Unity, Unreal Engine and computer graphics.\n\nProgramming coaching\n'+defaults['coaching']['url']+'\n\nCommunity\nhttps://discord.gg/wZuqe7fqkR\n\nChannel membership\n'+defaults['membershipUrl']
titlesEn=["Titanfall 2's Time Travel Was a Vertical Teleport? #GameDev #Shorts","How Small Objects Really Grow in Superliminal | Forced Perspective","Ghost of Tsushima Fixed Non-Burning Leaves with Wind? #GameDev","Why Switching Animations Can Still Look Smooth | Inertialization","Portals Inside Portals: Does the Game Render Forever? #GameDev"]
introsEn=[
"Titanfall 2's Effect and Cause connects two eras with vertically stacked maps and teleportation. See the game and our Unity reconstruction. The 10 m gap is an example value from our demo.",
"Superliminal changes an object's distance and actual size together while keeping its apparent size. Compare the player's view with a side view. The 2 m to 6 m example is from our demo.",
"During development of Ghost of Tsushima, leaves could fall into a campfire without burning. Wind emitters created an updraft to keep most leaves out. Actual game footage is paired with a Unity reconstruction using identical initial leaf conditions.",
"Gears of War 4's inertialization switches to a new animation and smoothly removes the difference from the old pose. Our articulated characters show why pose offsets and velocity matter. The angles and timing are values from our demo.",
"A stencil buffer marks the portal area, and recursive rendering draws the view through nested portals. Our Unity demonstration uses render textures and stencil masking. Its view counts are not measurements of Valve's engine."]
items=[]
for i,slug in enumerate(batch['authorization']['slugs']):
 p=R/'projects'/slug;d=read(p/'production/delivery.json');m=read(p/'publishing/metadata.json');src=read(p/'sources/selected-footage.json');plan=read(p/'planning/production-plan.json')
 master=Path(d['files']['captioned']['path']);assert sha(master)==d['files']['captioned']['sha256']
 for f in d['files'].values():assert sha(Path(f['path']))==f['sha256']
 acceptance={'status':'accepted-for-upload-and-schedule','kind':'explicit-upload-and-schedule-request-after-complete-local-delivery','userEvidence':user,'recordedAt':now,'masterSha256':d['files']['captioned']['sha256'],'wholeListeningExplicitlyConfirmed':False}
 body=m['description'].split('\n\n자료\n',1)[0]
 credits=m['description'].split('\n\n자료\n',1)[1]
 tools='\n\n제작 도구\nUnity — https://unity.com/\nMotion Canvas — https://motioncanvas.io/\n'
 ko=body+'\n\n'+footerKo+'\n\n출처·자료 및 제작 도구\n'+credits.strip()+tools
 sources='\n'.join(s['url'] for s in plan['research']['primarySources'])
 enCredits='Technical sources\n'+sources+'\n\nGameplay recording\n'+src['title']+' — '+src['recorder']+'\n'+src['url']+'\nThe recording is labeled Creative Commons Attribution (CC BY) on YouTube. Excerpted, arranged vertically, annotated, captioned and narrated; original recording audio removed. Game rights remain with their respective owners.\nhttps://support.google.com/youtube/answer/2797468\nhttps://creativecommons.org/licenses/by/4.0/'
 if i==0:enCredits+='\n\nThis video is not endorsed by or affiliated with EA or its licensors.\nKayKit Adventurers / Kay Lousberg — CC0; knight character in the Unity demo.\nhttps://kaylousberg.itch.io/kaykit-adventurers'
 enCredits+='\n\nMusic\nPixel Peeker Polka - faster Kevin MacLeod (incompetech.com)\nLicensed under Creative Commons: By Attribution 4.0 License\nhttps://creativecommons.org/licenses/by/4.0/\nhttps://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100833\nMusic edited, faded and mixed.\n\nProduction tools\nUnity — https://unity.com/\nMotion Canvas — https://motioncanvas.io/'
 en=introsEn[i]+'\n\n#GameDev #GameTechnology #Shorts\n\n'+footerEn+'\n\nSources, assets and production tools\n'+enCredits
 assert len(ko)<=5000 and len(en)<=5000 and len(titlesEn[i])<=100 and len(m['title'])<=100
 schedule={'requestedLocal':f'2026-10-{25+i:02d}T17:00:00+09:00','timezone':'Asia/Seoul','status':'pending-platform-save','active':False,'userEvidence':user}
 receipt={'schemaVersion':1,'slug':slug,'status':'prepared-not-uploaded','videoId':None,'video':{'path':master.relative_to(R).as_posix(),'sha256':d['files']['captioned']['sha256'],'bytes':d['files']['captioned']['bytes'],'seconds':d['durationSeconds'],'width':1080,'height':1920,'fps':60},'userAcceptance':acceptance,'metadata':{'title':m['title'],'description':ko,'tags':m['tags'],'language':'ko','categoryId':'27','privacyStatus':'private','madeForKids':False},'englishMetadata':{'title':titlesEn[i],'description':en},'subtitles':[{'language':lang,'path':Path(d['files'][lang]['path']).relative_to(R).as_posix(),'sha256':d['files'][lang]['sha256'],'status':'pending-platform-save'} for lang in ['ko','en']],'schedule':schedule,'sourceCredits':{'ko':credits.strip()+tools,'en':enCredits},'pinnedComment':{'status':'pending-video-publication','commentId':None},'fullSettings':False,'platformStateVerified':False}
 target=p/'publishing/youtube-upload.json';assert not target.exists(),'Do not overwrite an existing platform receipt'
 save(target,receipt)
 for lang,txt in [('ko',ko),('en',en)]: (p/f'publishing/upload-description.{lang}.txt').write_text(txt+'\n',encoding='utf8')
 (p/'publishing/pinned-comment.ko.txt').write_text('게임 개발 원리를 직접 구현하며 공부하고 싶다면 얌얌코딩 프로그래밍 코칭을 확인해 보세요.\n'+defaults['coaching']['url']+'\n',encoding='utf8')
 for file in ['production/review-ledger.json','production/checkpoint.json']:
  j=read(p/file);j['userAcceptance']=acceptance;j['humanFinalReview']='accepted-for-upload-and-schedule-via-direct-request';j['updatedAt']=now
  if file.endswith('checkpoint.json'):j['nextAction']='Upload unchanged approved master once; finish available settings and verify requested local schedule.'
  save(p/file,j)
 project=read(p/'project.json');project['publishingAuthorization']=acceptance;project['status']='approved-publishing-in-progress';save(p/'project.json',project)
 items.append({'slug':slug,'order':i+1,'captionedSha256':receipt['video']['sha256'],'requestedLocal':schedule['requestedLocal'],'videoId':None,'status':'prepared-not-uploaded'})
auth={'id':'six-short-daily-1700-20261025','recordedAt':now,'userEvidence':[user,extra],'timezone':'Asia/Seoul','startDate':'2026-10-25','time':'17:00','fiveDeliveredMastersAccepted':True,'sixthStatus':'production-requested; no delivered master or actual human review yet','sixthSlug':'shorts-portal-teleport-momentum','sixthTarget':'2026-10-30T17:00:00+09:00','items':items,'preserveOtherSchedules':True,'noDeletionAuthorized':True}
save(B/'publishing-schedule.json',auth)
control=read(R/'shared/publishing/video-production-control.json');control['shortsPublishingBatchAuthorization']=auth;save(R/'shared/publishing/video-production-control.json',control)
print(json.dumps({'prepared':len(items),'dates':[x['requestedLocal'] for x in items],'sixth':auth['sixthStatus']},ensure_ascii=False))
