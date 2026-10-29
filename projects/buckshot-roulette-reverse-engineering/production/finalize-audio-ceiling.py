"""Allow AAC reconstruction headroom; preserve verified video and original voice."""
from pathlib import Path
import shutil
import assemble_documentary as edit

P=Path(__file__).resolve().parents[1]
OLD=P/'production/local/documentary-v2'
NEW=P/'production/local/documentary-v3'

def main():
    plan_path=P/'production/timeline.json';plan=edit.load(plan_path)
    previous=edit.load(OLD/'technical-qa.json')
    previous.update(audioLoudnessPassed=False,deliveryBlocked=True,
        correction='AAC reconstruction peak -1.2dBTP exceeds -1.5dBTP policy; final limiter ceiling adjusted from -1.5 to -2.0dB. Superseded by v3, never delivered.')
    edit.save(OLD/'technical-qa.json',previous)
    NEW.mkdir(parents=True,exist_ok=True)
    if not (OLD/'timeline-before-peak-fix.json').exists():shutil.copy2(plan_path,OLD/'timeline-before-peak-fix.json')
    plan.update(workDirectory='production/local/documentary-v3',outputDirectory=str(edit.REPO/'output'/f'{P.name}-v3'))
    edit.save(plan_path,plan)
    receipt=edit.validate(plan,plan_path,NEW)
    output=edit.resolve(plan['outputDirectory']);output.mkdir(parents=True,exist_ok=True)
    stem=P.name
    assert not any((output/f'{stem}.{kind}.mp4').exists() for kind in ['clean','captioned'])
    edit.ff(plan,['-i',OLD/'complete-mix.wav','-af','aresample=192000,alimiter=limit=0.794328:level=false:latency=true,aresample=48000','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',NEW/'approved-pair-audio.m4a'],NEW/'logs/encode-single-aac.log')
    identical={}
    previous_packets=edit.load(OLD/'repair-receipt.json')['videoPacketHashesUnchanged']
    for kind in ['clean','captioned']:
        original=Path(previous['outputs'][kind]['file']);target=output/f'{stem}.{kind}.mp4'
        edit.ff(plan,['-i',original,'-i',NEW/'approved-pair-audio.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-map_metadata','-1','-movflags','+faststart',target],NEW/'logs'/f'{kind}-remux.log')
        dest=NEW/f'{kind}-video.sha256'
        edit.ff(plan,['-i',target,'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256',dest],NEW/'logs'/f'{kind}-video-hash.log')
        actual=dest.read_text().strip();assert actual==previous_packets[kind]
        identical[kind]=actual
    for lang in ['ko','en']:shutil.copy2(NEW/f'captions.{lang}.srt',output/f'{stem}.{lang}.srt')
    edit.write_index(output,stem)
    qa=edit.verify(plan,receipt,NEW)
    edit.save(NEW/'repair-receipt.json',{'createdAt':edit.now(),'reason':'AAC reconstruction headroom -2.0dB limiter ceiling; narration gain/timing preserved',
        'sourceNarrationUnchanged':edit.digest(edit.resolve(plan['narration']['wav']))==receipt['narrationSha256'],
        'videoPacketHashesUnchanged':identical,'durationSeconds':receipt['totalFrames']/60,
        'encodedTruePeakDbtp':qa['encodedTruePeakDbtp'],'priorMastersRetainedNeverDelivered':True,
        'newCaptionedSha256':qa['outputs']['captioned']['sha256']})
    print('Final audio peak passed; video packets and narration input unchanged.')

if __name__=='__main__':main()
