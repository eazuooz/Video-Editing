from pathlib import Path
import sys,json,os,psutil,datetime
if '--observe-live' in sys.argv:
 root=Path(__file__).resolve().parents[3]
 ep=root/'projects/game-lighting-history-04/production/part1-protected-onsets-tts-execution-v211.json'
 e=json.loads(ep.read_text('utf-8-sig'));i=e['actualIdentity'];p=psutil.Process(i['pid'])
 if abs(p.create_time()-i['createTime'])>.001 or p.cmdline()!=i['command']:raise RuntimeError('Live identity changed')
 cp=root/'production/research/game-lighting-history/checkpoint.json';c=json.loads(cp.read_text('utf-8-sig'))
 c['ownedActiveWork']={**i,'sessionId':18914,'execution':ep.relative_to(root).as_posix(),'log':'session18914 stdout','cpuThreads':2,'gpuJobs':1,'status':e['status'],'next':'Actual exit/GPU return, two complete protected ASR windows, exact lead-in removal, five final affected windows.'}
 c['episode04Part1ProtectedOnsetInitialRefusalV211']={'exitCode':1,'beforeStateOrLease':True,'reason':'Transient GPU utilization threshold rejected start. Compute-app/CIM inspection found no new research CUDA worker; later fresh utilization3% and27288MiB free allowed the actual owned lease. No bypass.'}
 c['updatedAt']=datetime.datetime.now(datetime.timezone.utc).isoformat()
 tmp=cp.with_name(cp.name+'.observe213-'+str(os.getpid()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2)+'\n','utf-8');os.replace(tmp,cp)
 print(json.dumps({'pid':i['pid'],'session':18914,'alive':True,'lease':e['leaseToken']}))
 raise SystemExit(0)
source=Path(__file__).with_name('verify-part1-onset-gpu-return-v207.py').read_text('utf-8')
source=source.replace('part1-onset-repairs-tts-execution-v199','part1-protected-onsets-tts-execution-v211').replace('part1-onset-gpu-return-v207','part1-protected-onsets-gpu-return-v213').replace('session=13934','session=18914').replace('Select35 preserved takes and these2 new takes. Recognize only the five affected whole/complete-context windows.','Recognize two protected complete utterances, review removal of the temporary prelude, then recognize the five final affected windows.')
source=source.replace("e.get('exitCode')!=0 or not e.get('endedAt') or not e.get('generationComplete')", "e.get('exitCode') not in (0,1) or not e.get('endedAt')")
source=source.replace('sessionObservedClosedExitCode=0','sessionObservedClosedExitCode=e[\'exitCode\']').replace('ttsExitCode=0','ttsExitCode=e[\'exitCode\']')
source=source.replace("allAsrApproved=False,uploaded=False)","generationExitCode=e['exitCode'],generationComplete=e['generationComplete'],tailFailurePreserved=e.get('error'),allAsrApproved=False,uploaded=False)")
exec(compile(source,str(__file__),'exec'))
