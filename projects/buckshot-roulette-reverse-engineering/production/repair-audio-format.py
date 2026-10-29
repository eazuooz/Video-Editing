"""Repair the never-delivered v1 mixed-PCM join without re-encoding video."""
from pathlib import Path
import shutil
import assemble_documentary as edit

P=Path(__file__).resolve().parents[1]
OLD=P/'production/local/documentary-v1'
NEW=P/'production/local/documentary-v2'

def main():
    plan_path=P/'production/timeline.json';plan=edit.load(plan_path)
    previous=edit.load(OLD/'technical-qa.json')
    previous.update(technicalDecodePassed=False,deliveryBlocked=True,
        correction='Mixed PCM demuxer join corrupted audio; video343.083333s/audio674.166667s. Superseded by v2, never delivered.')
    edit.save(OLD/'technical-qa.json',previous)
    NEW.mkdir(parents=True,exist_ok=True)
    if not (OLD/'timeline-before-audio-fix.json').exists():shutil.copy2(plan_path,OLD/'timeline-before-audio-fix.json')
    plan['workDirectory']='production/local/documentary-v2'
    plan['outputDirectory']=str(edit.REPO/'output'/f'{P.name}-v2')
    edit.save(plan_path,plan)
    receipt=edit.validate(plan,plan_path,NEW)
    output=edit.resolve(plan['outputDirectory']);output.mkdir(parents=True,exist_ok=True)
    stem=P.name
    assert not any((output/f'{stem}.{kind}.mp4').exists() for kind in ['clean','captioned'])
    parts=[OLD/'bookend-brand.wav',OLD/'body-mix.wav',OLD/'bookend-member.wav']
    edit.concat(plan,parts,NEW/'complete-mix.wav',NEW,'complete-mix-filter',audio=True)
    meta=edit.probe(NEW/'complete-mix.wav',plan)
    assert abs(float(meta['format']['duration'])-receipt['totalFrames']/60)<1/48000
    edit.ff(plan,['-i',NEW/'complete-mix.wav','-af','aresample=192000,alimiter=limit=0.841395:level=false:latency=true,aresample=48000','-c:a','aac','-b:a','192k','-ar','48000','-ac','2',NEW/'approved-pair-audio.m4a'],NEW/'logs/encode-single-aac.log')
    identical={}
    for kind in ['clean','captioned']:
        original=Path(previous['outputs'][kind]['file']);target=output/f'{stem}.{kind}.mp4'
        edit.ff(plan,['-i',original,'-i',NEW/'approved-pair-audio.m4a','-map','0:v:0','-map','1:a:0','-c','copy','-map_metadata','-1','-movflags','+faststart',target],NEW/'logs'/f'{kind}-remux.log')
        hashes=[]
        for label,path in [('before',original),('after',target)]:
            dest=NEW/f'{kind}-{label}-video.sha256'
            edit.ff(plan,['-i',path,'-map','0:v:0','-c:v','copy','-f','hash','-hash','sha256',dest],NEW/'logs'/f'{kind}-{label}-video-hash.log')
            hashes.append(dest.read_text().strip())
        assert hashes[0]==hashes[1]
        identical[kind]=hashes[0]
    for lang in ['ko','en']:shutil.copy2(NEW/f'captions.{lang}.srt',output/f'{stem}.{lang}.srt')
    edit.write_index(output,stem)
    qa=edit.verify(plan,receipt,NEW)
    edit.save(NEW/'repair-receipt.json',{'createdAt':edit.now(),'reason':'Decode mixed S16/FLOAT inputs independently before joining',
        'sourceNarrationUnchanged':edit.digest(edit.resolve(plan['narration']['wav']))==receipt['narrationSha256'],
        'videoPacketHashesUnchanged':identical,'correctedDurationSeconds':receipt['totalFrames']/60,
        'priorMastersRetainedNeverDelivered':True,'newCaptionedSha256':qa['outputs']['captioned']['sha256']})
    print('Audio format repaired; video packets unchanged; exact duration and full decode passed.')

if __name__=='__main__':main()
