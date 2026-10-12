"""Only the evidenced 06a fixed labels move; inherited teaching is preserved."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from teaching_revision_detailed_v1 import TeachingRevision


class DetailedScene06a(TeachingRevision):
    sid = '06a'

    def fixed(self, *items):
        for item in items:
            text = ''.join(getattr(item, 'text', '').split())
            if text == 'x:빨강y:초록z:파랑':
                item.move_to([-3.3, -1.8, 0])
                self._clearance_seen.add(text)
            elif text == '몸에붙인세축':
                item.move_to([-3.3, -2.15, 0])
                self._clearance_seen.add(text)
        return super().fixed(*items)

    def construct(self):
        self._clearance_seen = set()
        super().construct()
        assert self._clearance_seen == {'x:빨강y:초록z:파랑', '몸에붙인세축'}
