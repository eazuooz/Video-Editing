"""Record the full76-paragraph direct source-text review; no audio repair."""
from pathlib import Path
import difflib,importlib.util,json
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_content_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
s=importlib.util.spec_from_file_location('v8_content_analysis',H/'voice-analysis.py');v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
CONTEXT={
 ('m03',2):'Whole-source ASR wrote 물체부터 instead of 물체에 붙어. Object-attached-frame relation needs complete-context clarification.',
 ('m05',3):'Whole-source ASR wrote coordinate2,0,-2 instead of2,0,-1 and omitted initial 지금. Critical number is not normalized to the expected value.',
 ('m07',2):'Whole-source ASR wrote1분의2 instead of 이분의일. Reciprocal values are not treated as spelling equivalents.',
 ('m08',7):'Whole-source ASR wrote 전체 rather than canonical 전치. Inspect complete paragraph.',
 ('m09',2):'Whole-source ASR wrote3개공간 instead of 세계공간. Inspect actual frame-name context.',
 ('m09',7):'Whole-source ASR omitted 바깥으로 before 바깥에서. Inspect complete bidirectional-conversion clause.',
 ('m13',3):'Whole-source ASR wrote 전체 rather than 전치 in inverse summary.',
 ('m13',4):'Whole-source ASR wrote 대체 rather than 대신자세 at memory-cost summary opening.'}
SCENE_NOTES={
 'm01':'Direction versus full orientation, bank and three independent changes preserved. Native/Arabic numeral spelling differs only.',
 'm02':'Reference/home/identity posture, angular displacement versus state, Y-up/east+X/north+Z and quarter-turnaboutY all present. attitude is Latin readback.',
 'm03':'Object/upright frames, common origin, position separated, three basis rows and row-vector convention present. 같게/갖게 and 세/새 are phonetic spelling differences; object-attached wording separately pending.',
 'm04':'Rows(0,0,-1),(0,1,0),(1,0,0),point(1,0,2)→(2,0,-1) and unchanged physical point present. 의/에 and 이표/2표 readbacks do not change the demonstration.',
 'm05':'Both storage directions, inverse=transpose only under unit/orthogonal constraints and stretch counterexample preserved. Critical worked-coordinate recognition separately pending.',
 'm06':'3×3linear,4×4homogeneous,4×3row-affine, target-vector-versus-point and typed directional APIs preserved. 늘이기/느리기 is a Korean resyllabification spelling ambiguity; 아핀/앞인,좌표/자표 and 각변위/각변이 remain phonetic recognition cautions, not a proved audio defect.',
 'm07':'Projection/dot=sumproducts=lengthproductcos, unit-length condition,0/90/180 values, directioncosinematrix and m11=0/m22=1 preserved.60deg fraction separately pending. Repeated 두 occupies the same source interval and is not evidence of repeated speech.',
 'm08':'P/Q/R-prime names, not differentiation; common orthonormal coordinates before dot; row/column dual interpretation, general-linear-versus-orthogonal caveat and memory-layout distinction present. Decoder clock reset duplicates source19–24.6s; raw ASR preserved, timestamp-derived view deduplicated. Split written prime labels rejoined only for timing.',
 'm09':'Vector transform/API convenience not mandatory engine storage; linkedframesA→B→C,right product order and twoYquarter-turn worked result, noncommutativity and reverse inverse order present. World-space spelling and two-direction sentence separately pending.',
 'm10':'All measured examples directly match15×15=225,32bit=4B,9×4=36,8100B/s,12B,2700B/s,5400B/s and30s→162000B=decimal162KB. Per-second not per-frame, no compression/position/time/renderfps inference.',
 'm11':'Nine entries versus threeDOF; three unit-length+three orthogonality continuousconstraints; selfdot1/crossdot0; determinant+1rotation/-1reflection present. Raw ASR00-1 retains negative sign despite punctuation-stripped initial diff.',
 'm12':'diag(2,1,1)stretch, shear/reflection/projection separation, measurements/frameinterpretation, floatingpointcreep(exaggeratedillustration), reorthonormalization beyond independentnormalization,reflection/tolerance/damaged-data caveats preserved. Source95–101s decoder reset created duplicate transcript; no repeated-speech proof. 일에서/이래서 has unresolved phonetic spelling uncertainty and requires actual listening.',
 'm13':'Summary keeps three axes, row/column relation,dot/cosine,conversion/product/inverse,storage/manualvalidity/creep and reading one row. Decoder source19–24.88s restart duplicated transcript. Canonical transpose and memory-summary opening separately pending.'}
