"""CPU1 sample validation of editorial title-only changes; no motion edits."""
import subprocess
from PIL import Image
import caption_safe_stage_footer as p
from qa_caption_safe_footer import outside_equal


def main():
    data = p.read(p.H / 'caption-safe/elden-header.json')
    assert data['status'] == 'nine-canonical-game-headers-ready'
    rows = []
    out = p.DEST / 'qa'; out.mkdir(exist_ok=True)
    for kind in ('game', 'analysis'):
        j = next(j for j in data['jobs'] if j['id'].endswith('-' + kind))
        frame = j['frames'] // 2
        assert p.sha(j['source']) == j['sourceSha256']
        assert p.sha(j['output']) == j['sha256']
        old = p.decode_yuv(j['source'], frame)
        new = p.decode_yuv(j['output'], frame)
        planes = outside_equal(old, new, [0, 0, 1400, 80])
        assert old != new
        target = out / ('A16-elden-header-' + kind + '.png')
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-threads','1','-i',j['output'],
            '-filter_threads','1','-vf',f'select=eq(n\\,{frame})','-frames:v','1',
            '-an','-threads','1',str(target)],check=True,creationflags=subprocess.CREATE_NO_WINDOW)
        with Image.open(target) as im:
            assert im.size == (1920,1080)
            im.resize((375,211),Image.Resampling.LANCZOS).save(target.with_name(target.stem+'-375.png'))
        rows.append({'id':j['id'],'frame':frame,'sourceSha256':j['sourceSha256'],
                     'outputSha256':j['sha256'],'outsideHeaderDecodedYuv':planes,
                     'preview':str(target),'previewSha256':p.sha(target)})
    for j in data['jobs']:
        assert p.sha(j['output']) == j['sha256']
        streams = p.probe(j['output']); assert len(streams)==1
        s=streams[0]
        assert (s['width'],s['height'],s['avg_frame_rate'],int(s['nb_frames']))==(1920,1080,'60/1',j['frames'])
    p.save(p.H/'caption-safe/elden-header-qa.json',{
        'status':'technical-header-only-validation-passed-visual-inspection-pending',
        'allNineFrameCountsAndHashesVerified':True,'sourcePixelsStartY':80,
        'representativeNativeAndAnalysisChecks':rows,'audioChanged':False,
        'humanFullWatching':False,'humanListening':False,'modelVisualInspection':None,
        'safeGameManifestSha256':p.sha(p.H.parent/'game-plates-caption-safe.json')})
    print('Elden Ring header QA: nine hashes/frame counts and two decoded pixel comparisons passed.')


if __name__=='__main__': main()
