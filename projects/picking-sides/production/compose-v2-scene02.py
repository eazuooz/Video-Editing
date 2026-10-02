"""Preserve four existing explanation paragraphs byte-for-byte, add only new bridge."""
import hashlib,json,pathlib,wave
ROOT=pathlib.Path(__file__).resolve().parents[3]
BASE=ROOT/'projects/picking-sides/production/existing-game-replan'
old=ROOT/'shared/output/narration/picking-sides/qwen3-1.7b-balanced-v1/chunks/02-scene.wav'
bridge=ROOT/'shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2-bridge02/chunks/02-scene.wav'
out=ROOT/'shared/output/narration/picking-sides/qwen3-1.7b-balanced-v2/chunks/02-scene.wav'
def read(p):
    with wave.open(str(p),'rb') as f:return f.getparams(),f.readframes(f.getnframes())
a,pcm=read(old);b,new=read(bridge)
assert (a.nchannels,a.sampwidth,a.framerate)==(b.nchannels,b.sampwidth,b.framerate)==(1,2,24000)
count=round(29.175*a.framerate);prefix=pcm[:count*a.nchannels*a.sampwidth]
gap=bytes(round(.1*a.framerate)*a.nchannels*a.sampwidth)
combined=prefix+gap+new
if out.exists():raise RuntimeError('Composite already exists; inspect it instead of overwriting')
with wave.open(str(out),'wb') as f:f.setnchannels(a.nchannels);f.setsampwidth(a.sampwidth);f.setframerate(a.framerate);f.writeframes(combined)
_,saved=read(out);assert saved[:len(prefix)]==prefix
report={'source':str(old.relative_to(ROOT)),'bridge':str(bridge.relative_to(ROOT)),'out':str(out.relative_to(ROOT)),'originalAudioSha256':hashlib.sha256(old.read_bytes()).hexdigest(),'bridgeSha256':hashlib.sha256(bridge.read_bytes()).hexdigest(),'compositeSha256':hashlib.sha256(out.read_bytes()).hexdigest(),'preservedPrefixSeconds':29.175,'preservedPrefixSamples':count,'preservedPcmSha256':hashlib.sha256(prefix).hexdigest(),'prefixByteIdentical':True,'bridgeStartsAt':29.275,'duration':len(combined)/48000,'fullAsrAndBoundaryReview':'pending','humanListening':'pending'}
(BASE/'scene02-composite.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(json.dumps(report,ensure_ascii=False))
