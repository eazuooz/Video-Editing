"""Additional candidate comparison; retain completed v4 and baseline evidence."""
exec((__import__('pathlib').Path(__file__).with_name('review-polar-unused-actions-v4.py')).read_text(encoding='utf-8').split('source=ROOT/')[0])
source=ROOT/'shared/output/game-math-polar-lecture/sources/WJVRoLR6KvY.mp4'
folder=LOCAL/'unused-native-v5';folder.mkdir(parents=True,exist_ok=True)
windows=[(88,110),(400,430)]
frames=sorted({s*60 for a,b in windows for s in range(a,b)})
statefile=OUT/'unused-native-execution-v5.json';assert not statefile.exists()
state={'startedAt':datetime.now(timezone.utc).isoformat(),'pid':os.getpid(),'createTime':psutil.Process().create_time(),'commandLine':psutil.Process().cmdline(),'cwd':str(ROOT),'cpuThreads':2,'gpuJobs':0,'status':'running','sourceSha256':sha(source),'nativeTimebase':'1/15360','nativeStep':256,'windows':windows,'plannedNativeFrames':frames,'selectionApproved':False,'finalPixelsApproved':False}
exec((__import__('pathlib').Path(__file__).with_name('review-polar-unused-actions-v4.py')).read_text(encoding='utf-8').split('def save():',1)[1].join(['def save():','']))
