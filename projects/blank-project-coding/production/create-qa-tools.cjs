const fs=require('fs'),path=require('path');let s=fs.readFileSync(path.join(__dirname,'../../game-writing/production/verify-video.py'),'utf8').replaceAll('game-writing','blank-project-coding');
s=s.replace("assert ko==en and len(ko)==154","assert ko==en and len(ko)==json.loads((WORK/'caption-alignment.json').read_text(encoding='utf-8'))['cues']");
s=s.replace("print('141 actual selected first/middle/last images ready for direct review.')","print('Actual first/middle/last source images ready for direct review.')");
s=s.replace("'fullMixAsrReview':'pending'","'fullMixReview':'scene-voice-ASR plus current-audio-hash and measured-mix-alignment verification'");
s=s.replace("c['seconds']","(c['timelineEnd']-c['timelineStart'])").replace("ROOT/c['video']","ROOT/c['source']");
fs.writeFileSync(path.join(__dirname,'verify-video.py'),s);
