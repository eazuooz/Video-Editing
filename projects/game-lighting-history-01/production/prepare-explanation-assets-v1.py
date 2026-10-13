"""Freeze reusable, speech-timed explanation assets, not a final episode.

The final interleaving/ratio gates remain in final/runtime.tsx and timing.ts.
These independent scene assets preserve the entire existing paragraph envelope;
the editor may retain decoded-equivalent subranges without rendering them again.
"""
import hashlib,json,pathlib,datetime
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'projects/game-lighting-history-01'
DST=ROOT/'motion-canvas/src/projects/game-lighting-history-01/explanation-assets-v1'
OUT=P/'production/local/explanation-assets-v1'
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,v): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
plan=read(P/'planning/production-plan.json')
voice=read(P/'production/current-voice-direct-review-v4.json')
story=read(P/'production/animation-storyboard-v4.json')
pcm=ROOT/'shared/output/narration/game-lighting-history-01/qwen3-1.7b-balanced-v4/game-lighting-history-01-qwen3-1.7b-balanced-v4.wav'
assert sha(pcm)==plan['preservedAudioSha256']==voice['audioSha256']
assert voice['all26WindowsDirectlyCompared'] and voice['structuralContentCoverageReviewed']
anchors={x['paragraphKey']:x for x in plan['speechMotionDesign']['entries']}
rows={x['paragraphKey']:x for x in plan['visualAllocation']['rows']}
assert len(anchors)==len(rows)==108
assert not (OUT/'plan.json').exists(), 'Preserve existing rendered asset plan; inspect it instead.'
DST.mkdir(exist_ok=True); (OUT/'renders').mkdir(parents=True,exist_ok=True)
chapters=[]
for scene in story['scenes']:
    blocks=[]
    for paragraph in scene['paragraphs']:
        key=paragraph['key']; row=rows[key]; anchor=anchors[key]
        assert anchor['model']==paragraph['model'] and anchor['textAndWordAnchorsDirectlyCompared']
        previous=0
        for step in anchor['actionSteps']:
            assert step['actionStartFrame']>=previous and step['actionDurationFrames']>0 and step['spokenTrigger']
            previous=step['actionStartFrame']+step['actionDurationFrames']
            assert previous<=row['frames']
        blocks.append({**{k:row[k] for k in ['paragraphKey','pcmStartFrame','pcmEndFrame','frames']},'actionSteps':anchor['actionSteps']})
    frames=sum(x['frames'] for x in blocks); name='explanation-'+scene['id']
    chapters.append({'id':scene['id'],'title':scene['title'],'frames':frames,'pcmStartFrame':blocks[0]['pcmStartFrame'],'pcmEndFrame':blocks[-1]['pcmEndFrame'],'blocks':blocks,'name':name,'output':f'projects/game-lighting-history-01/production/local/explanation-assets-v1/renders/{name}.mp4'})
    (DST/f'scene-{scene["id"]}.tsx').write_text("import {explanationAssetScene} from './runtime';\nexport default explanationAssetScene('"+scene['id']+"');\n",encoding='utf-8')
    (DST/f'{name}.ts').write_text("import {makeProject} from '@motion-canvas/core';\nimport scene from './scene-"+scene['id']+"?scene';\nexport default makeProject({scenes:[scene]});\n",encoding='utf-8')
    write(DST/f'{name}.meta',{'version':0,'shared':{'background':None,'range':[0,(frames-1)/60],'size':{'x':1920,'y':1080},'audioOffset':0},'preview':{'fps':30,'resolutionScale':1},'rendering':{'fps':60,'resolutionScale':1,'colorSpace':'srgb','exporter':{'name':'@motion-canvas/ffmpeg','options':{'fastStart':True,'includeAudio':False}}}})
data={'schemaVersion':1,'scope':'independent-explanation-assets-only','voiceSha256':voice['audioSha256'],'all26VoiceWindowsCompared':True,'paragraphs':108,'steps':sum(len(x['actionSteps']) for x in anchors.values()),'chapters':chapters,'finalTimelineApproved':False,'bodyRatioApproved':False,'finalVideoApproved':False}
write(DST/'data.json',data)
source=(ROOT/'motion-canvas/src/projects/game-lighting-history-01/final/runtime.tsx').read_text(encoding='utf-8')
source=source.replace("from './black-models-v2'","from '../final/black-models-v2'").replace("import {PLAN} from './timing';","import data from './data.json';")
source=source.replace("export function episodeScene(id:string)","export function explanationAssetScene(id:string)")
source=source.replace(" const timing=PLAN?.scenes[id];\n if(!PLAN||!timing||!PLAN.all26WindowsDirectlyCompared||!PLAN.bodyRatioApproved)throw new Error('Final narration/native interleaving has not been reviewed. Do not render final scenes yet.');", " const timing=data.chapters.find(c=>c.id===id);\n if(!timing||data.scope!=='independent-explanation-assets-only'||!data.all26VoiceWindowsCompared||data.paragraphs!==108)throw new Error('Speech-timed asset input missing');")
source=source.replace("const steps=block.actionSteps??[{actionStartFrame:block.actionStartFrame,actionDurationFrames:block.actionDurationFrames,spokenTrigger:block.spokenTrigger,to:action.to}];","const steps=block.actionSteps;")
source=source.replace('timing.explanationFrames','timing.frames')
assert 'PLAN' not in source
(DST/'runtime.tsx').write_text(source,encoding='utf-8')
config=(ROOT/'motion-canvas/vite.game-lighting-history-01.preflight-v7.config.ts').read_text(encoding='utf-8')
config=config.replace('game-lighting-history-01-preflight-v7-cpu','game-lighting-history-01-explanation-assets-v1-cpu').replace('port:9271','port:9272')
config=config.replace("const record=fileURLToPath(new URL('../projects/game-lighting-history-01/production/local/preflight-v7/execution.json',import.meta.url));", "const filename=path.basename((this as any).command._outputs[0].target).replace(/\\.mp4$/,'.execution.json');\n const record=fileURLToPath(new URL('../projects/game-lighting-history-01/production/local/explanation-assets-v1/renders/'+filename,import.meta.url));")
config=config.replace("project:['./src/projects/game-lighting-history-01/preflight-v7/project.ts']",'project:'+json.dumps(['./src/projects/game-lighting-history-01/explanation-assets-v1/'+x['name']+'.ts' for x in chapters]))
config=config.replace("output:'../projects/game-lighting-history-01/production/local/preflight-v7'","output:'../projects/game-lighting-history-01/production/local/explanation-assets-v1/renders'")
(ROOT/'motion-canvas/vite.game-lighting-history-01.explanation-assets-v1.config.ts').write_text(config,encoding='utf-8')
write(OUT/'plan.json',{**data,'createdAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),'inputHashes':{str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [P/'planning/production-plan.json',P/'production/animation-storyboard-v4.json',P/'production/current-voice-direct-review-v4.json',DST/'data.json',DST/'runtime.tsx',ROOT/'motion-canvas/src/projects/game-lighting-history-01/final/black-models-v2.tsx',ROOT/'motion-canvas/src/projects/game-lighting-history-01/final/depth-space-v3.tsx']},'humanListening':'pending','finalMixAsr':'pending','nativeInterleaving':'pending'})
print(json.dumps({'chapters':len(chapters),'frames':sum(x['frames'] for x in chapters),'paragraphs':108,'steps':data['steps'],'finalGatesUnchanged':True}))
