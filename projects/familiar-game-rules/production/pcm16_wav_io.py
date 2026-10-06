"""Minimal PCM16 WAV I/O, using the stdlib and existing NumPy runtime."""
import wave
import numpy as np
def read(path,dtype='int16',always_2d=False):
    assert dtype=='int16'
    with wave.open(str(path),'rb') as f:
        assert f.getsampwidth()==2 and f.getcomptype()=='NONE'
        rate,channels=f.getframerate(),f.getnchannels()
        x=np.frombuffer(f.readframes(f.getnframes()),dtype='<i2').copy().reshape(-1,channels)
    if channels==1 and not always_2d:x=x[:,0]
    return x,rate
def write(path,x,rate,subtype='PCM_16'):
    assert subtype=='PCM_16' and x.dtype==np.dtype('int16')
    channels=1 if x.ndim==1 else x.shape[1]
    with wave.open(str(path),'wb') as f:
        f.setnchannels(channels);f.setsampwidth(2);f.setframerate(rate);f.writeframes(x.astype('<i2',copy=False).tobytes())
