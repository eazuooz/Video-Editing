"""Make a separate editable repaired pilot script; preserve v1 and its review."""
from pathlib import Path
root=Path(__file__).resolve().parents[3]
batch=root/'production/batches/unpublished-teaching-clarity-revision'
src=batch/'render-orientation-observation-pilot-v1.py'
target=batch/'render-orientation-observation-pilot-v2.py'
assert not target.exists()
text=src.read_text('utf8').replace('observation-pilot-v1','observation-pilot-v2').replace('observation-pilot-execution-v1','observation-pilot-execution-v2').replace('observation-silhouette-track-v1','observation-silhouette-track-v2')
changes={
"label(d,(64,28),'Superflight · NCR Gameplay · 서로 다른 순간의 화면 관찰','#ffffff',22)":"label(d,(64,28),'Superflight · NCR Gameplay · 화면 관찰','#ffffff',22)",
"'청록: 보이는 몸 윤곽과 그 중심'":"'청록: 보이는 윤곽의 화면 위치'",
"if frame>=100 and t['anisotropy']>=1.35:\n            a,b=t['axisEnds'];line(d,a,b,RED,5)\n            label(d,(64,242),'빨강: 윤곽의 긴 쪽 · 화면 기울기',RED)":"if frame>=100 and t.get('previousScreenCentroid') is not None:\n            arrow(d,t['previousScreenCentroid'],t['centroid'],RED,5)\n            label(d,(64,242),'빨강: 0.5초 동안의 화면 위치 변화',RED)",
"label(d,(64,810),'관찰한 픽셀 ≠ 게임 내부의 월드축','#ffffff',27)\n    label(d,(64,855),'윤곽은 자세의 단서입니다. 정확한 3D 회전은 별도 모형으로 계산합니다.','#ffffff',25)":"label(d,(64,810),'화면 위치에는 카메라의 움직임도 함께 나타납니다.','#ffffff',27)\n    label(d,(64,855),'몸의 3D 자세는 다음 모형에서 세 축으로 설명합니다.','#ffffff',25)",
"mask=(crop.mean(2)<68)&(crop.max(2)-crop.min(2)<45)":"mask=(crop.mean(2)<83)&(crop.max(2)-crop.min(2)<50)&((crop[:,:,0]-crop[:,:,2])>2)\n                mask=ndimage.binary_closing(mask,structure=np.ones((3,3)),iterations=1)",
"not 350<=sizes[j]<=8500":"not 100<=sizes[j]<=8500",
"tracks.append(t);ep.stdin.write(drawing(im,frame,t).tobytes())":"t['previousScreenCentroid']=tracks[frame-30]['centroid'] if frame>=30 and visible and tracks[frame-30]['visible'] else None\n                t['screenDisplacementPixels']=[round(center[k]*3-t['previousScreenCentroid'][k],2) for k in range(2)] if t['previousScreenCentroid'] is not None else None\n                tracks.append(t);ep.stdin.write(drawing(im,frame,t).tobytes())",
"method='Dark connected visible silhouette, proximity selection, image centroid and principal line; invisible observations are hidden'":"method='Brown/dark silhouette with local closing, proximity selection and image centroid. Red vector is centroid(t)-centroid(t-0.5s), in image pixels including camera effects. Invalid observations are hidden.'"
}
for old,new in changes.items():
    assert old in text,old
    text=text.replace(old,new)
target.write_text(text,'utf8')
print('Separate v2 script prepared; v1 unchanged. No render performed by this preparation.')
