"""Measure current voice-only body headroom; never changes/encodes its sound."""
from pathlib import Path
import importlib.util,json,math,re,subprocess
H=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('v8_headroom_common',H/'audio-common.py');c=importlib.util.module_from_spec(s);s.loader.exec_module(c)
def main():
 c.validate();source=c.read(c.O/'tts-current.json');levels=c.read(c.O/'line-levels.json');assert source['sceneCount']==13 and levels['lineCount']==76
 concat=c.O/'source-body.ffconcat';rows=['ffconcat version 1.0']
 for scene in source['scenes']:
  file=c.R/scene['file'];assert c.sha(file)==scene['sha256'];assert "'"not in str(file)
  rows.append("file '"+file.as_posix()+"'")
 concat.write_text('\n'.join(rows)+'\n',encoding='utf8')
 command=['ffmpeg','-hide_banner','-nostdin','-threads','2','-filter_threads','2','-f','concat','-safe','0','-i',str(concat),
  '-af','aresample=48000,pan=stereo|c0=c0|c1=c0,loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']
 result=subprocess.run(command,cwd=c.R,capture_output=True);log=c.O/'source-headroom-measurement.log';log.write_bytes(result.stderr);assert result.returncode==0
 blocks=re.findall(r'\{\s*"input_i".*?\}',result.stderr.decode(errors='replace'),re.S);assert len(blocks)==1;measurement=json.loads(blocks[0])
 loud=float(measurement['input_i']);peak=float(measurement['input_tp']);gain=min(-16-loud,-2.3-peak)
 candidates=[]
 for row in levels['lines']:
  p=row['processedFloatPeak'];candidates.append(dict(scene=row['scene'],line=row['line'],takeFile=row['takeFile'],takeSha256=row['takeSha256'],
   sourceFrameMedianDbfs=row['before']['speechFrameMedianDbfs'],lineGainDb=row['gainDb'],postGainFrameMedianDbfs=row['after']['speechFrameMedianDbfs'],
   normalizedSamplePeakDbfs=20*math.log10(max(p,1e-12)),normalizedFloatPeak=p,takeRange=[row['startSample']/24000,row['endSample']/24000],
   status='Quantitative headroom ranking only. Not a spoken-content defect or listening approval.'))
 candidates.sort(key=lambda x:x['normalizedFloatPeak'],reverse=True)
 report=dict(revision='orientation-matrix-v8',inputs=dict(sourceReceiptSha256=c.sha(c.O/'tts-current.json'),lineLevelsSha256=c.sha(c.O/'line-levels.json'),implementationSha256=c.sha(Path(__file__))),
  sourceScenes=[dict(id=s['id'],file=s['file'],sha256=s['sha256'])for s in source['scenes']],measurement=measurement,
  currentBodyInputLufs=loud,currentBodyTruePeakDbtp=peak,proposedConstantGainDb=gain,forecastBodyLufs=loud+gain,forecastTruePeakDbtp=peak+gain,
  targetVoiceLufs=-16,targetBeforeMixTruePeakDbtp=-2.3,sourceBodySeconds=sum(s['seconds']for s in source['scenes']),
  paragraphPeakRanking=candidates,normalizedFloatPeaksAboveOne=sum(x['normalizedFloatPeak']>1 for x in candidates),
  method='All13 current scene WAVs concatenated at native1x; resampled48k and duplicated stereo for a discarded loudnorm analysis only. input_* are measured current source-body values; output_* are discarded filter output. No audio master encoded/modified.',
  limit='Voice-only body before frame padding/branding/game mix. Final mixer uses its actual placed48k source and remeasures. Per-paragraph sample peaks are not true peaks.',
  automaticRetakes=False,humanListening='pending')
 c.save(c.O/'source-headroom.json',report)
 print(json.dumps(dict(bodyLufs=loud,bodyTruePeak=peak,constantGainDb=gain,forecastLufs=loud+gain,peaksAboveOne=report['normalizedFloatPeaksAboveOne'],largest=candidates[:3])))
if __name__=='__main__':main()
