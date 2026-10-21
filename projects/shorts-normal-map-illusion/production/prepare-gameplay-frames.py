"""Decode the inspected6.6s source once, at1x; no GPU/audio/old-output changes."""
from pathlib import Path
import hashlib,json,subprocess
P=Path(__file__).resolve().parents[1];R=P.parents[1];L=P/'production/local'
BIN=Path('C:/Users/1/AppData/Local/Microsoft/WinGet/Packages/Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe/ffmpeg-9.0-full_build/bin')
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def main():
 c=read(R/'shared/publishing/video-production-control.json');assert c.get('selectedShortVideo')==P.name and c.get('shortsDirectSelection',{}).get('selectedRevision')=='normal-map-v2-grid-rgb-deadcells'
 evidence=read(P/'sources/deadcells-v2.json');source=R/evidence['source']['file'];sha=hashlib.sha256(source.read_bytes()).hexdigest();assert sha==evidence['source']['sha256']
 decoded=json.loads(subprocess.check_output([str(BIN/'ffprobe.exe'),'-v','error','-select_streams','v:0','-show_entries','stream=width,height,r_frame_rate','-of','json',str(source)],text=True))['streams'][0]
 assert decoded['width']==1920 and decoded['height']==1080 and decoded['r_frame_rate']=='60/1'
 out=L/'native-gameplay-v2/deadCells';assert not out.exists(),'Preserve prior native frame extraction';out.mkdir(parents=True)
 subprocess.run([str(BIN/'ffmpeg.exe'),'-hide_banner','-loglevel','error','-ss','30.0','-i',str(source),'-map','0:v:0','-an','-vf','fps=60','-frames:v','396','-fps_mode','cfr','-start_number','0','-compression_level','1',str(out/'frame-%05d.png')],check=True)
 assert len(list(out.glob('frame-*.png')))==396
 receipt=dict(status='pass',source=evidence['source']['file'],sourceSHA256=sha,sourceStart=30.0,sourceEndExclusive=36.6,rate=1,fps=60,decodedSize=[1920,1080],frames=396,output=str(out.relative_to(R)).replace('\\','/'),originalOffsetSeconds=0,nativeAudioAdopted=False,audioDecision='Source soundtrack rights unverified; approved source-evidence decision retains our narration and rights-cleared BGM only.',purpose='Same-time full16:9 and source-pixel character enlargement. No normal-buffer/toggle measurement is inferred from final gameplay.')
 (out/'extraction.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(receipt))
if __name__=='__main__':main()
