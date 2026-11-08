"""Measured sprite support-foot displacement; annotated visual landmarks, not mocap."""
from pathlib import Path
import json,hashlib,math
import cv2,numpy as np
from PIL import Image,ImageDraw
H=Path(__file__).resolve().parent;P=H.parents[1];R=P.parents[1];SRC=R/'sites/yamyam-cartographers-room/dist/assets/motions';OUT=P/'production/local/room-v3/pixel-clean'
rows=[]
for i in range(8):
 f=SRC/f'walk-{i:02}.png';a=np.array(Image.open(f).convert('RGBA'));mask=(a[144:,:,3]>=128).astype(np.uint8);n,labels,stats,cent=cv2.connectedComponentsWithStats(mask);feet=[]
 for k in range(1,n):
  if stats[k,4]<15:continue
  yy,xx=np.nonzero(labels==k);bottom=yy.max();foot=xx[yy>=bottom-1];feet.append({'x':float(np.median(foot)),'y':int(bottom+144),'pixelCount':int(stats[k,4])})
 feet.sort(key=lambda f:f['x']);rows.append({'frame':i,'sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'visibleLowerFootRegions':feet})
# The supported foot swaps sides visually between passing and up poses. Identity
# was read from the inspected eight images; no detector confidence is invented.
trackA=[rows[0]['visibleLowerFootRegions'][-1],rows[1]['visibleLowerFootRegions'][-1],rows[2]['visibleLowerFootRegions'][-1],rows[3]['visibleLowerFootRegions'][0],rows[4]['visibleLowerFootRegions'][0]]
trackB=[rows[4]['visibleLowerFootRegions'][-1],rows[5]['visibleLowerFootRegions'][-1],rows[6]['visibleLowerFootRegions'][0],rows[7]['visibleLowerFootRegions'][0],rows[0]['visibleLowerFootRegions'][0]]
scale=.75;halfA=(trackA[0]['x']-trackA[-1]['x'])*scale;halfB=(trackB[0]['x']-trackB[-1]['x'])*scale;full=halfA+halfB
hip=[(62,89),(61,91),(60,87),(63,89),(63,90)];knee=[(78,117),(78,120),(61,117),(50,119),(47,117)];ankle=[(89,144),(76,143),(63,143),(40,143),(33,143)]
legs=[{'frame':i,'hip':hip[i],'knee':knee[i],'ankle':ankle[i],'sole':trackA[i],'jointChainPixels':math.dist(hip[i],knee[i])+math.dist(knee[i],ankle[i]),'verticalHipToSole':trackA[i]['y']-hip[i][1]} for i in range(5)]
data={'method':'inspect registered original128×176 frames; identify stance leg visually; binary-alpha lower-foot connected regions; median x of bottom2 contour rows; manual hip/knee/ankle guides','notMotionCapture':True,'uncertainty':'Generated2D poses have approximate anatomy and changing sole shape; contact centroids are visual estimates, ±2 source pixels. No physical meters inferred.','sourceCanvas':[128,176],'sourceGameScale':scale,'newCanvas':[96,132],'newGameScale':1,'supportTrackA':trackA,'supportTrackB':trackB,'halfStrideGamePixels':[halfA,halfB],'measuredFullCycleGamePixels':full,'recommendedFullCycleGamePixels':82,'currentOldFullCycleGamePixels':38,'oldCycleRateExcessFactor':full/38,'recommendedPhase':'walkPhase = totalTravelDistance / 82; frame = floor(fract(walkPhase)*8)','speedOptions':{'preserve39GamePxPerSecond':{'cycleSeconds':82/39,'effectiveFps':39/82*8},'recommended62GamePxPerSecond':{'cycleSeconds':82/62,'effectiveFps':62/82*8}},'doNotChangePlaybackWithClockIndependently':True,'legLandmarks':legs,'meanJointChainWorldPixels':float(np.mean([x['jointChainPixels'] for x in legs]))*scale,'meanVerticalHipToSoleWorldPixels':float(np.mean([x['verticalHipToSole'] for x in legs]))*scale,'frames':rows}
native=[]
for i in range(8):
 a=np.array(Image.open(OUT/'96x132/motions'/f'walk-{i:02}.png').convert('RGBA'))
 n,labels,stats,cent=cv2.connectedComponentsWithStats((a[108:,:,3]>=128).astype(np.uint8));feet=[]
 for k in range(1,n):
  if stats[k,4]<10:continue
  yy,xx=np.nonzero(labels==k);bottom=yy.max();feet.append({'x':float(np.median(xx[yy>=bottom-1])),'y':int(bottom+108)})
 native.append(sorted(feet,key=lambda f:f['x']))
half_native=[native[0][-1]['x']-native[4][0]['x'],native[4][-1]['x']-native[0][0]['x']];stride=round(sum(half_native))
data['nativePixelRecheck']={'size':[96,132],'feet':native,'halfStrides':half_native,'fullStride':sum(half_native),'recommendedRoundedDistance':stride}
data['recommendedFullCycleGamePixels']=stride;data['recommendedPhase']=f'walkPhase = totalTravelDistance / {stride}; frame = floor(fract(walkPhase)*8)'
data['speedOptions']={f'{"recommended" if speed==62 else "preserve"}{speed}GamePxPerSecond':{'cycleSeconds':stride/speed,'effectiveFps':speed/stride*8} for speed in [39,62]}
(H/'walk-distance-measurement.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
canvas=Image.new('RGB',(2048,960),(12,18,20));d=ImageDraw.Draw(canvas)
for i in range(8):
 im=Image.open(SRC/f'walk-{i:02}.png').convert('RGBA').crop((0,70,128,176)).resize((512,424),Image.Resampling.NEAREST);x=(i%4)*512;y=(i//4)*480;canvas.paste(im,(x,y+36),im)
 foot=trackA[i] if i<5 else trackB[i-4];fx=x+foot['x']*4;fy=y+36+(foot['y']-70)*4;d.line((fx-24,fy,fx+24,fy),fill='#ffe075',width=4);d.ellipse((fx-7,fy-7,fx+7,fy+7),outline='#ffe075',width=3)
 d.text((x+12,y+8),f"frame {i} / supported sole x={foot['x']} y={foot['y']}",fill='white')
 if i<5:
  pts=[(x+pt[0]*4,y+36+(pt[1]-70)*4) for pt in [hip[i],knee[i],ankle[i]]];d.line(pts,fill='#76dac4',width=4)
  for px,py in pts:d.ellipse((px-5,py-5,px+5,py+5),fill='#76dac4')
canvas.save(OUT/'walk-contact-measurement.png');print(json.dumps({k:data[k] for k in ['halfStrideGamePixels','measuredFullCycleGamePixels','meanJointChainWorldPixels','meanVerticalHipToSoleWorldPixels','speedOptions']}))
# Separate proposed integration manifest; does not modify the deployed site.
# The initial integration manifest is already consumed by the game. Do not
# regenerate it from the now-mutated website or double-prefix native paths.
