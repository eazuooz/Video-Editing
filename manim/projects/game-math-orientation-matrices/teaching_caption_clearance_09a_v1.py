"""Prepared EX09a label clearance repair; keep original scene and audio intact."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from teaching_revision_detailed_v1 import TeachingRevision


class CaptionClearanceDetailedScene09a(TeachingRevision):
    sid = '09a'

    def fixed(self, *items):
        for item in items:
            text_key = ''.join(getattr(item, 'text', '').split())
            if text_key == 'x:빨강y:초록z:파랑':
                item.move_to([-3.3, -1.8, 0])
                self._clearance_world_legend = True
            elif text_key == '몸에붙인세축':
                item.move_to([-3.3, -2.15, 0])
                self._clearance_body_label = True
        return super().fixed(*items)

    def construct(self):
        super().construct()
        assert getattr(self, '_clearance_world_legend', False)
        assert getattr(self, '_clearance_body_label', False)
