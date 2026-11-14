"""Cache only independently recorded, already inspected game animations for analysis."""
import subprocess
from pathlib import Path

from prepare import BATCH, HERE, WORK, read, save
from finish_episode import sha

FOOTAGE = BATCH / 'contrast-v5/footage'
BANKS = {
 'ringfit': {'file': FOOTAGE/'team-b/local/ringfit-warrior1.mp4', 'start': 16., 'duration': 3.,
             'crop': [90, 180, 350, 740], 'sha256': '9896d1d448d8c133ffa207e2fe8c6a15adfd25a24c5aa678ebc96de3e6621b9c',
             'evidence': FOOTAGE/'team-b/game-coverage.json', 'purpose': 'Existing in-game trainer animation: raised arms, body lean and planted legs.'},
 'acnh-face': {'file': FOOTAGE/'local/acnh-catch-expression.mp4', 'start': 10.5, 'duration': 3.,
              'crop': [730, 90, 420, 380], 'sha256': 'e6208d06ddd4f31c546e4cba0407c138f867b1b4ab70400b85ad61ae30e174de',
              'evidence': FOOTAGE/'team-b/game-coverage.json', 'purpose': 'Native face changes and blinking in the inspected fish presentation.'},
 'lune-face': {'file': FOOTAGE/'team-b/local/lune-clean-camp.mp4', 'start': 11.5, 'duration': 3.,
              'crop': [1040, 250, 1000, 850], 'sha256': 'dc41229a4bb9b82243f7d31328fd5767da6019de550fcce65ba6ef57a259448b',
              'evidence': FOOTAGE/'team-b/game-coverage.json', 'purpose': 'Native brows, eyelids and mouth, without a manually driven face rig.'},
 'luigi-face': {'file': FOOTAGE/'local/luigi-lobby.mp4', 'start': 31.5, 'duration': 3.,
               'crop': [420, 250, 640, 520], 'sha256': '82f808c7d2fa8d616359aa1f1d4cb5cf76f4399c1bb5138427d3340fc2416260',
               'evidence': FOOTAGE/'episode-A18-sources.json', 'purpose': 'Original head, eye and hand performance; rotations shown separately remain our principle diagram.'},
}


def main():
    records = {}
    for key, row in BANKS.items():
        assert sha(row['file']) == row['sha256']
        folder = WORK / 'game-banks' / key
        folder.mkdir(parents=True, exist_ok=True)
        x,y,w,h = row['crop']
        subprocess.run(['ffmpeg','-nostdin','-v','error','-y','-ss',str(row['start']),'-threads','2',
                        '-i',str(row['file']),'-vf',f'fps=60,crop={w}:{h}:{x}:{y}',
                        '-frames:v',str(round(row['duration']*60)),'-start_number','0',str(folder/'%06d.png')],check=True,
                       creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
        files=sorted(folder.glob('*.png'))
        assert len(files)==180
        records[key] = dict(row, file=str(row['file']), evidence=str(row['evidence']), folder=str(folder),
                            sourceKind='independent-gameplay used as explanation analysis',
                            frames=180, fps=60, imageHashes=[{'frame':n,'sha256':sha(files[n])} for n in (0,45,90,135,179)])
    save(WORK / 'game-banks/manifest.json', records)
    print('Four original-game animation banks ready for crop/phase inspection.', flush=True)


if __name__=='__main__':
    main()
