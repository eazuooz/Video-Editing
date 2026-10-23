from common import *
import runpy
# Publishing drafts only: no platform mutation.
en_titles={
'game-math-camera-frustum':['Four questions about the camera','Two views of the same game','Where the image is stored and displayed','Image aspect and pixel aspect','Editing a building versus changing the observer','The camera view is a volume','Six clipping planes','Orbiting a completed building','What field of view measures','Calculating a two-times zoom','Character size and visible space','Relating horizontal and vertical fields of view','Following the same roof through a zoom','Does moving forward double every object?','Field of view from lens and sensor','Tracking the near door and distant roof','Parallel rays in orthographic projection','Zoom from the orthographic box size','From a nearby castle to surrounding towers','What to preserve in two player views','Record construction and observation separately','Review: view volume, zoom and viewport'],
'game-math-camera-projection':['From a point to a pixel','Stationary pillars and a moving observer','Four conventions before calculation','Placing a local point in the world','Existing roof points and newly created points','Coordinates relative to the camera','The matrix prepares w; division comes later','The same tower, altered platform and viewpoint','Substituting values into the perspective matrix','Testing six boundaries before division','Cube placement versus camera movement','A triangle crossing the near plane','Writing the scene with different conventions','A new roof versus occlusion','Divide by w and map to the viewport','Complete the screen-coordinate calculation'],
'game-math-projection-depth':['Why depth and w still matter after division','Depth 0.825 is not distance 0.825','A near building hides a distant railing','Texture attributes must remember w','Projection-plane distance and matrix scale','Roof patterns and perspective-correct interpolation','Which steps does the GPU perform?','Work a new numerical example','Following reference points on the same terrace','Complete the journey of one point']}
for slug,titles in en_titles.items():
 P=R/'projects'/slug;H=P/'production/concept-fit-v2';T=read(H/'timeline.json');D=P/'publishing/revisions/concept-fit-v2';D.mkdir(parents=True,exist_ok=True);assert len(titles)==len(T['scenes'])
 if slug.endswith('projection-depth'):
  intros={'ko':'같은 화면 위치에 겹친 두 표면 중 무엇이 보일까요? 건축 장면의 앞뒤 가림과 지붕 무늬를 관찰하며 깊이, 원근 보정 보간, 클립 좌표의 w를 작은 계산으로 연결합니다.','en':'Which surface appears when two surfaces overlap on screen? Connect building occlusion and roof patterns to depth, perspective-correct interpolation and clip-space w through small calculations.'}
  for lang in ['ko','en']:
   old=(R/f'projects/game-math-polygon-partition-v2/publishing/upload-description.{lang}.txt').read_text(encoding='utf8');footer='🎮'+old.split('🎮',1)[1]
   note='게임 위 표식은 설명용 안내이며 내부 좌표나 측정값이 아닙니다. 별도 배경음악은 추가하지 않았습니다.' if lang=='ko' else 'Game overlays are editorial guides, not measurements of internal coordinates. No separate background music was added.'
   rows=[]
   for i,s in enumerate(T['scenes']):
    n=int(0 if i==0 else s['start']);rows.append(f'{n//60:02}:{n%60:02} '+(s['title'] if lang=='ko' else titles[i]))
   n=int(T['seconds']-10);rows.append(f'{n//60:02}:{n%60:02} '+('멤버십 감사와 코칭 안내' if lang=='ko' else 'Membership thanks and programming coaching'))
   credits='\n\n'+('게임 화면 출처' if lang=='ko' else 'Gameplay sources')+'\nTownscaper — independent gameplay recording\nhttps://www.youtube.com/watch?v=FRfnXAIbA-M\nTiny Glade — Pounce Light official trailer\nhttps://pouncelight.games/tiny-glade/\n'
   (D/f'upload-description.{lang}.txt').write_text(intros[lang]+'\n\n'+note+'\n\n'+'\n'.join(rows)+'\n\n'+footer.rstrip()+credits,encoding='utf8')
 else:
  p=D/'upload-description.en.txt';lines=p.read_text(encoding='utf8').splitlines();i=0
  import re
  for j,line in enumerate(lines):
   if re.match(r'^\d{2}:\d{2} ',line) and i<len(titles):lines[j]=line.split(' ',1)[0]+' '+titles[i];i+=1
  assert i==len(titles);p.write_text('\n'.join(lines)+'\n',encoding='utf8')
 save(H/'description-drafts.json',dict(status='local drafts only',files=[dict(path=rel(x),sha256=sha(x)) for x in D.glob('*.txt')],creditsAtBottom=True,englishChapterTitlesVerified=True,uploadAuthorized=False))
# The failed new07 render never completed; keep all unaffected successful clips.
H=R/'projects/game-math-mesh-uv/production/concept-fit-v2';f=H/'render-progress.json';r=read(f);old=r['identity'];assert '07' not in r['scenes']
r['identity']=hashlib.sha256((sha(B/'m19-scenes.py')+sha(B/'m18-scenes.py')+sha(B/'m16-scenes.py')+sha(B/'m03-scenes.py')+sha(H/'timeline.json')).encode()).hexdigest();r.update(state='ready-to-resume',updatedAt=now());save(f,r)
save(H/'projection-variable-repair.json',dict(checkedAt=now(),oldIdentity=old,newIdentity=r['identity'],reason='The scalar normal-interpolation coordinate shadowed the camera-up vector in scene07. Renamed that local scalar; no other geometry/audio changed.',nextAction='Resume unfinished scenes after the currently running voice job finishes.'))
sourceplay=dict(checkedAt=now(),tool='cua_repl local tabs77/79',rate=1,segments=[(34,39.044825),(56,59.147046),(46,53.115373),(600,607.201623),(28,31.191824),(76,85.237879),(30,35.045975),(94,99.256342),(666,670.239748),(41,47.11349),(52,56.250447)],nativePlaybackCompleted=True,continuousHumanViewing=False,actualListening=False,directFrames='128 coarse,96 selected and31 additional frames inspected separately; playback alone is not a human viewing/listening claim.')
save(B/'m19-m20-source-playback.json',sourceplay)
e=read(H/'source-evidence.json');e.update(nativePlayback=rel(B/'m19-m20-source-playback.json'),directReview='All128 coarse/11sheets,96 selected/8sheets and31 extra/3sheets directly inspected. Short object/structure windows selected; native1x playback complete, actual listening not claimed.',purposefulReuse='SE2 angular-module window overlaps a prior quaternion example; here the narrated observation is silhouette versus panel brightness. Big Walk recap returns to a different wall-hole interval to separate geometry from shading. No generic walking filler.')
for s in e['sources']:
 if s['key']=='launch':s['url']='https://mirror.keenswh.com/PressKits/SE2%20Press%20Kit.zip'
save(H/'source-evidence.json',e)
print('M18 metadata, English chapter drafts, source-playback evidence and M19 repair checkpoint saved')