def main():
 c.validate();source=c.read(c.O/'tts-current.json');scripts={s['id']:s for s in c.read(H/'voice-input.json')['scenes']};review=c.read(c.O/'source-asr-review.json');assert review['complete']
 context=c.read(c.O/'context-asr-review.json')if(c.O/'context-asr-review.json').exists()else{};context_by={(r['scene'],r['line']):r for r in context.get('paragraphs',[])}
 rows=[];scenes=[]
 for scene in source['scenes']:
  sid=scene['id'];asrfile=c.R/scene['asrFile']if scene.get('asrFile')else c.O/'asr'/(sid+'.json');raw=c.read(asrfile);assert raw['audio_sha256']==scene['sha256']
  words,events=v.monotonic_word_view(raw['words']);local=[]
  for row,expected in zip(scene['lines'],scripts[sid]['lines']):
   start,end=row['startSample']/24000,row['endSample']/24000;chosen=[]
   for w in words:
    a,b=w['timestamp'];best=max(scene['lines'],key=lambda z:max(0,min(b,z['endSample']/24000)-max(a,z['startSample']/24000)))
    if best['line']==row['line']and max(0,min(b,end)-max(a,start))>0:chosen.append(w)
   recognized=''.join(w['text']for w in chosen).strip();a,b=v.n.normalized(expected),v.n.normalized(recognized);matcher=difflib.SequenceMatcher(None,a,b,autojunk=False)
   item=dict(id=f'{sid}.L{row["line"]:02}',scene=sid,line=row['line'],expected=expected,recognizedFromTimestampDerivedView=recognized,
    rawTakeFile=row['takeFile'],rawTakeSha256=row['takeSha256'],currentSceneSha256=scene['sha256'],asrFile=c.rel(asrfile),asrSha256=c.sha(asrfile),
    directWholeSourceContextRead=True,reviewMethod='All13 complete recognized scene texts read directly against the approved76 paragraphs, then actual word clocks inspected for repeated/ambiguous passages.',
    normalizedDifferences=[dict(kind=t,expected=a[i:j],recognized=b[k:l])for t,i,j,k,l in matcher.get_opcodes()if t!='equal'],
    status='source-ASR ambiguity; independent complete-context check pending'if(sid,row['line'])in CONTEXT else'no material claim omission found in direct source-text review; actual listening pending',
    humanListening='pending',automaticSemanticPass=False)
   if(sid,row['line'])in CONTEXT:item['ambiguity']=CONTEXT[(sid,row['line'])]
   if(sid,row['line'])==('m05',3):
    item['status']='Spoken-number phonology ambiguity retained; no proved wrong number. Display/source remain(2,0,-1).'
    item['phonology']='마이너스 일을 and 마이너스 이를 can both surface as[마이너스 이를] through Korean liaison. Neither ASR occurrence proves the numeric value. No-2→-1 normalization and no retake.'
   if(sid,row['line'])in context_by:
    ctx=context_by[sid,row['line']];item['independentContextAsr']=dict(file=c.rel(c.O/'context-asr'/(item['id']+'.json')),audioSha256=ctx['audio_sha256'],recognized=ctx['text'],review='Complete independent-context text directly read; ASR is not auditory approval.')
    if(sid,row['line'])==('m09',2):item['status']='World-space term recovered correctly in complete-context ASR; no source change.'
   if row.get('qaSelection',{}).get('pronunciationAlias'):
    assert(sid,row['line'])==('m07',2);item['status']='Resolved one-half pronunciation through exact-value scoped1/2=0.5 alias; candidate and changed-scene ASR both directly confirm0.5.'
    item['selectedPronunciationAlias']=row['qaSelection']['pronunciationAlias'];item['originalContextAsrIsPreviousTake']=True
   rows.append(item);local.append(item['id'])
  note=SCENE_NOTES[sid]
  if sid=='m07'and source.get('selectedRepair'):note=note.replace('60deg fraction separately pending.','60deg component is now confirmed0.5 in the selected scoped1/2=0.5 alias; all display wording unchanged.')
  if sid=='m09':note=note.replace('World-space spelling and two-direction sentence separately pending.','World-space spelling recovered in complete-context ASR; the two-direction sentence retains its recognition caution for actual listening.')
  scenes.append(dict(id=sid,paragraphIds=local,claimReview=note,rawDecoderClockEvents=events))
 assert len(rows)==76
 c.save(c.O/'source-content-review.json',dict(revision='orientation-matrix-v8',approvedScriptSha256=c.APPROVED,
  inputs=dict(sourceReceiptSha256=c.sha(c.O/'tts-current.json'),sourceAsrReviewSha256=c.sha(c.O/'source-asr-review.json'),sourceAlignmentSha256=c.sha(c.O/'source-alignment.json')),
  completeDirectWholeSourceTextRead=True,sceneCount=13,paragraphCount=76,scenes=scenes,paragraphs=rows,
  unresolvedRecognitionSpellingsForHumanListening=[f'{s}.L{i:02}'for s,i in CONTEXT if(s,i)not in [('m07',2),('m09',2)]],sourceRepair=source.get('selectedRepair'),originalRawPcmPreserved=True,sourceSpeed=1,
  status='All76 current source paragraphs directly compared; m07 value confirmed by scoped decimal alias, world-space spelling recovered, remaining recognition/phonology cautions recorded without claiming listening approval.',
  acceptedSpellingEquivalents='Verified native/Arabic numeral readbacks,axisletters,prime/API label renderings and phonetic Korean spelling differences only. Wrong coordinate or reciprocal values are never silently equated.',
  humanWholeListening='pending',actualVoiceVisualPace='pending',finalEncodedAac='pending exact final master;sourceASR is not final mix QA'))
 print('Recorded full13-scene76-paragraph direct source-text review;8 selected contexts reviewed;scoped one-half alias confirmed;human listening pending')
if __name__=='__main__':main()
