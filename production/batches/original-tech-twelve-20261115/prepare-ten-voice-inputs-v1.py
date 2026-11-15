"""One-shot CPU input locking for the exact remaining ten original-tech lessons.

Locks original, source-supported speech. This does not accept footage actions,
native visuals, voice quality, word timestamps, final films or human review.
"""
from pathlib import Path
import datetime,hashlib,json,copy
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
MEDIA=Path('C:/Users/1/Videos/YamyamProduction/original-tech-twelve-20261115')
RUN=MEDIA/'production-resume-20261115T055255Z';PREP=MEDIA/'ten-cpu-prep-20261115'
def read(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def sha(p):
    with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def pin(p):return dict(path=str(Path(p).resolve()),sha256=sha(p))
def save(p,d):
    p=Path(p);assert not p.exists(),f'Preserve existing source: {p}'
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
# Local source, original public metadata, inspected contact, model compiler,
# observed scope, remaining action/rights limits. The source is only context
# where the specific internal mechanism cannot be seen in gameplay pixels.
CASES=[
 ('shorts-journey-sand-sparkle','journey-free-PcL6zmz4GM8-candidate-copy-v2.mp4','journey-free-metadata-v1.json','journey-free-contact-v2.jpg','sand-static-v1',
  'Eight decoded samples show dune traversal, flight, changing viewpoints, dune shading and ruins. Use the source as game context; the original fine-grain buffers are not observable.',
  'Recorder explicitly permits commercial/noncommercial use without required credit. Primary source is thatgamecompany\'s published presentation; its figures are research only. Final excerpt must preserve scenery, speed and original aspect. Fine glints are demonstrated by our labelled shader, not claimed from compressed pixels.'),
 ('shorts-horizon-gpu-placement','JxqdU3IKHoo-candidate-120-180-copy-v1.mp4','horizon-candidate-metadata-v1.json','horizon-contact-v1.jpg','placement-static-v1',
  'Six decoded samples show trees beside a walkable path, vegetation, traversal and plant collection in Zero Dawn. No placement buffers or artist maps are visible.',
  'Recorder title explicitly says FREE TO USE; description and channel bio add no detailed terms. This narrower basis is recorded rather than invented as CC. Publisher scope remains separate; source is context for local commentary review. Do not relabel as Forbidden West, remaster or an exact GPU benchmark.'),
 ('shorts-inside-temporal-antialiasing','inside-free-9rwA7qvYnds-candidate-copy-v2.mp4','inside-free-metadata-v1.json','inside-free-contact-v2.jpg','temporal-static-v2',
  'Eight decoded samples show a moving character, forest edges, thin geometry, headlights and reflections. These are visual context, not access to original motion/depth/history buffers.',
  'Recorder CC Attribution plus explicit creator-use permission. Playdead permits video commentary with original audio and visuals together: final game excerpts must pair this recording\'s original audio at exact matching source time. Full same-source audio is preserved separately. Do not adopt a silent detached excerpt. MIT implementation license is a separate permission and remains bundled with modified source.'),
 ('shorts-spiderman-swing-anchor','pressstartplay-5Q4AfoUX1eU-swing-120-190-v4.mp4','spiderman-free-metadata-v2.json','spider-swing-contact-v1.jpg','remaining-seven-static-v2',
  'Eight decoded samples include rooftop setup followed by street swinging, a visible web, wall traversal and resumed swinging. Suggested local context9–40s; final continuous in/out and occlusion remain to be checked.',
  'Recorder CC Attribution and explicit free creative-use description. Actual recording is PC Remastered per recorder; label it separately from the documented2018 implementation. Do not infer internal attachment candidates, exact stick input or selected scoring from these pixels. Earlier combat-only candidate is rejected for swing teaching.'),
 ('shorts-control-destruction-pipeline','control-free-TVfahIR7lYQ-candidate-copy-v2.mp4','control-free-metadata-v1.json','control-free-contact-v2.jpg','remaining-seven-static-v2',
  'Eight decoded samples show office combat and desks, red-carpet progression, firing and an interrupting map. Final edit must exclude inventory/map interruptions and verify any claimed intact→impact→fragment action.',
  'Recorder CC Attribution and explicit creator-use permission; Xbox Series S per recorder. Remedy fan-content conditions apply separately. This is local commentary review, not a finding that unrestricted commercial publishing is cleared. Internal fracture hierarchy is illustrated by our own prepared desk, not inferred from the game frames.'),
 ('shorts-returnal-particle-tentacles','nohud-8-OJj2JoPfQ-candidate-45-105-copy-v2.mp4','returnal-nohud-candidate-metadata-v1.json','returnal-contact-v2.jpg','remaining-seven-static-v2',
  'Six decoded samples show the Ophion encounter, tendril-like forms and projectiles. The developer article supports the node mechanism; these pixels do not identify every Ophion mesh as that specific system.',
  'Recorder CC Attribution plus explicit reuse permission. PC MAX-settings per recorder; channel mentions visual mods and some HUD remains. Do not present as an unmodified PS5 baseline. The parent-transform native comparison is an introductory illustration, not the article\'s one-frame-old solver. That delay and cylindrical surface need their own explicitly labelled diagrams.'),
 ('shorts-ratchet-dimension-streaming','gXQ2ipMeyDQ-candidate-120-180-copy-v1.mp4','ratchet-candidate-metadata-v1.json','ratchet-contact-v1.jpg','remaining-seven-static-v2',
  'Six decoded samples show city movement, dimensional effects and a portal approach. Complete transition and exact recording platform remain to be checked for the final excerpt.',
  'Recorder title explicitly says FREE TO USE GAMEPLAY; no detailed CC terms are supplied. Description discusses PC while tags include PS5: do not invent a confirmed platform. Explain the documented PC pipeline using our labelled read/decompress model. Never use this recording as a PC storage speed measurement.'),
 ('shorts-doom-push-forward-healing','genericbomb-2tXXuiAU1Xs-full-f299-v3.mp4','doom-generic2-metadata-v1.json','doom-health-event-v5.jpg','remaining-seven-static-v2',
  'Dense decoded samples244–256s show low-health combat, a highlighted staggered enemy, approach, close finishing animation and blue pickups with HUD changes.305–314s contains a second highlighted enemy and close finish. Preserve exact sequence; do not label nearby green armor pickups as health. Chainsaw/fuel is not shown in these inspected ranges.',
  'Recorder explicitly permits any voice-over/video projects and no required credit; metadata also labels CC Attribution. Include recorder/source/modifications in descriptions. Bethesda publisher policy is separate. Do not infer a universal exact reward amount or DOOM Eternal resource rules. Chainsaw cost/reward may use a labelled rule diagram until an actual matching independent game excerpt is verified.'),
 ('shorts-botw-chemistry-rules','archive64-tOvTBrO7bPo-fire-candidate-410-500-v2.mp4',None,'botw-fire-contact-v1.jpg','remaining-seven-static-v2',
  'Eight decoded samples show Link, the Old Man and an already burning campfire, plus dialogue and traversal. This is fire context only: it does not show ignition or rain extinguishing and must never be called that proof.',
  'Archive64 explicitly allows edited/monetized reuse in its original description. CEMU recording with a declared upscale; do not label it native Switch footage or original4K. The GDC rules support the spoken explanation. Show causal ignition/rain only in our labelled, actually captured rule demonstration or a later verified game excerpt.'),
 ('shorts-mariokart8-spin-boost','royaltyfree-npz4T7sznog-full-f299-v3.mp4','mk8-free-metadata-v1.json','mk8-contact-dense-v4.jpg','remaining-seven-static-v2',
  'Decoded0.5-second samples224–240s show Water Park anti-gravity wheels, approach to a rotating underwater post at226.5s, kart rotation and circular blue effect by227s, then continuing motion. Still samples are not a speed measurement.282.5s shows a separate hit/coin loss: exclude it as a successful Spin Turbo example.',
  'Recorder explicitly permits reuse/editing/upload/monetization with no mandatory attribution. Original game/version/hardware remain separate: title is Mario Kart8, single-slot HUD and FPS overlay are visible, but hardware is not confirmed. Use the Wii U primary terminology Spin Turbo and do not claim Deluxe or measured acceleration from these frames. Final cue needs denser contact continuity and a verified eligible target.'),
]
def main():
    import av
    batch=read(HERE/'batch.json');assert [x['slug'] for x in batch['projects'][2:]]==[x[0] for x in CASES]
    manifest_template=read(ROOT/'projects/shorts-mario64-lakitu-camera/production/tts-manifest-v1.json')
    # Preflight every input before the first mutation.
    prepared=[]
    for row,case in zip(batch['projects'][2:],CASES):
        slug,filename,meta,contact,compiler,observed,limits=case;p=ROOT/'projects'/slug;source=MEDIA/slug/'sources'/filename
        metadata=RUN/meta if meta else PREP/'footage-botw-metadata-v1.json';assert source.is_file() and metadata.is_file()
        draft=ROOT/row['narrationDraft'];order=ROOT/row['sourceOrderMap'];primary=ROOT/row['currentSourceReview'];cpu=RUN/compiler/'compile-receipt.json'
        d=read(draft);assert not d['narrationLocked'] and all(x['ko'] and x['en'] for x in d['paragraphs']);assert read(primary)['source']['fullRelevantScopeReviewed'];assert read(cpu)['staticCompilationPassed']
        with av.open(str(source)) as c:
            f=next(c.decode(video=0));assert f.width>=1920 and f.height>=1080
            decoded=dict(width=f.width,height=f.height,fps=str(c.streams.video[0].average_rate),containerSeconds=c.duration/av.time_base)
        for relative in ['planning/source-action-review-v3.json','planning/narration-locked-v1.json','script/narration.ko.v1.json','production/tts-manifest-v1.json']:assert not (p/relative).exists(),str(p/relative)
        prepared.append((row,case,p,d,draft,order,primary,cpu,source,metadata,decoded))
    summary=[]
    for row,case,p,d,draft,order,primary,cpu,source,metadata,decoded in prepared:
        slug,filename,meta,contact,compiler,observed,limits=case
        action=dict(schemaVersion=3,slug=slug,recordedAtUtc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='speech-meaning-matched; final visual actions and runtime QA pending',sourceInputs=[pin(x) for x in [source,metadata,RUN/contact,primary,order,cpu]],sourceUrl='https://www.youtube.com/watch?v='+str(read(metadata).get('id','tOvTBrO7bPo')),decoded=decoded,observations=observed,claimAndPermissionLimits=limits,
          cuePolicy='Use actual gameplay only for observed actions and context. Internal algorithms use independently authored diagrams or own labelled Unity scenes in original source order. Planned scenes are not marked captured. Final cues require whole-word speech anchors and actual runtime output.',
          sourceAndNarrationSemanticsReady=True,speechTextSupportedByPrimarySource=True,allFinalActionCuesAccepted=False,originalEngineBuffersObserved=False,actualNativeRuntimeReviewed=False,continuousWholeRecordingViewed=False,publicUploadApproved=False,humanApproval=False)
        action_path=p/'planning/source-action-review-v3.json';save(action_path,action)
        locked=copy.deepcopy(d);locked.update(status='source-order-speech-locked; native and final action QA pending',narrationLocked=True,approvedForTts=True,sourceDraft=pin(draft),sourceOrderMap=pin(order),primarySourceReview=pin(primary),sourceActionReview=pin(action_path),nativeModelCpuReview=pin(cpu),reason='Original primary-source-supported wording preserved. Acquired independent gameplay is scoped to observed context/actions. Own illustrations explain internal mechanisms and still require actual runtime/visual QA. Voice and final media acceptance remain separate.',humanApproval=False)
        save(p/'planning/narration-locked-v1.json',locked)
        script=dict(title=d['workingTitle'],status='locked-v1 natural voice input; separate blind word/level review required',scenes=[dict(id=f'{i:02}',title=x['id'],lines=[x['ko']]) for i,x in enumerate(d['paragraphs'],1)]);save(p/'script/narration.ko.v1.json',script)
        manifest=copy.deepcopy(manifest_template);manifest['slug']=slug;manifest['paths']['script']=str((p/'script/narration.ko.v1.json').relative_to(ROOT)).replace('\\','/');manifest['tts']['outputDir']='shared/output/original-tech-twelve-20261115/'+slug+'/voice-v1';manifest['tts']['filenameStem']='lesson-voice-v1';save(p/'production/tts-manifest-v1.json',manifest)
        summary.append(dict(slug=slug,paragraphs=len(d['paragraphs']),locked=pin(p/'planning/narration-locked-v1.json'),manifest=pin(p/'production/tts-manifest-v1.json'),sourceActionReview=pin(action_path),finalFilmComplete=False))
    save(RUN/'ten-voice-input-locks-v1.json',dict(exactTopics=10,inputs=summary,existingDraftsUnmodified=True,modelsStarted=False,finalFilmsCreated=False))
    print(json.dumps(dict(speechInputsLocked=10,paragraphs=sum(x['paragraphs'] for x in summary),modelsStarted=False),ensure_ascii=False))
if __name__=='__main__':main()
