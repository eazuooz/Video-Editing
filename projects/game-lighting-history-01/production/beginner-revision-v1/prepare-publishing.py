"""Prepare retimed metadata; does not imply render, collection or upload."""
import pathlib,json,hashlib,datetime
R=pathlib.Path(__file__).resolve().parents[4];P=R/'projects/game-lighting-history-01';O=P/'production/local/beginner-revision-v1';PUB=P/'publishing'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def wr(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def main():
 plan=rd(O/'plan.json');old=rd(PUB/'upload-package-v1.json');defaults=rd(R/'shared/publishing/youtube-defaults.json');names={c['id']:c for c in old['chapters']};chapters=[]
 for i,c in enumerate(plan['chapters']):chapters.append(dict(id=c['id'],seconds=0 if i==0 else c['startFrame']/60,ko=names[c['id']]['ko'],en=names[c['id']]['en']))
 chapters.append(dict(id='membership',seconds=(plan['frames']-600)/60,ko='멤버쉽가입 감사드립니다.',en='Thank you to our members'))
 def stamps(lang):
  return '\n'.join(f"{int(c['seconds'])//60:02}:{int(c['seconds'])%60:02} {c[lang]}" for c in chapters)
 ko="""게임 속 조명과 그림자는 어떻게 만들어질까요? 픽셀·깊이·표면 방향부터 출발해 둠의 구역 밝기, 퀘이크의 라이트맵, 섀도 맵, 포워드·디퍼드 렌더링을 연결합니다.

처음 공부하는 분도 따라올 수 있도록 낯선 용어를 먼저 풀고, 작은 계산 예제와 같은 장면의 전후 모습을 차례로 보여 줍니다. 특히 포워드와 디퍼드는 같은 표면·같은 조명을 두고 어떤 정보를 언제 계산하고 저장하는지 비교합니다.

실제 게임과 언리얼 엔진 시연에 Three.js 입체 설명, Manim 수식 전개와 도식을 함께 사용합니다. 설명용 비유·수치와 실제 화면에서 확인되는 결과를 구별합니다. 게임 렌더링 이야기 1편의 기초 설명 보강본입니다.

"""+stamps('ko')+'\n\n🎮'+(PUB/'description.ko.txt').read_text(encoding='utf8').split('🎮',1)[1]
 ko=ko.replace(stamps('ko')+'\n\n게임 개발',stamps('ko')+'\n\n🎮 게임 개발')
 en="""How are lighting and shadows in games made? Start with pixels, depth and surface directions, then follow DOOM sector brightness, Quake lightmaps, shadow maps, and forward and deferred shading.

This beginner revision introduces unfamiliar terms before using them, works through small numerical examples, and compares before/action/result in the same scene. Forward and deferred shading are explained using the same surfaces and lights so you can follow when information is calculated and stored.

Actual game footage and Unreal Engine demonstrations are paired with Three.js spatial explanations, Manim equations and diagrams. Illustrative numbers and analogies are distinguished from directly observed results. Part 1 of our game-rendering series.

"""+stamps('en')+'\n\nYamYam Coding'+old['descriptionEn'].split('YamYam Coding',1)[1]
 en=en.replace(stamps('en')+'\n\n teaches',stamps('en')+'\n\nYamYam Coding teaches')
 for text in [ko,en]:
  assert len(text)<5000
  for link in [defaults['coaching']['url'],defaults['membershipUrl'],'https://discord.gg/wZuqe7fqkR']:assert text.count(link)==1
 (PUB/'description-beginner.ko.txt').write_text(ko.strip()+'\n',encoding='utf8');(PUB/'description-beginner.en.txt').write_text(en.strip()+'\n',encoding='utf8')
 out=dict(status='prepared-only-awaiting-reviewed-pair',preparedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),titleKo='게임의 빛은 어떻게 시작됐을까? | 기초부터 포워드·디퍼드 렌더링까지',titleEn='How Game Lighting Began: The Basics of Forward and Deferred Rendering',descriptionKo=ko.strip(),descriptionEn=en.strip(),chapters=chapters,planSha256=hashlib.sha256((O/'plan.json').read_bytes()).hexdigest(),privacy='private',schedule=None,videoId=None,baselineVideoIds=['uT5FTLJx5_c','ZUrPmDV-bSQ'],preserveBaseline=True,thumbnail=old['thumbnail'],thumbnailSha256=hashlib.sha256((R/old['thumbnail']).read_bytes()).hexdigest(),coachingCardSeconds=0,endScreenSeconds=[(plan['frames']-600)/60,plan['frames']/60],pinnedComment=old['pinnedComment'],fullSettingsVerified=False,captionedSha256=None,receipt='projects/game-lighting-history-01/publishing/youtube-receipt-beginner-v1.json',uploadComplete=False)
 wr(PUB/'upload-package-beginner-v1.json',out);print(json.dumps(dict(chapters=chapters,characters=[len(ko),len(en)],status=out['status']),ensure_ascii=False))
if __name__=='__main__':main()
