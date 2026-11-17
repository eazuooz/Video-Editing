"""Speech-coverage comparison with explicit evidence for silent-region ASR hallucinations."""
import difflib

def norm(text):return ''.join(c.lower() for c in text if c.isalnum())

def compare_speech(narration_asr,mix_asr,timeline,narration_path):
    import numpy as np
    import soundfile as sf
    pcm,rate=sf.read(narration_path,always_2d=True)
    windows=[(s['start'],s['speechEnd']) for s in timeline['scenes']]
    excluded=[]
    def within_speech(asr,kind):
        kept=[]
        for word in asr['chunks']:
            a,b=word['timestamp']
            assert a is not None and b is not None,(kind,'missing timestamp',word)
            if any(b>=start-.05 and a<=end+.05 for start,end in windows):
                kept.append(word['text']);continue
            # Do not silently discard a mismatch. Every excluded word must be
            # outside all narration windows and over sample-confirmed silence.
            first=max(0,int((a-.025)*rate));last=min(len(pcm),max(first+1,int((b+.025)*rate)))
            peak=float(np.max(np.abs(pcm[first:last]))) if last>first else 0
            assert peak<1e-5,(kind,'ASR outside speech over non-silent narration',word,peak)
            excluded.append({'track':kind,'word':word['text'],'timestamp':[a,b],'narrationPeakAmplitude':peak,'basis':'Outside every planned speech window and over confirmed silent narration PCM; raw ASR retained.'})
        return norm(''.join(kept))
    expected=within_speech(narration_asr,'narration')
    actual=within_speech(mix_asr,'mix')
    sequence=difflib.SequenceMatcher(None,expected,actual,autojunk=False)
    missing=[expected[a:b] for tag,a,b,c,d in sequence.get_opcodes() if tag=='delete' and b-a>=12]
    return {'ratioAgainstFullNarrationAsr':sequence.ratio(),'materialMissingSpans':missing,
            'encodedMixAsrSha256':mix_asr['audio_sha256'],'narrationAsrSha256':narration_asr['audio_sha256'],
            'excludedSilentRegionRecognitions':excluded,'rawTranscriptRatio':difflib.SequenceMatcher(None,norm(narration_asr['text']),norm(mix_asr['text']),autojunk=False).ratio()}
