"""Adapt the audited serial input/ASS sampler to this measured37-paragraph plan."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3];BASE=Path(__file__).resolve().parent
old=ROOT/'projects/presenting-game-scores/production/build-selected-input-preflight-v8.py'
new=BASE/'build-selected-input-preflight-v3.py';assert not new.exists()
text=old.read_text('utf-8')
replacements=[
 ('presenting-game-scores','character-parameters'),('selected-inputs-v8','selected-inputs-v3'),('selected-input-preflight-execution-v8','selected-input-preflight-execution-v3'),
 ('measured-timeline-candidate-v7','measured-timeline-candidate-v3'),('caption-candidate-v8','caption-candidate-v4'),('measured-native-inputs-execution-v8','measured-native-inputs-execution-v3'),
 ("black=read(BASE/'measured-black-input-verification-v8.json');native=read(BASE/'measured-native-inputs-execution-v3.json')\nassert black['frames']==7334 and black['plannedSegmentFrames']==7333 and black['wholeDecodeExitCode']==0",
  "export=read(BASE/'measured-black-export-execution-v3.json');native=read(BASE/'measured-native-inputs-execution-v3.json')\nassert export['exitCode']==0 and export['childExited']\nblack=dict(videoPath=export['output'],videoSha256=export['outputSha256'])"),
 ("assert native['exitCode']==0 and len(native['results'])==12","assert native['exitCode']==0 and len(native['results'])==24"),
 ("assert cap['koCueCount']==168 and cap['enCueCount']==68 and cap['allLiteralKoEn39ParagraphsPreserved']","assert cap['koCueCount']==201 and cap['enCueCount']==95 and cap['allCurrent37KoEnParagraphsRetained']"),
 ('totalBlackSegments=12','totalBlackSegments=17'),('total=12','total=17'),('7333','9071'),('18332','22677'),('18331','22676'),('10999','13606'),
 ("assert black_cursor==9071 and len(s['segments'])==24","assert black_cursor==9071 and len(s['segments'])==41"),
 ("f'trim=start_frame={a}:end_frame={b},setpts=N/(60*TB),setsar=1'","f'trim=start_frame={a}:end_frame={b},settb=1/90000,setpts=N*1500,setsar=1,setparams=range=limited:color_primaries=bt709:color_trc=bt709:colorspace=bt709'"),
 ("for chunk in cap['chunks']:sample(math.ceil((chunk['startSeconds']-2)*60)+1,dict(kind='complete-clause-onset',scene=chunk['scene'],paragraph=chunk['paragraph'],chunk=chunk['chunk']))",
  "for para in cap['paragraphs']:\n  onset=min(c['startSeconds']for c in cap['ko']if (c['scene'],c['paragraph'])==(para['scene'],para['paragraph']))\n  sample(math.ceil((onset-2)*60)+1,dict(kind='complete-paragraph-onset',scene=para['scene'],paragraph=para['paragraph']))"),
 ('all168CuesCovered=True,all24CutsCovered=True,all12BlackMotionSegmentsCovered=True','all201CuesCovered=True,all41CutsCovered=True,all17BlackMotionSegmentsCovered=True'),
 ('cues=168,cuts=24,blackSegments=12','cues=201,cuts=41,blackSegments=17'),('inputs=24,bodyFrames=22677,ko=168,en=68','inputs=41,bodyFrames=22677,ko=201,en=95'),
 ("BASE/'selected-input-preflight-v8.json'","BASE/'selected-input-preflight-v3.json'"),('schemaVersion=8','schemaVersion=3'),
 ('Before each current cue/motion/UI','Before each current cue/motion/UI')]
for a,b in replacements:
 if a==b:continue
 assert a in text,(a,'Missing audited adaptation target');text=text.replace(a,b)
text=text.replace("checkpoint();black_cursor=0;nb={x['id']:x for x in native['results']}","""checkpoint()
 raw_probe=probe(ROOT/black['videoPath'],9072)
 raw_pts=json.loads(run(FP,['-v','error','-select_streams','v:0','-show_frames','-show_entries','frame=best_effort_timestamp','-of','json',ROOT/black['videoPath']],'all-raw-black-pts'))['frames']
 assert [int(v['best_effort_timestamp'])for v in raw_pts]==list(range(0,9072*1500,1500))
 ff(['-i',ROOT/black['videoPath'],'-f','null','-'],'whole-raw-black-decode')
 save(BASE/'measured-black-input-verification-v3.json',dict(videoPath=black['videoPath'],videoSha256=black['videoSha256'],frames=9072,plannedSegmentFrames=9071,probe=raw_probe,allPtsVerified=True,wholeDecodeExitCode=0,actualExportExitCode=export['exitCode'],scope='Current raw measured silent black input. No final animated/caption/pair approval.'))
 black_cursor=0;nb={x['id']:x for x in native['results']}""")
assert '7333'not in text and '18332'not in text and "cap['chunks']"not in text
new.write_text(text,'utf-8')
resource=(BASE/'capture-current-resource-v5.ps1').read_text('utf-8')
resource=resource.replace('review-additional-role-action-v2.py','review-additional-role-action-v2.py|build-measured-native-inputs-v3.py|build-selected-input-preflight-v3.py|build-character-final-mix-v1.py|review-character-mixed-v1.py|render-character-pair-v1.py|extract-character-final-qa-v1.py')
resource=resource.replace('capture-current-resource-v5','capture-current-resource-v6')
(BASE/'capture-current-resource-v6.ps1').write_text(resource,'utf-8')
(BASE/'selected-input-worker-preparation-v3.json').write_text(json.dumps(dict(source=str(old.relative_to(ROOT)).replace('\\','/'),sourceSha256=hashlib.sha256(old.read_bytes()).hexdigest(),worker=str(new.relative_to(ROOT)).replace('\\','/'),workerSha256=hashlib.sha256(new.read_bytes()).hexdigest(),inputs=41,actualCuts=24,blackCuts=17,koCues=201,enCues=95,preparedOnly=True,executed=False,finalTimingApproved=False),indent=2)+'\n','utf-8')
print('Prepared serial41 input and current201-cue ASS sample worker; no execution or approval.')
