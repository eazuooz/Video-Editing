"""Selected visual-only revision; retain all prior delivery and audio evidence."""
from pathlib import Path
import json,datetime,shutil
R=Path(__file__).resolve().parents[4];V=Path(__file__).parent;P=V.parent.parent
O=P/'production/local/reference-preserving-v2/screenshots-v1';O.mkdir(parents=True,exist_ok=True)
M=R/'motion-canvas/src/projects/avoid-game-comparisons/revision-v2/screenshots';M.mkdir(exist_ok=True)
read=lambda p:json.loads(p.read_text(encoding='utf8'))
def write(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
plan=read(V/'edit-plan.json');cuts=[c for c in plan['cuts'] if c['kind']=='explanation']
for c in cuts:
 (M/(c['id']+'.tsx')).write_text("import {makeScene2D} from '@motion-canvas/2d';\nimport {screenshots} from './visuals';\nexport default makeScene2D(function*(view){yield* screenshots(view,"+json.dumps(c['visual'])+','+json.dumps({'duration':c['frames']/60,'cues':c['cues']})+");});\n",encoding='utf8')
 write(M/(c['id']+'.meta'),{'version':0,'timeEvents':[],'seed':int(c['id'][3:])+32000})
(M/'project.ts').write_text("import {makeProject} from '@motion-canvas/core';\n"+''.join(f"import s{i} from './{c['id']}?scene';\n" for i,c in enumerate(cuts))+"export default makeProject({scenes:["+','.join(f's{i}' for i in range(len(cuts)))+"]});\n",encoding='utf8')
shutil.copy2(M.parent/'production-project.meta',M/'project.meta')
request='ppt 설명 부분에 각 설명에 알맞는 스샷 같이 넣어주면 좋을거같아~'
rev={'id':'screenshots-v1','userRequest':request,'status':'design-and-preflight','scope':'Six explanation cuts only; narration, AAC, all cut frames, actual gameplay and115 KO/EN cues unchanged','renderer':'Motion Canvas','classification':'explanation','retainedRatio':'actual60:explanation40','sourceFrames':'projects/avoid-game-comparisons/production/reference-preserving-v2/screenshot-assets.json','priorCaptionedSha256':'8b372e97ae239014bafa5aef40a2c1b07910a0a2f7bdeb7e4e26d61f8e0bf9a7','sameAudioRequired':'0686ba6400fcc2f4898f0de2fae3aea69cb07a91bb211b726c644eddb0a9906d','motionCanvasProject':(M/'project.ts').relative_to(R).as_posix(),'cuts':[]}
images={'pitch':['capture'],'conditions':['pull','moon'],'rewrite':['moon','pull','break'],'retell':['capture','break'],'shared':['side-jump'],'conclusion':['moon','pull','break']}
for c in cuts:rev['cuts'].append({'cut':c['id'],'scene':c['scene'],'frames':c['frames'],'visual':c['visual'],'stills':images[c['visual']],'scenePath':(M/(c['id']+'.tsx')).relative_to(R).as_posix(),'reason':'Connect each spoken claim to the observed game object/action/result; hypothetical proposals and dialogue remain explicitly labeled','timing':c['cues'],'captionClearance':'Fixed caption region below y900; diagram main content ends below y870','marks':'Source-space verified target outlines; arrows encode narrated relationships, not measured data','sourceReview':'Eight decoded FHD stills directly inspected; all preserve source aspect; final layout pending'})
for name in ['edit-plan.json','review-ledger.json']:
 dst=O/('before-'+name)
 if not dst.exists():shutil.copy2(V/name,dst)
for file in [P/'project.json',P/'planning/chapter-plan.json',P/'production/latest-checkpoint.json']:
 dst=O/('before-'+file.name)
 if not dst.exists():shutil.copy2(file,dst)
cp=read(P/'production/latest-checkpoint.json');cp['currentRevision']['visualRevision']=rev;cp['currentRevision']['status']='screenshot-revision';cp['currentRevision']['productionComplete']=False;write(P/'production/latest-checkpoint.json',cp)
design=read(P/'planning/chapter-plan.json');design['currentRevision']['visualRevision']=rev;design['currentRevision']['nextAction']='Finish six screenshot diagrams, verify changed pixels and exact AAC, deliver revised local review master';write(P/'planning/chapter-plan.json',design)
control=read(R/'shared/publishing/video-production-control.json');assert control['selectedVideo']==P.name
control['selectedVideoRevision'].update(status='screenshot-revision',productionComplete=False,visualRevision='screenshots-v1',latestUserRequest=request)
control['selectedVideoFinalReview'].update(status='visual-revision-in-progress',userReview=None)
control['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();write(R/'shared/publishing/video-production-control.json',control)
print('Six independent editable screenshot scenes prepared; baseline retained')
