"""Open exact revised frames with approved audio/caption clocks; CPU only."""
from pathlib import Path
import bisect, importlib.util, json, math
from PIL import Image

H = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('requested_lockon_preview', H/'run-lockon-user-revision-v70.py')
film = importlib.util.module_from_spec(spec); spec.loader.exec_module(film)
prep, reason = film.prepare('pilot'); assert prep and reason is None
out = film.BASE.parent/'design-samples-v71'; out.mkdir(exist_ok=False)
composer = film.layout.Composer(film.P.name)
records = []; readers = {}; beats=prep['identity']['beats']; cues=prep['identity']['captionCues']
for seconds in [19.0, 38.0, 40.4, 42.4, 47.2, 67.0]:
    b=beats[bisect.bisect_right([x['start']for x in beats],seconds)-1]
    c=cues[bisect.bisect_right([x['start']for x in cues],seconds)-1]
    elapsed=seconds-b['start']; source_seconds=None
    if b['kind']=='native':
        key=b['clip']['video']['path']
        if key not in readers:readers[key]=film.layout.NativeStreamReader(b['clip'])
        index=b['startFrame']+int(math.floor(elapsed*60+1e-7));pixels,digest=readers[key].frame(index)
        im=composer.base(b.get('label','해설용 모형 · 직접 만든 비교 장면'))
        im.paste(pixels.resize((984,984),Image.Resampling.LANCZOS),(0,396))
        source=dict(kind='native',frame=index,rgbSHA256=digest)
    else:
        key=b['source']['path']
        if key not in readers:readers[key]=film.GameReader(key)
        source_seconds=b['sourceStartSeconds']+elapsed;pixels,pts=readers[key].frame(source_seconds)
        im=composer.base(b['label']);height=round(984*pixels.height/pixels.width)
        im.paste(pixels.resize((984,height),Image.Resampling.LANCZOS),(0,396+(984-height)//2))
        source=dict(kind=b['kind'],sourcePts=pts)
    film.overlays.annotate(im,b,source_seconds);composer.captioned(im,c['ko'])
    path=out/f'frame-{seconds:04.1f}.jpg';im.save(path,quality=94)
    small=out/f'frame-{seconds:04.1f}-375.jpg';im.resize((375,667),Image.Resampling.LANCZOS).save(small,quality=96)
    records.append(dict(seconds=seconds,caption=c['ko'],image=film.pin(path),mobile=film.pin(small),source=source))
for reader in readers.values():reader.close()
film.save(out/'evidence.json',dict(fingerprint=prep['fingerprint'],records=records,modelStarted=False,fullRenderStarted=False,publishingApproved=False))
print(json.dumps(dict(samples=str(out),count=len(records),fingerprint=prep['fingerprint'])))
