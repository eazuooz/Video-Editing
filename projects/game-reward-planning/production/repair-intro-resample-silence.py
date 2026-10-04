"""Only erase resampling ringing inside the already silent 2s branding."""
from pathlib import Path
import hashlib,json,shutil
import soundfile as sf,numpy as np
WORK=Path(__file__).resolve().parent/'final-v1';FILE=WORK/'voice-normalized.wav';old=WORK/'voice-normalized-before-intro-resample-repair.wav';assert not old.exists()
raw,sr=sf.read(WORK.parent/'measured-edit-v3/narration-timed.wav',dtype='int16',always_2d=True);assert sr==24000 and not np.any(raw[:48000])
wav,rate=sf.read(FILE,dtype='int16',always_2d=True);assert rate==48000;shutil.copy2(FILE,old);tail=wav[96000:].copy();count=int(np.count_nonzero(wav[:96000]));peak=int(np.max(np.abs(wav[:96000].astype('int32'))));wav[:96000]=0;sf.write(FILE,wav,rate,subtype='PCM_16');new,s=sf.read(FILE,dtype='int16',always_2d=True);assert np.array_equal(tail,new[96000:]) and not np.any(new[:96000])
(WORK/'intro-resample-repair.json').write_text(json.dumps({'reason':'24k-to48k interpolation creates tiny pre-onset ringing in the originally exact-silent intro. Zero only the already silent2s; do not truncate/move any spoken sample.','oldSha256':hashlib.sha256(old.read_bytes()).hexdigest(),'newSha256':hashlib.sha256(FILE.read_bytes()).hexdigest(),'nonzeroIntroChannelSamplesBefore':count,'introPeakIntegerBefore':peak,'allNormalizedBodyAndOutroSamplesByteIdentical':True,'sourcePcmUntouched':True,'humanListening':'pending'},indent=2)+'\n',encoding='utf8');print(json.dumps({'introRingingChannelSamples':count,'originalPeak':peak,'allOtherSamplesIdentical':True}))
