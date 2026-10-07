"""Persist the actual blocked UI action without inventing a video ID or repeating the upload."""
from pathlib import Path
import json,datetime
ROOT=Path(__file__).resolve().parents[3];batch=ROOT/'production/batches/visual-depth-revision'
read=lambda p:json.loads(p.read_text('utf-8-sig'))
write=lambda p,v:p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n','utf-8')
block=dict(observedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='browser-upload-permission-denied',action='Upload reviewed output/picking-sides/picking-sides.captioned.mp4 to the existing YouTube Studio channel as a new private correction',surface='https://studio.youtube.com/video/NLEHMC0XMtg/edit',toolResult='Browser security policy rejected fileChooser.setFiles because the user declined permission for the file upload request.',fileSent=False,actualNewVideoId=None,workaroundAttempted=False,modalClosed=True,requiredInput='Allow this YouTube file upload action before private reupload can resume',localProductionCanContinue=True)
write(batch/'private-reupload-block.json',block)
qpath=batch/'queue.json';q=read(qpath);q['privateUploadBlock']='production/batches/visual-depth-revision/private-reupload-block.json';q['localPipelineSessionId']=25661
item=next(i for i in q['items'] if i['slug']=='picking-sides');report=read(ROOT/'projects/picking-sides/production/delivery-output.json');qa=read(ROOT/'projects/picking-sides/production/visual-depth-v1/pair-technical-qa.json')
for o in qa['outputs']:
 if next(f for f in report['files'] if f['name']=='picking-sides.'+o['variant']+'.mp4')['sha256']!=o['sha256']:raise RuntimeError('Collected file does not match current reviewed pair')
item.update(stage='reviewed-collected-private-reupload-blocked',collected=True,collectionReport='projects/picking-sides/production/delivery-output.json',uploaded=False,newVideoId=None,uploadBlock=q['privateUploadBlock'])
motion=next(i for i in q['items'] if i['slug']=='motion-sickness-games');motion.update(stage='single-cpu-white-render-in-progress',sessionId=70710,pipelineExecution='production/batches/visual-depth-revision/local-review-pipeline-execution.json',pipelineSessionId=25661,execution='projects/motion-sickness-games/production/visual-depth-v1/white-cpu-execution.json')
write(qpath,q)
mPath=ROOT/'projects/picking-sides/project.json';m=read(mPath);m['visualDepthRevision'].update(status='reviewed-collected-private-reupload-blocked',collected=True,uploadBlock=q['privateUploadBlock'],privateUploadCompleted=False);write(mPath,m)
print('Observed upload denial and exact collected pair recorded; new video ID/upload/Git remain incomplete')
