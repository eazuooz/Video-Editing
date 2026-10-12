"""Seven evidenced caption-clearance repairs; inherited math and timing intact."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from teaching_revision_detailed_v1 import TeachingRevision
from teaching_revision_v2 import TeachingRevision as RetainedStorageRevision
from teaching_baseline_detailed_v2 import LectureScene


class CaptionClearance:
    def fixed(self, *items):
        for item in items:
            text = ''.join(getattr(item, 'text', '').split())
            children = ''.join(''.join(getattr(child, 'text', '').split())
                               for child in item.submobjects)
            position = None
            if self.sid in ('09a', '13a', '16a', '21a', '12'):
                if text == 'x:빨강y:초록z:파랑':
                    position = (-3.3, -1.8, 0)
                elif text == '몸에붙인세축':
                    position = (-3.3, -2.15, 0)
                elif self.sid == '12' and text == '큰몸체:부모주황부품:자식':
                    position = (-3.2, -2.15, 0)
            elif self.sid == '16':
                if children == 'xy↑z앞':
                    position = (-3.35, -1.8, 0)
                elif text == '오차를크게그린개념도':
                    position = (-3.35, -2.15, 0)
            elif self.sid == '18':
                position = {
                    '회전자유도=3': (0, -1.50, 0),
                    '한칸=float32성분4B': (0, -1.84, 0),
                    '성분수와회전자유도를구분': (0, -2.2, 0),
                }.get(text)
            if position is not None:
                item.move_to(position)
                self._clearance_seen.add(text or children)
        return super().fixed(*items)

    def construct(self):
        self._clearance_seen = set()
        super().construct()
        expected = ({'x:빨강y:초록z:파랑', '큰몸체:부모주황부품:자식'}
                    if self.sid == '12' else
                    {'xy↑z앞', '오차를크게그린개념도'} if self.sid == '16' else
                    {'회전자유도=3', '한칸=float32성분4B', '성분수와회전자유도를구분'}
                    if self.sid == '18' else
                    {'x:빨강y:초록z:파랑', '몸에붙인세축'})
        assert self._clearance_seen == expected, (self.sid, self._clearance_seen)


for sid in ('09a', '12', '13a', '16a', '21a'):
    globals()['DetailedScene' + sid] = type(
        'DetailedScene' + sid, (CaptionClearance, TeachingRevision),
        {'sid': sid, '__module__': __name__})
DetailedScene16 = type('DetailedScene16', (CaptionClearance, LectureScene),
                       {'sid': '16', 'slug': 'game-math-orientation-matrices',
                        '__module__': __name__})
DetailedScene18 = type('DetailedScene18', (CaptionClearance, RetainedStorageRevision),
                       {'sid': '18', '__module__': __name__})
