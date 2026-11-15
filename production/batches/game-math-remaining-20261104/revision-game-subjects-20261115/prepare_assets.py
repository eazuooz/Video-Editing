import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'production/batches/animation-18-20261031/research/A10/ocr-deps'))
import cv2
import numpy as np
HERE=Path(__file__).resolve().parent

def main():
    assets=HERE/'local/assets';assets.mkdir(exist_ok=True)
    for key,box in [('M24-004',(870,185,143,220)),('M25-002',(788,440,425,486)),('M28-001',(588,320,635,490)),('M26-001',(844,419,244,230))]:
        im=cv2.imread(str(HERE/'local'/f'{key}-source.png'));x,y,w,z=box;pad=24;crop=im[y-pad:y+z+pad,x-pad:x+w+pad].copy();mask=np.zeros(crop.shape[:2],np.uint8);bg=np.zeros((1,65),np.float64);fg=bg.copy()
        cv2.grabCut(crop,mask,(pad,pad,w,z),bg,fg,7,cv2.GC_INIT_WITH_RECT)
        alpha=np.where((mask==1)|(mask==3),255,0).astype(np.uint8)
        a=np.dstack([crop,alpha]);cv2.imwrite(str(assets/f'{key}.png'),a);print(key,crop.shape)

if __name__=='__main__':main()
