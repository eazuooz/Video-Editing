"""Apply the approved per-paragraph gain and fades before assembling the lecture."""
import numpy as np


def speech_level(samples,sr,settings):
    length=max(1,round(sr*settings['frameMs']/1000))
    assert len(samples)>=length,'Too-short narration take'
    frames=samples[:len(samples)//length*length].reshape(-1,length)
    db=20*np.log10(np.maximum(np.sqrt(np.mean(frames*frames,axis=1)),1e-10))
    return float(np.median(db[db>=db.max()-settings['gateBelowPeakDb']]))


def level_paragraph(samples,sr,settings,fade):
    before=speech_level(samples,sr,settings)
    gain_db=max(-settings['maxGainDb'],min(settings['maxGainDb'],settings['targetSpeechFrameMedianDbfs']-before))
    levelled=fade(samples*np.float32(10**(gain_db/20)),sr)
    return levelled,before,gain_db
