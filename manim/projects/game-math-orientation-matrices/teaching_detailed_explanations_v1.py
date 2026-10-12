"""Scoped scene classes only; no original lesson edits."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from teaching_baseline_detailed_v1 import LectureScene
from teaching_revision_detailed_v1 import TeachingRevision
DetailedScene03=type('DetailedScene03',(LectureScene,),{'sid':'03','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene04=type('DetailedScene04',(LectureScene,),{'sid':'04','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene06=type('DetailedScene06',(LectureScene,),{'sid':'06','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene07=type('DetailedScene07',(LectureScene,),{'sid':'07','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene09=type('DetailedScene09',(LectureScene,),{'sid':'09','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene10=type('DetailedScene10',(LectureScene,),{'sid':'10','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene13=type('DetailedScene13',(LectureScene,),{'sid':'13','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene15=type('DetailedScene15',(LectureScene,),{'sid':'15','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene16=type('DetailedScene16',(LectureScene,),{'sid':'16','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene21=type('DetailedScene21',(LectureScene,),{'sid':'21','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene22=type('DetailedScene22',(LectureScene,),{'sid':'22','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene06a=type('DetailedScene06a',(TeachingRevision,),{'sid':'06a','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene09a=type('DetailedScene09a',(TeachingRevision,),{'sid':'09a','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene13a=type('DetailedScene13a',(TeachingRevision,),{'sid':'13a','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene16a=type('DetailedScene16a',(TeachingRevision,),{'sid':'16a','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene21a=type('DetailedScene21a',(TeachingRevision,),{'sid':'21a','slug':'game-math-orientation-matrices','__module__':__name__})
DetailedScene12=type('DetailedScene12',(TeachingRevision,),{'sid':'12','slug':'game-math-orientation-matrices','__module__':__name__})
