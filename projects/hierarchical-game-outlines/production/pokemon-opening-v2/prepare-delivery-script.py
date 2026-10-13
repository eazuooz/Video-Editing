from pathlib import Path
P=Path(__file__).resolve().parent;N=P.parent/'reference-preserving-v1'
s=(N/'deliver-selected-v1.cjs').read_text(encoding='utf-8')
s=s.replace("production/reference-preserving-v1", "production/pokemon-opening-v2")
s=s.replace("settings.videoId!=='JoHXz7YtEPw'||", "!/^[-_A-Za-z0-9]{11}$/.test(settings.videoId)||")
s=s.replace("videoId:'JoHXz7YtEPw'", "videoId:settings.videoId")
s=s.replace('Complete hierarchical outlines private video and consolidate one-video production rules','Add Pokemon planning introduction and independent narration to hierarchical outlines')
s=s.replace('Integrated rules and this selected independent-footage video only; raw sources, QA media and foreign queues excluded','Selected Pokemon-opening revision only; prior delivery, foreign rules, queues, raw sources and QA media excluded')
s=s.replace("save(P+'/git-precommit-failure-v1.json',{", "save(P+'/git-precommit-failure-'+Date.now()+'.json',{")
a=s.index('function ordinaryFiles(){');b=s.index("if(process.argv.includes('--prepare'))",a)
names='''acquire-pokemon.py build-current-v1.py build-timeline.py caption-alignment-review-v1.json caption-timing-direct-review.json captions.en.srt captions.ko.srt captions.py collect-current-v1.cjs collection-verification-v1.json current-voice-splice.json duplicate-current-review.json final-direct-review-v1.json final-pixel-plan-v1.json final-timeline-v1.json inspect-source.py latest-checkpoint.json main-promotion-v1.json mix-asr-v1.json mix-direct-review-v1.json mix-execution-v1.json mix-final-inputs-v1.json narration-before-sentence-repair.en.json narration-before-sentence-repair.ko.json narration.en.json narration.ko.json native-caption-preflight-review.json normal-direct-review-v1.json pair-execution-v1.json preflight-native-and-render.py preparation-console-failure.json prepare-08-repair.py prepare-assembler.py prepare-delivery-script.py prepare-normal-review.py prepare-publishing.py prepare-renderer.py prepare-repair-asr.py prepare-revision.py prepare-script.py prepare-voice.py preservation.json promote-current-v1.py qa-execution-v1.json render-pokemon.cjs render-repair08.py render-voice-v1.py review-ambiguity.py review-audio-v1.py review-repair08.py revision-request.json script-review.json seal-current-voice.py seal-final-review.py seal-private-delivery.py source-acquisition.json source-direct-review.json source-inspection.json source-normal-observation.json tts-request.ko.json visuals-execution-v1.json voice-actual-closure.json voice-ambiguity.json voice-asr-v1.json voice-current-asr.json voice-current-inputs.json voice-direct-review.json voice-execution-v1.json voice-manifest.json voice-repair08-asr.json voice-repair08-closure.json voice-repair08-execution-v1.json voice-repair08-manifest.json voice-repair08-reason.json voice-repair08-request.json white-cpu-execution.json white-preflight-direct-review.json white-render-wrapper-v1.json deliver-selected-v1.cjs'''.split()
names += '''duck-two-passages-v2.py finalize-duck-existing-v2.py mix-duck-v2.json mix-duck-existing-verification-v2.json mix-final-inputs-before-duck-v1.json mix-asr-v2.json review-audio-v2.py mix-contexts-v1.json mix-context-plan-v1.json review-mix-contexts.py pixel-direct-observations-v1.json collect-current-v2.cjs collection-verification-v2.json repair-caption-review-timing-v1.py caption-review-timing-repair-v1.json finalize-current-plan.py'''.split()
pub='''titles.json description.ko.txt description.en.txt pinned-comment.ko.txt youtube-upload-v1.json upload-wizard-evidence-v1.json private-settings-direct-review-v1.json main-private-transition-v1.json git-preflight-rebuild-v1.json'''.split()
import json
new="""function ordinaryFiles(){
 const own=['project.json','rebuild.json','planning/production-plan.json','production/review-ledger.json','production/delivery-output.json'].map(s=>'projects/'+slug+'/'+s);
 const code=['pokemon-opening-plan-v2.json','pokemon-opening-v2.tsx'].map(s=>'motion-canvas/src/projects/'+slug+'/'+s);
 const names=%s.map(s=>N+'/'+s);
 const pub=%s.map(s=>P+'/'+s);
 return [...new Set([...own,...code,...names,...pub])].sort();
}
"""%(json.dumps(names),json.dumps(pub))
s=s[:a]+new+s[b:]
(P/'deliver-selected-v1.cjs').write_text(s,encoding='utf-8')
print('Explicit selected-video delivery script prepared; not staged, committed or pushed.')
