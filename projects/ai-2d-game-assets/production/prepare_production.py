"""Scoped, repeatable preparation. Does not touch other productions or services."""
from pathlib import Path
import json, hashlib, shutil, subprocess
P=Path(__file__).resolve().parents[1]
ROOT=P.parents[1]
T=Path('C:/Users/1/Videos/YamyamCoding/ai-2d-tools')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
content=read(P/'script/content.json')
for row in content['paragraphs']:
    if row['id']=='05':
        row['ko']=row['ko'].replace('여러 방향과 자세를 모으되,','노벨에이아이에서 만든 여러 자세와 챗지피티의 방향별 시트를 함께 모으되,')
        row['en']=row['en'].replace('Collect different views and poses,','Combine varied NovelAI poses with ChatGPT turnaround views,')
    if row['id']=='10':
        row['ko']='연결은 기본 모델과 로라에서 끝나지 않습니다. 문장을 인코딩하고, 샘플러가 잠재 이미지의 노이즈를 단계적으로 정리한 뒤, 브이에이이 디코더가 보이는 이미지로 바꿉니다. 마지막에 크기 조절과 저장을 붙입니다. 이렇게 각 단계를 나누어 두면, 마음에 드는 캐릭터는 유지하면서 축소 방식이나 팔레트만 바꿔 비교하기 쉽습니다. 캐릭터 로라는 학습한 파일이 준비되었을 때 추가합니다.'
        row['en']='The graph continues beyond the model and adapters. Text is encoded, a sampler denoises the latent, and the VAE decoder turns it into visible pixels. Resizing and saving follow. Keeping these stages separate lets you retain an image while comparing reduction methods and palettes. Add a character adapter once its trained file is available.'
write(P/'script/content.json',content)
for lang in ('ko','en'):
    write(P/f'script/narration.{lang}.json',{'scenes':[{'id':r['id'],'title':r['title'],'lines':[r[lang]]} for r in content['paragraphs']]})
m=read(P/'project.json')
m['titles']={'ko':content['titleKo'],'en':m['titleEn']}
m['engines']=['ComfyUI','PixelOE','pixelfx','Pixelbolt','Canvas 2D / FFmpeg']
m['editing']['exampleSeconds']=0
m['editing']['ratioContract']={'id':'reality-check-no-ratio-v1','reason':'Practical tool workflow: actual generated outputs, executed tools, and explicitly labeled conceptual diagrams. No unrelated gameplay quota.'}
m['audio'].update(mixStatus='narration-only-lecture',backgroundMusicEnabled=False,bgmPlacement='none',backgroundMusic={'required':False,'approvalStatus':'lecture-default-no-added-bgm','file':None})
m['paths'].update(narration=str((P/'production/local/narration/ai-2d-game-assets.wav').relative_to(ROOT)).replace('\\','/'), sources='projects/ai-2d-game-assets/planning/sources.json')
write(P/'project.json',m)
roles={
 '01':'Actual authored asset in game-like composition → identify consistency problem → preview pipeline',
 '02':'Same sprite carried through generation / processing / validation; each stage reveals its actual output',
 '03':'Full-sized original character; attached callouts on clip, jacket and bag',
 '04':'Generated four-view sheet, inspect accessories and strap; no claim of perfect consistency',
 '05':'View/pose coverage diagram; identify training inputs versus learned adapter',
 '06':'Input images → training → low-rank adapter; W + BA relationship, matrices are illustration',
 '07':'Style and identity as two separate labeled adapter paths',
 '08':'Executable Comfy API workflow redrawn from actual graph, outputs beside MODEL/CLIP connections',
 '09':'Actual same-seed Comfy output with style strength 0 and 0.8; no fabricated trained character LoRA',
 '10':'Saved graph stages with same output carried to processing',
 '11':'Actual zoomed pixel clusters, source versus logical grid',
 '12':'768x1344 and96x168 exact-size example; nearest versus actual PixelOE',
 '13':'Actual palette swatches counted from processed image, shared-palette concept',
 '14':'Real alpha over light/dark/checker backgrounds; actual contour visible',
 '15':'Outpainting process illustration over our workshop; not claimed as an executed outpaint',
 '16':'Same real processed background and sprite; pixel scale and furniture scale shown separately',
 '17':'Actual still asset versus native Pixelbolt animation; temporal criteria introduced',
 '18':'Key pose/in-between diagram with articulated original schematic figure, labeled workflow illustration',
 '19':'Video/row paths converge on actual exported atlas image and its real frame metadata',
 '20':'Actual pixelfx fire/slash/frost exports at native timing; blue fire variant uses palette only',
 '21':'Actual PixelOE before/after on our sprite/background; Pixel Snapper described, not claimed executed',
 '22':'Action/registration/loop workflow illustration; no third-party generated demo assets assumed licensed',
 '23':'Explicit skeletal principle illustration, linked tail control points; not fake Codixel execution',
 '24':'Actual original/modified Pixelbolt recipe exports; palette-only diff shown next to synchronized animation',
 '25':'Reference + ordered poses → frames: research workflow illustration, no local weight execution claimed',
 '26':'Asset-type routing with actual assets next to each route',
 '27':'Unity settings explained with actual nearest/bilinear sprite sampling and pivot guides; own compositor, not fake Unity UI',
 '28':'Real export native playback then frame steps; actual frame borders and baseline, no invented measured errors',
 '29':'Separate code/provider/model/data/output conditions beside actual asset versions',
 '30':'Same final composed workshop + sprite/effects; three conclusions inherited from body'
}
plan={'schemaVersion':1,'slug':m['slug'],'scope':m['authorization'],'thesis':content['thesis'],
 'sourceReview':{'suppliedShorts':'Both complete narrations transcribed/read; all-duration4-second contact sheets visually reviewed. Research only. All8tools retained in source order.','article':'Every paragraph of DC no214752 read; user-supplied transformation text retained. Design→dataset→adapters→Comfy→pixel processing→background→animation remains coherent.','corrections':['LoRA is a learned low-rank adapter, not dataset','8x and background3x are case-specific, not universal','20–50images is an editorial starting point','SakuLike model page mentions embedded example-image workflow; no universal no-JSON claim','Code license does not cover all provider/model/data terms']},
 'rendererDecision':{'renderer':'Canvas2D via @napi-rs/canvas + FFmpeg, actual tool exports','reason':'Preserve exact nearest pixels/alpha/atlas frame timing and display executable procedural outputs without resampling through an engine; illustrations are explicitly labeled. No duplicate engine scene.','width':1920,'height':1080,'fps':60,'palette':'research-black-v1','captionCenter':[960,970],'captionPx':48,'mobileWidth':375},
 'audio':{'voice':'Qwen3-TTS12Hz1.7BBase approved reference15–35s','takes':'one complete paragraph per scene; no sentence fragmentation','sceneGap':0.28,'paragraphMedianDbfs':-22,'mixLufs':-16,'bgm':'none per lecture default','humanWholeListening':'pending'},
 'footageClassification':{'finishedReferencesInCut':False,'actualCommercialGameplay':0,'scope':'Tool/tutorial workflow, no fixed actual/explanation ratio; show actual executable results and label other diagrams.'},
 'trainingStatus':'No character LoRA training executed; do not label an invented file or identity claim as a tested result.',
 'scenes':[]}
