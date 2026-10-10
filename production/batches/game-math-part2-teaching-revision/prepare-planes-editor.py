"""Independent Motion Canvas scenes and editable matching fixed captions."""
from pathlib import Path
import json,argparse
from PIL import ImageFont
ROOT=Path(__file__).resolve().parents[3]
parser=argparse.ArgumentParser();parser.add_argument('slug',choices=['game-math-plane-distances-v2','game-math-triangle-addresses-v2']);args=parser.parse_args()
P=ROOT/'projects'/args.slug;M=ROOT/'motion-canvas/src/projects'/args.slug
plan=json.loads((P/'production/timeline.json').read_text(encoding='utf8'));font=ImageFont.truetype('C:/Windows/Fonts/malgun.ttf',48)
layouts=[]
for cue,c in enumerate(plan['koCaptions'],1):
 lines=c['text'].splitlines();assert len(lines)<=2
 width=round(max(font.getlength(s) for s in lines)+44);height=len(lines)*62+22;x=round(960-width/2);y=round(970-height/2)
 assert width<=1614 and y+height+14<=1080
 layouts.append({'cue':cue,'scene':c['scene'],'start':c['start'],'end':c['end'],'text':c['text'],'box':[x,y,width,height],'center':[960,970],'shadow':[14,14]})
def write(p,text):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8')
write(M/'caption-layout.json',json.dumps(layouts,ensure_ascii=False,indent=2)+'\n')
helper=f'''import {{Video,View2D,Node,Rect,Txt}} from '@motion-canvas/2d';
import {{waitFor}} from '@motion-canvas/core';
import plan from '../../../../../projects/{args.slug}/production/timeline.json';
import captions from '../caption-layout.json';
class SilentVideo extends Video {{protected override video(){{const v=super.video();v.muted=true;return v;}}}}
export function* playScene(view:View2D,src:string,id:string) {{
  view.fill('#ffffff');const video=new SilentVideo({{src,width:1920,height:1080}});
  view.add(video);yield video;video.play();
  const slot=plan.scenes.find(s=>s.id===id);
  const seconds=id==='intro'?2:id==='outro'?10:slot!.seconds;
  let elapsed=0;
  for(const cue of captions.filter(c=>c.scene===id)){{
    const start=cue.start-slot!.start,end=cue.end-slot!.start;
    yield* waitFor(Math.max(0,start-elapsed));
    const [x,y,w,h]=cue.box;const layer=new Node({{}});
    layer.add(new Rect({{x:x+w/2-960+14,y:y+h/2-540+14,width:w,height:h,fill:'#073c32',radius:0}}));
    layer.add(new Rect({{x:x+w/2-960,y:y+h/2-540,width:w,height:h,fill:'#161b18',radius:0}}));
    layer.add(new Rect({{x:x+w/2-960,y:y+h/2-540,width:w-6,height:h-6,fill:'#ffffff',radius:0}}));
    layer.add(new Txt({{x:0,y:430,text:cue.text,fontFamily:'Malgun Gothic',fontSize:48,lineHeight:62,fill:'#090b08',textAlign:'center'}}));
    view.add(layer);yield* waitFor(Math.max(0,end-start));layer.remove();elapsed=end;
  }}
  yield* waitFor(Math.max(0,seconds-elapsed));video.pause();video.remove();
}}
'''
write(M/'scenes/play-clip.tsx',helper)
imports=["import {makeProject} from '@motion-canvas/core';","import audio from './assets/final-mix.wav';"]
names=[]
for ident,name in [('intro','brand-intro'),*[(s['id'],'scene'+s['id']) for s in plan['scenes']],('outro','membership-outro')]:
 variable='s'+ident;imports.append(f"import {variable} from './scenes/{name}?scene';");names.append(variable)
 write(M/f'scenes/{name}.tsx',f"import {{makeScene2D}} from '@motion-canvas/2d';\nimport clip from '../assets/{ident}.mp4';\nimport {{playScene}} from './play-clip';\nexport default makeScene2D(function* (view){{yield* playScene(view,clip,'{ident}');}});\n")
write(M/'project.ts','\n'.join(imports)+f"\nexport default makeProject({{name:'{args.slug}',audio,scenes:[{','.join(names)}]}});\n")
write(M/'timing.ts',f'export const NARRATION_FPS=60;\nexport const TOTAL_FRAMES={plan["frames"]};\nexport const TOTAL_DURATION={plan["seconds"]};\n')
catalog=ROOT/'motion-canvas/projects.json';paths=json.loads(catalog.read_text(encoding='utf8'));entry=f'./src/projects/{args.slug}/project.ts'
if entry not in paths:paths.append(entry);write(catalog,json.dumps(paths,ensure_ascii=False,indent=2)+'\n')
write(P/'production/editor-record.json',json.dumps({'independentScenes':len(names),'captionStyle':'boxed-white-forest-v1','captionCenter':[960,970],'captionCueCount':len(layouts),'audio':'one final narration-only stereo mix','editableSources':['production/timeline.json','script/final.ko.ass',f'motion-canvas/src/projects/{args.slug}/caption-layout.json','production/batches/game-math-part2-teaching-revision/planes-annotation-tracks.json','manim/projects/game-math-part2-teaching-revision'],'actualEditorPlaybackReview':False},ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'scenes':len(names),'editableCaptionCues':len(layouts),'editorPlaybackApproval':False}))
