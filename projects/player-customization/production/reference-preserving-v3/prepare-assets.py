"""Extract source-linked stills; no reference lesson frames or Git raster writes."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess

ROOT = Path(__file__).resolve().parents[4]
PROJECT = ROOT/'projects/player-customization'
HERE = Path(__file__).resolve().parent
LOCAL = PROJECT/'production/local/reference-preserving-v3'
FF = os.environ.get('FFMPEG', 'C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin/ffmpeg.exe')


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(8*1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def main():
    auth = json.loads((HERE/'authorization.json').read_text(encoding='utf-8-sig'))
    assert auth['fullProductionAuthorized'] and auth['revision'] == 'reference-preserving-v3'
    origin = ROOT/'projects/game-math-euler-axis-angle/production/local/revision-v3/sources/YNQ20CKbY8U-hls.mp4'
    zelda = LOCAL/'media/totk-fuse.mp4'
    expected = '2f415500919c69dc8525bacf728d355bf10bf28de7a854dd3032c67ab1a29cc2'
    if not zelda.exists():
        assert sha(origin) == expected
        shutil.copy2(origin, zelda)
    assert sha(zelda) == expected
    acnh = PROJECT/'production/local/reference-preserving-v2/media/nintendo-acnh-character-creation.mp4'
    rows = [
        ('splatoon-shop', LOCAL/'media/splatoon-shop.mp4', 4, 'https://www.youtube.com/watch?v=mEAk2nQydPg', 'Karmakazi', 'Weapon shop candidate and description; selection is not yet equipment confirmation.'),
        ('splatoon-shooter', LOCAL/'media/splatoon-shooter.mp4', 70, 'https://www.youtube.com/watch?v=mEAk2nQydPg', 'Karmakazi', 'Shooter main-weapon firing with muzzle flash and target response; excludes the earlier Quick Bomb. The visible UI is not our measured comparison.'),
        ('splatoon-charger', LOCAL/'media/splatoon-charger.mp4', 30, 'https://www.youtube.com/watch?v=mEAk2nQydPg', 'Karmakazi', 'Charger shot and target response in lobby; the displayed value is not our numerical comparison or measurement.'),
        ('totk-inventory', zelda, 1120, 'https://www.youtube.com/watch?v=YNQ20CKbY8U', 'Royalty Free Game Clips', 'Weapons category/icon and candidate cursor; blue equipped cell and yellow cursor are distinct.'),
        ('totk-test', zelda, 1328, 'https://www.youtube.com/watch?v=YNQ20CKbY8U', 'Royalty Free Game Clips', 'Boulder attachment after material choice, before wall-breaking trial.'),
        ('acnh-before', acnh, 150.5, 'https://www.youtube.com/watch?v=kfiiYm3iuKY', 'LongplayArchive / SpectreBull', 'Initial hairstyle selection with linked avatar preview.'),
        ('acnh-after', acnh, 151.5, 'https://www.youtube.com/watch?v=kfiiYm3iuKY', 'LongplayArchive / SpectreBull', 'Changed initial hairstyle on same avatar; no performance claim.'),
        ('acnh-categories', acnh, 155, 'https://www.youtube.com/watch?v=kfiiYm3iuKY', 'LongplayArchive / SpectreBull', 'Eye category/options in initial appearance menu; not a mirror or clothes shop.'),
    ]
    out = LOCAL/'assets'; out.mkdir(parents=True, exist_ok=True)
    dest = ROOT/'output/player-customization/preproduction-assets-v3'; dest.mkdir(parents=True, exist_ok=True)
    records = []
    for name, source, at, url, recorder, purpose in rows:
        target = out/(name+'.png')
        signature = dict(sourceSha256=sha(source), sourceSeconds=at, accurateSeek=True, crop='none', outputDimensions=[1920,1080])
        cache = out/(name+'.json')
        if cache.exists():
            old = json.loads(cache.read_text(encoding='utf-8-sig'))
            assert old['extraction'] == signature and target.exists() and sha(target) == old['sha256']
        else:
            assert not target.exists()
            subprocess.run([FF,'-nostdin','-n','-v','error','-threads','2','-ss',str(at),'-i',str(source),'-frames:v','1',str(target)],check=True)
        record = dict(id=name, image=target.relative_to(ROOT).as_posix(), sha256=sha(target),
                      sourceFile=source.relative_to(ROOT).as_posix(),sourceUrl=url,uploader=recorder,
                      extraction=signature,purpose=purpose,sourceRole='independent-gameplay',
                      referenceLessonUsed=False,classification='explanation-still',
                      layoutReview='pending actual1080/mobile with final captions')
        cache.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        shutil.copy2(target,dest/target.name)
        records.append(record)
    (HERE/'visual-assets.json').write_text(json.dumps(dict(revision='reference-preserving-v3',assets=records),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Prepared8 independent gameplay explanation stills. Current layout review pending.')


if __name__ == '__main__':
    raise SystemExit('Superseded candidate extraction: current Raiders/BOTW assets require new inspected source records. See title-selection.json; retain existing candidate images as unused research.')