for i,r in enumerate(content['paragraphs']):
    plan['scenes'].append({'id':r['id'],'title':r['title'],'sourceSection':('user guide' if i<17 else 'supplied shorts tool'+str(i-16) if i<25 else 'workflow synthesis'),
      'retainedNarration':r['ko'],'screen':roles[r['id']],'renderer':'actual exports + Canvas2D composition','hold':0,
      'speechVisual':'Reveal object/action/result during the corresponding spoken sentence; use synthesized sentence boundaries when available.',
      'incomingLink':content['paragraphs'][i-1]['title'] if i else '2-second approved branding → actual asset result',
      'outgoingLink':content['paragraphs'][i+1]['title'] if i+1<len(content['paragraphs']) else 'original membership ending10s',
      'captionClearance':'All substantive graphics above y880; fixed caption center970;1080p and375px inspection required'})
write(P/'planning/production-plan.json',plan)
write(P/'planning/terminology.json',{'ComfyUI':'컴피유아이','LoRA':'로라 / Low-Rank Adaptation (저랭크 적응)','Illustrious XL':'일러스트리어스 엑스엘','PixelArt SakuLike ILXL':'픽셀아트 사쿠라이크 일러스트리어스','PixelOE':'픽셀 오이','pixelfx':'픽셀 에프엑스','Pixelbolt':'픽셀볼트 (formerly PixelForge)','Codixel':'코디셀','Alpha':'알파 / 투명도','Palette Quantization':'색상 수 제한','Outpainting':'배경 확장','Pixels Per Unit':'픽셀 퍼 유닛','Pivot':'피벗 / 기준점'})
md=['# 전체 대본 · AI 2D 게임 리소스','',content['titleKo'],'','> 현지 제작 검수용. 플랫폼 업로드 승인 아님.']
for r in content['paragraphs']:
    md += ['',f"## {r['id']} · {r['title']}",'',r['ko'],'',f"화면: {roles[r['id']]}"]
(P/'script/full-script.md').write_text('\n'.join(md)+'\n',encoding='utf-8')
print('Prepared',len(plan['scenes']),'mapped paragraphs')
