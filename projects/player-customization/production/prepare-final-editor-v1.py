"""Prepare an independent measured chapter review editor, without rendering."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent;W=BASE/'final-v1'
MC=ROOT/'motion-canvas/src/projects/player-customization';DEST=MC/'final-review-scenes-v1'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
plan=read(W/'plan.json');timing=read(ROOT/plan['voiceTiming']);mix=read(W/'mix-settings.json')
assert hashlib.sha256((W/'plan.json').read_bytes()).hexdigest()==mix['planSha256']
assert not DEST.exists(),'Reuse prepared final editor rather than recreate it.'
DEST.mkdir()
rows=[dict(id='00-branding',startFrame=0,frames=120),*timing['rows'],dict(id='99-membership',startFrame=35441,frames=600)]
assert sum(x['frames'] for x in rows)==36041
imports=[];names=[]
for n,row in enumerate(rows):
    path=DEST/(row['id']+'.tsx')
    path.write_text("import {finalReviewScene} from '../final-review-composite-v1';\n"+
        f"export default finalReviewScene({row['startFrame']}, {row['frames']});\n",'utf-8')
    name=f'chapter{n}';names.append(name)
    imports.append(f"import {name} from './final-review-scenes-v1/{row['id']}?scene';")
project=MC/'final-review-project-v1.ts'
project.write_text("import {makeProject} from '@motion-canvas/core';\n"+
    "import finalMix from '../../../../projects/player-customization/production/final-v1/final-mix.m4a';\n"+
    '\n'.join(imports)+"\nexport default makeProject({name:'player-customization-final-review-v1',\n"+
    '  scenes:['+','.join(names)+'],audio:finalMix});\n','utf-8')
meta=read(MC/'current-voice-white-project-v1.meta')
meta['shared']['range']=[0,36041/60];meta['rendering']['exporter']['options']['includeAudio']=True
project.with_suffix('.meta').write_text(json.dumps(meta,indent=2)+'\n','utf-8')
config=ROOT/'motion-canvas/vite.player-customization.final-review-v1.config.ts'
config.write_text("import {defineConfig} from 'vite';\nimport motionCanvasPlugin from '@motion-canvas/vite-plugin';\n"+
    "import ffmpegPlugin from '@motion-canvas/ffmpeg';\n"+
    "const motionCanvas=(motionCanvasPlugin as any).default ?? motionCanvasPlugin;\n"+
    "const ffmpeg=(ffmpegPlugin as any).default ?? ffmpegPlugin;\n"+
    "export default defineConfig({server:{host:'127.0.0.1',port:9249,strictPort:true,\n"+
    "  fs:{allow:['..']}},plugins:[ffmpeg(),motionCanvas({\n"+
    "  project:['./src/projects/player-customization/final-review-project-v1.ts'],\n"+
    "  output:'../shared/output/motion-canvas'})]});\n",'utf-8')
record=dict(schemaVersion=1,createdAt=datetime.now(timezone.utc).isoformat(),status='prepared-only-await-editor-playback-review',
    project=project.relative_to(ROOT).as_posix(),config=config.relative_to(ROOT).as_posix(),
    audioMix='projects/player-customization/production/final-v1/final-mix.m4a',audioMixSha256=mix['aacSha256'],
    editorAudioMixSameAsFinalMp4Input=True,videoSource='projects/player-customization/production/final-v1/current.silent.mp4',
    sourceVideoHasNoAudio=True,independentReviewScenes=18,narrationScenes=16,rows=rows,frames=36041,
    originalEditableExplanationScenesPreserved=True,renderStarted=False,editorAudioPlaybackObserved=False,
    allFinalCaptionPixelsReviewed=False,qaApproved=False)
(BASE/'final-editor-prepared-v1.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n','utf-8')
manifestPath=ROOT/'projects/player-customization/project.json';manifest=read(manifestPath)
manifest['paths'].update(motionCanvasProject=record['project'],audioMix=record['audioMix'],
    editorAudioMix=record['audioMix'],finalEditorPreparation='projects/player-customization/production/final-editor-prepared-v1.json')
manifestPath.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n','utf-8')
print(json.dumps(dict(prepared=True,independentScenes=18,sameFinalMix=True,editorObserved=False)))
