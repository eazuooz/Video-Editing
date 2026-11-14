"""Map every affected comparison back to the exact current narration and source."""
import sys

from prepare import BATCH, HERE, ROOT, read, save
from assemble_delivery import srt


def main():
    previous = BATCH / 'contrast-v5/review-notes-20261110'
    sys.path.insert(0, str(previous))
    import paint_replacements
    from config import EPISODES
    episodes = read(HERE / 'plan.json')['episodes']
    paint_replacements.EPISODES = {row['id']: set(EPISODES[row['id']][2]) for row in episodes
                                  if row['id'] in EPISODES and row['id'] != 'A06'}
    audit = []
    for row in episodes:
        ep = row['id']
        if ep in ('A03', 'A06'):
            audit.append({'id': ep, 'special': 'Existing topic-specific stage layout' if ep == 'A03'
                          else 'User selected the existing A06 demonstration as the quality reference.'})
            continue
        edl = read(BATCH / 'contrast-v5/local/explanation-assembly' / ep / 'edl.json')
        assert edl['frames'] == row['baseline']['frames']
        spans = paint_replacements.classify(ep, edl)
        ko_file = next(f['path'] for f in row['baseline']['files'] if f['kind'] == 'ko.srt')
        captions = srt(ROOT / ko_file)
        for span in spans:
            span['narration'] = [text.replace('\n', ' ') for a, b, text in captions
                                 if a * 60 < span['end'] and b * 60 > span['start']]
            span['requiresNativeMotionReview'] = True
        audit.append({'id': ep, 'intervals': spans})
    save(HERE / 'motion-audit.json', {'episodes': audit, 'status': 'mapped-to-current-final-clock'})
    for episode in audit:
        print(episode['id'], len(episode.get('intervals', [])), 'comparison intervals')


if __name__ == '__main__':
    main()
