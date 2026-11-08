"""Use the actual first UE renders to align the visible support sole with its floor.

This is orthographic image-to-height alignment, not a center-of-mass simulation.
Original joint rotations and relative pose are unchanged; only root Z is fixed.
"""
from sources import *
LOCAL=B/'local/contrast-v5/a08-cumulative'
def main():
    receipt=read(LOCAL/'capture-receipt.json');receipt['definitionHashes']={k:sha(LOCAL/'poses'/(k+'.json'))for k in receipt['keys']}
    (LOCAL/'capture-receipt.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),'utf8')
    result={'basis':'Observed orange sole pixels in actual UE capture; compare with initial unmodified mannequin sole y=901. Same 450 cm orthographic width.',
            'screenPixelsPerCm':1920/450,'targetSoleY':901,'notMeasuredPhysics':True,'keys':{}}
    for key in ('stance','overview'):
        rows=[]
        for n in range(180):
            p=LOCAL/'frames'/key/f'{n:06d}.png'
            with Image.open(p)as im:a=np.asarray(im.convert('RGB'))[700:,960:].astype('int16')
            mask=(a[:,:,0]>a[:,:,1]+22)&(a[:,:,1]>a[:,:,2]+12)&(a[:,:,0]>120)
            yy,xx=np.nonzero(mask);assert len(yy)>100
            bottom=int(yy.max()+700);shift=max(0,(bottom-901)/(1920/450))
            rows.append({'frame':n,'observedSoleY':bottom,'rootDeltaZCm':shift,'sourceFrameSha256':sha(p)})
        result['keys'][key]=rows
    (H/'a08-ground-calibration.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),'utf8');print('Calibrated actual sole pixels; no replacement capture yet')
if __name__=='__main__':main()
