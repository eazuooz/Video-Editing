"""Read current scene exporter results; never launch, retry, stop or approve a render."""
import json,pathlib,subprocess,hashlib,datetime
R=pathlib.Path(__file__).resolve().parents[3]; P=R/'projects/game-lighting-history-01'; O=P/'production/local/explanation-assets-v1'
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
plan=read(O/'plan.json'); result=read(O/'observed.json') if (O/'observed.json').exists() else {'chapters':{},'finalVideoApproved':False,'allPixelsReviewed':False}
active=[]
for c in plan['chapters']:
 e=O/'renders'/f'{c["name"]}.execution.json'
 if not e.exists():continue
 x=read(e)
 if x['status']=='rendering':active.append({'chapter':c['id'],'execution':str(e.relative_to(R)).replace('\\','/'),**x});continue
 if x['status']!='complete' or x.get('exitCode')!=0:raise RuntimeError(f'Exporter failure preserved: {e}')
 if c['id'] in result['chapters']:continue
 f=R/c['output']; raw=subprocess.run(['C:/ProgramData/HP/LCDDisplayHelper/bin/ffprobe.exe','-v','error','-show_streams','-show_format','-of','json',str(f)],capture_output=True,text=True,check=True)
 probe=json.loads(raw.stdout);v=probe['streams'][0]
 assert len(probe['streams'])==1 and v['codec_type']=='video'
 assert int(v['nb_frames'])==c['frames'] and v['width']==1920 and v['height']==1080 and v['r_frame_rate']=='60/1' and v['time_base']=='1/90000'
 result['chapters'][c['id']]={'path':c['output'],'sha256':sha(f),'frames':int(v['nb_frames']),'durationSeconds':float(v['duration']),'fps':v['r_frame_rate'],'timeBase':v['time_base'],'exportExit':0,'metadataProbeExit':0,'fullDecode':'pending-final-pair-integrity','pixels':'pending','completedAt':x['completedAt']}
result['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat();result['active']=active;write(O/'observed.json',result)
c=read(P/'production/checkpoint.json');c['updatedAt']=result['updatedAt'];c['explanationAssetProgress']={'completedChapters':list(result['chapters']),'remainingChapters':[x['id'] for x in plan['chapters'] if x['id'] not in result['chapters']],'assetOnly':True,'observed':'projects/game-lighting-history-01/production/local/explanation-assets-v1/observed.json','finalVideoApproved':False}
c['activeOwnedHeavyJob']=({'type':'explanation-asset-render','browserTab':'89','port':9272,**active[0]} if active else None);write(P/'production/checkpoint.json',c)
print(json.dumps({'complete':list(result['chapters']),'active':[x['chapter'] for x in active],'frames':sum(x['frames'] for x in result['chapters'].values()),'finalVideo':False}))
