"""Read the failed concat timing; preserve all media and original execution."""
import importlib.util, subprocess
from pathlib import Path
p=Path(__file__).with_name('review-media-common-v15.py');s=importlib.util.spec_from_file_location('m',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
file=m.ROOT/'production/research/game-lighting-history/local/current-review-pair-v20/game-lighting-history-03.clean.mp4'
cmd=[str(m.FP),'-v','error','-show_entries','stream=codec_type,width,height,r_frame_rate,time_base,nb_frames,duration:format=duration','-of','json',str(file)]
probe=m.json.loads(subprocess.run(cmd,capture_output=True,text=True,check=True).stdout)
pc=[str(m.FP),'-v','error','-select_streams','v:0','-show_entries','packet=pts,dts,duration','-of','json',str(file)]
packets=m.json.loads(subprocess.run(pc,capture_output=True,text=True,check=True).stdout)['packets'];pts=sorted(x['pts']for x in packets)
delta=[v-i*1500 for i,v in enumerate(pts)];mismatches=[dict(frame=i,actualPts=v,expectedPts=i*1500,difference=v-i*1500)for i,v in enumerate(pts)if v!=i*1500]
r=dict(observedAt=m.stamp(),worker=m.worker(),input=dict(path=m.rel(file),sha256=m.sha(file)),probe=probe,probeCommand=cmd,packetCommand=pc,
 packetCount=len(packets),deltaMin=min(delta),deltaMax=max(delta),differingPts=len(mismatches),firstDifferences=mismatches[:10],lastDifferences=mismatches[-10:],
 roundedPresentationPtsContinuous=[round(x/1500)*1500 for x in pts]==list(range(0,93084*1500,1500)),
 roundedDecodePtsStrictlyIncreasing=all(round(packets[i]['dts']/1500)*1500>round(packets[i-1]['dts']/1500)*1500 for i in range(1,len(packets))),
 firstDecodePts=[x['dts']for x in packets[:6]],lastPackets=packets[-6:],allFinalPixelsReviewed=False)
out=m.PROD/'current-review-pair-pts-diagnostic-v20.json';assert not out.exists();m.save(out,r)
print(m.json.dumps({k:r[k]for k in ['packetCount','deltaMin','deltaMax','differingPts','roundedPresentationPtsContinuous','roundedDecodePtsStrictlyIncreasing','probe']}),flush=True)
