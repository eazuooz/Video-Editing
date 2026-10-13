"""One additive Qwen batch with the existing cooperative GPU guard/reference."""
import pathlib,json,hashlib,sys,runpy,datetime,os,traceback
R=pathlib.Path(__file__).resolve().parents[3];P=R/'projects/game-lighting-history-01'
def rd(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
review=rd(P/'production/native-guide-design-v1.json')
assert review['fullKoEnDirectRead'] and review['original108Preserved']
for lang in ['ko','en']:
 assert sha(P/f'script/native-guides-v1.{lang}.json')==review['guideHashes'][lang]
 assert sha(P/f'script/narration.{lang}.json')==review['originalScriptHashes'][lang]
control=rd(R/'shared/publishing/video-production-control.json')
assert control['mode']=='one-video-autonomous-until-private-upload'
assert rd(P/'production/checkpoint.json')['publishingAuthorization']['privateUploadForMobileReview']
assert '--manifest' in sys.argv and sys.argv[sys.argv.index('--manifest')+1]=='projects/game-lighting-history-01/production/native-guides-v1.project.json'
# Existing entrypoint validates current inventory and obtains/relinquishes the
# owned GPU lease. Unchanged original108 are checked, never regenerated here.
ns=runpy.run_path(str(P/'production/render-voice.py'),run_name='native_guides_shared_configuration')
if '--dry-run' in sys.argv:
 ns['render_narration'].main();raise SystemExit(0)
import psutil
out=P/'production/local/native-guides-v1';out.mkdir(parents=True,exist_ok=True)
state=dict(status='running',startedAt=now(),pid=os.getpid(),createTime=psutil.Process().create_time(),command=psutil.Process().cmdline(),gpuJobs=1,cpuThreads=2,scriptHashes=review['guideHashes'],original108PcmRegenerated=False,guideCount=len(review['rows']),completedGuides=[],controlSha256=sha(R/'shared/publishing/video-production-control.json'),humanListening='pending')
def save():
 (out/'execution.json').write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
save()
ck=rd(P/'production/checkpoint.json');ck.update(updatedAt=now(),stage='native-observation-guide-tts',activeOwnedHeavyJob=dict(kind='native-guide-TTS',pid=state['pid'],createTime=state['createTime'],command=state['command'],execution='projects/game-lighting-history-01/production/local/native-guides-v1/execution.json',gpuJobs=1),nextAction='Finish additive guide batch, compare its actual full ASR, bind measured guide PCM into native slots; preserve original108 and all13completed explanation assets.')
(P/'production/checkpoint.json').write_text(json.dumps(ck,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
try:
 ns['render_narration'].main()
 state.update(status='complete',completedAt=now(),exitCode=0)
except BaseException as e:
 state.update(status='failed',completedAt=now(),error=repr(e));raise
finally:
 chunks=R/'shared/output/narration/game-lighting-history-01/native-guides-v1/chunks'
 state['completedGuides']=[p.stem for p in sorted(chunks.glob('g*-scene.wav'))]
 save()
