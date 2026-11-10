"""Find independent source candidates. Search results require separate inspection and rights evidence."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import subprocess

HERE = Path(__file__).resolve().parent
QUERIES = {
    'DS02': ['Super Mario Bros 2 Luigi Toad LongplayArchive', 'Super Smash Bros Ultimate gameplay royalty free Mario Bowser'],
    'DS03': ['Metroid NES 1080p 60 LongplayArchive', "Ghosts 'n Goblins arcade longplay 1080p Capcom"],
    'DS04': ['Final Fight arcade LongplayArchive', 'Smash Ultimate Marth sword tipper 1080p creative commons gameplay'],
    'DS05': ['Super Mario 64 LongplayArchive', 'Kirby Air Ride 1080p LongplayArchive', 'Armored Core 6 quick boost dodging no commentary 1080p'],
    'DS06': ['Kid Icarus Uprising LongplayArchive no commentary', 'Animal Crossing New Horizons LongplayArchive fly island loading'],
    'DS07': ['Mario Bros arcade original 1080p LongplayArchive', 'Kirby Air Ride 1080p LongplayArchive', 'Kid Icarus Uprising land battle 1080p LongplayArchive'],
    'DS08': ['Smash Ultimate Fox Illusion ledge Fox Falcon Kick 1080p', 'Mega Man 2 LongplayArchive'],
    'DS09': ['Shiren the Wanderer LongplayArchive dungeon map', 'Forza Horizon 5 racing line royalty free gameplay'],
    'DS10': ['Meteos Nintendo DS LongplayArchive 1080p', 'Super Smash Bros Ultimate World of Light LongplayArchive'],
    'DS11': ['Super Smash Bros Ultimate control settings stick sensitivity training dash 1080p', 'Kid Icarus Uprising land battle LongplayArchive'],
    'DS12': ['Smash Bros 64 break the targets gameplay LongplayArchive', 'Cuphead tutorial LongplayArchive'],
    'DS13': ['Super Smash Bros Ultimate Hero command selection royalty free footage', 'Slay the Spire LongplayArchive gameplay 1080p'],
    'DS14': ['Mario Kart 8 Deluxe royalty free gameplay item comeback', 'Mario Kart 8 Deluxe LongplayArchive 1080p'],
    'DS15': ['Super Smash Bros Ultimate Mario mirror match 1080p', 'Street Fighter 6 Marisa Dhalsim creative commons gameplay 1080p'],
    'DS16': ['No Man Sky Worlds update Hello Games gameplay official', 'Cyberpunk 2077 patch 2.0 CD Projekt Red gameplay update'],
    'DS17': ['Resident Evil PS1 LongplayArchive', 'The Legend of Zelda NES LongplayArchive', 'Super Mario World key keyhole LongplayArchive'],
    'DS18': ["Kirby's Dream Land Shotzo Game Boy Gameplay For Editors", 'Smash Ultimate Pyra Blazing End 1080p Creative Commons gameplay'],
}


def search(query):
    run = subprocess.run(['yt-dlp', '--ignore-config', '--flat-playlist', '--dump-single-json', '--no-warnings',
                          '--socket-timeout', '10', '--extractor-retries', '1', f'ytsearch3:{query}'],
                         capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
    if run.returncode:
        return {'query': query, 'status': 'metadata-query-failed'}
    videos = [{key: row.get(key) for key in ('id', 'title', 'channel', 'duration')}
              for row in json.loads(run.stdout).get('entries', []) if row and row.get('id')]
    return {'query': query, 'videos': videos, 'approved': False}


def main():
    batch = json.loads((HERE / 'batch.json').read_text(encoding='utf-8'))
    out = Path(batch['mediaRoot']) / 'footage/candidate-discovery.json'
    queries = list(dict.fromkeys(q for values in QUERIES.values() for q in values))
    with ThreadPoolExecutor(max_workers=3) as pool:
        found = {r['query']: r for r in pool.map(search, queries)}
    result = {key: [found[q] for q in values] for key, values in QUERIES.items()}
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(len(result), 'episodes with independently searchable source candidates', flush=True)


if __name__ == '__main__':
    main()
