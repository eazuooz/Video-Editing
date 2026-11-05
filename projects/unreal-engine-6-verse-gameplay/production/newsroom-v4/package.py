"""Collect the sourced Actor/Pawn replacement and generate the Studio descriptions."""
from pathlib import Path
import json,subprocess,shutil,hashlib
from datetime import datetime,timezone
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];L=P/'production/local/newsroom-v4';B=P/'production/local/newsroom-v3';U=P/'publishing/studio-newsroom-v3'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def rel(p):return p.relative_to(R).as_posix()
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
title='언리얼 6에서 블루프린트가 사라진다? 그럼 왜 언리얼을 쓸까?'
en_title='No Blueprints in Unreal Engine 6? Why Stick With Unreal?'
def clock(s):return f'{int(s)//60:02}:{int(s)%60:02}'
def main():
 v=read(L/'encoded-verification.json');t=read(L/'timeline.json');old=read(B/'timeline.json')
 movies=B/'delivery/output'/P.name
 assert sha(movies/(P.name+'.captioned.mp4'))=='ac28c6ae0c49733ca90818af8131a683c1c917703c708f8444ec18b7a4eadbff'
 assert v['masters']['captioned']['sha256']==sha(L/'captioned.mp4')
 for lang in ('ko','en'):
  baseline=read(P/'production/newsroom-v3'/f'narration.{lang}.json')
  insert=read(H/f'added.{lang}.json')['scenes']
  for i,s in enumerate(insert):
   s['id']=f'03{chr(97+i)}'
  baseline['scenes'][3:3]=insert;save(H/f'narration.{lang}.json',baseline)
 stamp=datetime.now(timezone.utc).isoformat();total=t['totalFrames']/60
 ko_chapters=['에픽의 블루프린트 작업 화면','6월 시카고 로드맵','11월 도쿄에서 바뀐 계획','액터·폰·캐릭터, 무엇이 바뀔까?','포트나이트의 씬 그래프','AI가 움직이는 에디터','언리얼을 계속 쓸 이유','무료 고도와 유니티 비교','출시 후 엔진 비용']
 en_chapters=['Blueprints in the editor','The June roadmap','The November Tokyo announcement','Actors, Pawns and Characters','Scene Graph in Fortnite','AI in the editor','Why stay with Unreal?','Godot and Unity','Costs after launch']
 points=[2+s['startFrame']/60+(t['addedFrames']/60 if i>=3 else 0) for i,s in enumerate(old['scenes'])]
 points[0]=0;points.insert(3,t['boundary']/60)
 old_sources=(P/'production/newsroom-v3/sources.txt').read_text('utf-8-sig').split('Epic Games 안내\n',1)[1]
 notice,credits=old_sources.split('\n\n영상·기사·음악 출처\n')
 extra_sources='Epic Games · Pawn / Gameplay Framework (UE5)\nhttps://dev.epicgames.com/documentation/en-us/unreal-engine/pawn-in-unreal-engine\nhttps://dev.epicgames.com/documentation/en-us/unreal-engine/gameplay-framework-in-unreal-engine\nEpic Games · Possessing Pawns (UE4.27) · Possess 노드 예시\nhttps://dev.epicgames.com/documentation/en-us/unreal-engine/possessing-pawns?application_version=4.27\n'
 meta=read(B/'sources/bp-work.info.json')
 bp_url=meta.get('webpage_url') or ('https://www.youtube.com/watch?v='+meta['id'])
 sources='Epic Games 안내\n'+notice+'\n\n영상·기사·음악 출처\n'+credits.strip()+'\nUnreal Engine · Blueprint Communications | Live Training\n'+bp_url+'\n'+extra_sources
 (H/'sources.txt').write_text(sources,encoding='utf-8')
 for lang,chapters in [('ko',ko_chapters),('en',en_chapters)]:
  intro=('블루프린트가 사라진다면, 언리얼에 남을 이유는 무엇일까요? 에픽의 시카고 발표와 11월 도쿄 현장 보도를 비교하고, 기존 액터·폰·캐릭터 구조가 조종 코드에 미치는 영향과 무료 고도·유니티·언리얼의 출시 비용을 살펴봅니다.\n2026년 11월 5일 기준.' if lang=='ko' else
   'If Blueprints go away in Unreal Engine 6, why stay with Unreal? We compare the Chicago roadmap with the Tokyo keynote report, follow the Actor–Pawn–Character hierarchy into a player’s controls, and compare the costs of shipping with Unreal, Unity or Godot. Reported November 5, 2026.')
  footer=('프로그래밍 코칭' if lang=='ko' else 'Programming coaching')+'\nhttps://www.yamyamcoding.com/1430b1ff-a61e-8040-a542-d672d5d25328\nDiscord\nhttps://discord.gg/wZuqe7fqkR\n'+('멤버십' if lang=='ko' else 'Channel membership')+'\nhttps://www.youtube.com/channel/UCOgtkPoyC0VXhCs7Xk3jvjQ/join'
  credit_text=sources if lang=='ko' else ('Epic Games notice\n'+notice+'\n\nFootage, reporting, documentation and music\n'+'\n'.join(line if line.startswith('https://') else line.split(' (')[0].split(' · ')[0] for line in (credits.strip()+'\nUnreal Engine · Blueprint Communications\n'+bp_url+'\n'+extra_sources).splitlines()))
  if lang=='en':credit_text=(H/'credits.en.txt').read_text(encoding='utf-8')
  out=intro+'\n\n'+'\n'.join(clock(s)+' '+name for s,name in zip(points,chapters))+'\n\n'+footer+'\n\n'+credit_text.strip()+'\n'
  assert len(out)<5000;(U/f'description.{lang}.txt').write_text(out,encoding='utf-8')
 # Always preserve an unambiguous, hash-verified record of the local v3 master.
 pr=read(P/'project.json');pr.update(revision='newsroom-v4',title=title,titles={'ko':title,'en':en_title},status='revised-master-ready-for-requested-private-upload',humanFinalReview=False)
 pr['paths'].update(script=rel(H/'narration.ko.json'),scriptKo=rel(H/'narration.ko.json'),scriptEn=rel(H/'narration.en.json'),timeline=rel(L/'timeline.json'),videoClean=rel(L/'clean.mp4'),videoBurnedCaptions=rel(L/'captioned.mp4'),audioMix=rel(L/'final-mix.wav'),captionsKo=rel(L/'captions.ko.srt'),captionsEn=rel(L/'captions.en.srt'),narrationScriptReview=rel(H/'passages.txt'))
 pr['delivery']={'localStorageRoot':rel(L/'delivery')};pr['finalRender']={'status':'verified','openItems':['현재 수정본 전체 사람 청취 미확인']};save(P/'project.json',pr)
 subprocess.run(['node','scripts/collect-video-output.cjs',P.name],cwd=R,check=True)
 dest=L/'delivery/output'/P.name;report=read(P/'production/delivery-output.json')
 assert all(sha(dest/f['name'])==f['sha256'] for f in report['files'])
 shutil.copyfile(H/'sources.txt',dest/'sources.txt');save(dest/'delivery-manifest.json',report)
 page=dest/'index.html';page.write_text(page.read_text('utf-8').replace('</h1>','</h1><p><a href="'+P.name+'.captioned.mp4#t='+str(t['boundary']/60)+'">액터·폰·컨트롤러와 UE6 전환 보기</a></p>',1),encoding='utf-8')
 result={'revision':'newsroom-v4','masterSha256':v['masters']['captioned']['sha256'],'previousMasterSha256':'ac28c6ae0c49733ca90818af8131a683c1c917703c708f8444ec18b7a4eadbff','durationSeconds':total,'captioned':rel(dest/(P.name+'.captioned.mp4')),'directory':rel(dest),'format':'1920x1080 60fps','bilingualCues':len(read(L/'cue-review.json')),'addedAt':t['boundary']/60,'sourceScope':'Tokyo names the Actor/Blueprint/C++ gameplay framework transition; the effect on existing Pawn-derived code is an inference from Epic’s class hierarchy, not a separately announced Pawn replacement.','sources':rel(H/'sources.txt'),'verified':v,'audioCoverage':[s['coverage'] for s in t['extra']],'wholeHumanListening':False,'privateUploadExplicitlyRequested':True,'publishDateOwner':'user','preparedAt':stamp}
 save(H/'checkpoint.json',result)
 print(title,total,result['masterSha256'])
if __name__=='__main__':main()
