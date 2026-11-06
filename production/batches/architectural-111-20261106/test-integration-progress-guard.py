"""CPU-only checks in disposable fixtures. Never invoke integration main()."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('integration_guard',HERE/'integrate-planning.py')
integration=importlib.util.module_from_spec(spec)
spec.loader.exec_module(integration)


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


def snapshot(root):
    return {p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*') if p.is_file()}


class ProgressGuard(unittest.TestCase):
    def fixture(self,root):
        here=root/'production/batches/architectural-111-20261106'
        media=root/'media'
        # Reuse only the exact selected IDs/paths, never live mutable state.
        rows=[{key:row[key] for key in ('topicId','project','slug')}
              for row in integration.read(HERE/'batch.json')['projects']]
        self.assertEqual(len(rows),111)
        for row in rows:
            row.update(status='source-mapped-script-draft',productionComplete=False,
                       humanApproval=False,platformStatus='not-uploaded')
            folder=(root/row['project']).parent
            write(root/row['project'],{'status':'source-mapped-script-draft'})
            write(folder/'checkpoint.json',dict(stage='source-mapped-script-draft',
                  voiceGenerated=False,editableUnityScenesSaved=[],
                  finalOutputsVerified=False,humanReview='not-delivered',
                  completedStages=[],platformActions=[]))
        batch=dict(batchId='architectural-111-20261106',projects=rows,
                   scriptDraftCount=111,completedLocalReviewCount=0)
        write(here/'batch.json',batch)
        write(here/'checkpoint.json',dict(completedVoiceCount=0,completedLocalReviewCount=0))
        write(here/'worklist.json',{'rows':rows})
        first=(root/rows[0]['project']).parent
        output='shared/output/architectural-111-20261106/03-02/voice-v1'
        write(first/'voice-manifest.json',dict(preparationState='manifest-only; no voice synthesized',
                                              tts={'outputDir':output}))
        write(here/'first-unity-preparation.json',dict(project='capture-project',
              actualSceneFilesSaved=False,intendedScenes=['Assets/03-02.unity']))
        write(media/'first-native-progress.json',dict(status='waiting-for-resources',
                                                       gpuStarted=False,completed=False))
        return here,media,rows,first,root/output

    def check(self,mutate=None,refused=False):
        with tempfile.TemporaryDirectory(prefix='yamyam-integration-guard-') as temp:
            root=Path(temp);here,media,rows,first,voice=self.fixture(root)
            if mutate:mutate(root,here,media,rows,first,voice)
            before=snapshot(root)
            if refused:
                with self.assertRaisesRegex(RuntimeError,'refused before writes'):
                    integration.assert_preproduction_only(root=root,here=here,media=media)
            else:
                result=integration.assert_preproduction_only(root=root,here=here,media=media)
                self.assertEqual(result['projectsChecked'],111)
                self.assertEqual(result['writes'],0)
            self.assertEqual(before,snapshot(root),'Read-only guard mutated a fixture')

    def test_all_111_drafts_and_prepared_manifests_allowed(self):
        self.check()

    def test_completed_batch_count_rejected_without_mutation(self):
        def mutate(root,here,*_):
            value=integration.read(here/'batch.json');value['completedLocalReviewCount']=1
            write(here/'batch.json',value)
        self.check(mutate,True)

    def test_voice_checkpoint_or_pcm_rejected_without_mutation(self):
        for kind in ['checkpoint','pcm','batch-count']:
            with self.subTest(kind=kind):
                def mutate(root,here,media,rows,first,voice):
                    if kind=='pcm':
                        voice.mkdir(parents=True);(voice/'narration.wav').write_bytes(b'preserve existing PCM')
                    elif kind=='batch-count':
                        write(here/'checkpoint.json',{'completedVoiceCount':1})
                    else:
                        cp=integration.read(first/'checkpoint.json');cp['voiceGenerated']=True
                        write(first/'checkpoint.json',cp)
                self.check(mutate,True)

    def test_saved_native_scene_proof_or_started_worker_rejected(self):
        for kind in ['checkpoint','scene','proof','worker','partial-capture']:
            with self.subTest(kind=kind):
                def mutate(root,here,media,rows,first,voice):
                    if kind=='checkpoint':
                        cp=integration.read(first/'checkpoint.json')
                        cp['editableUnityScenesSaved']=['Assets/03-02.unity']
                        write(first/'checkpoint.json',cp)
                    elif kind=='scene':
                        scene=root/'capture-project/Assets/03-02.unity'
                        scene.parent.mkdir(parents=True);scene.write_bytes(b'preserve saved scene')
                    elif kind=='proof':write(here/'first-native-evidence.json',{'status':'native-verified'})
                    elif kind=='worker':
                        write(media/'first-native-progress.json',{'gpuStarted':True,'completed':False})
                    else:
                        image=media/rows[0]['slug']/'native-v1/narrow/top/00001.jpg'
                        image.parent.mkdir(parents=True);image.write_bytes(b'preserve partial capture')
                self.check(mutate,True)

    def test_completed_output_rejected_without_mutation(self):
        def mutate(root,here,media,rows,*_):
            output=root/'output'/rows[0]['slug']/'captioned.mp4'
            output.parent.mkdir(parents=True);output.write_bytes(b'preserve existing master')
        self.check(mutate,True)

    def test_human_review_and_platform_actions_rejected_without_mutation(self):
        for kind in ['review','approval','platform']:
            with self.subTest(kind=kind):
                def mutate(root,here,media,rows,first,voice):
                    cp=integration.read(first/'checkpoint.json')
                    if kind=='review':cp['humanReview']='approved-exact-master-sha'
                    elif kind=='approval':cp['humanApproval']=True
                    else:cp['platformActions']=[{'action':'private-upload','videoId':'existing-id'}]
                    write(first/'checkpoint.json',cp)
                self.check(mutate,True)

    def test_later_status_without_completion_flag_rejected(self):
        def mutate(root,here,media,rows,first,voice):
            write(first/'project.json',{'status':'voice-generated-awaiting-render'})
        self.check(mutate,True)

    def test_html_links_only_declared_final_review_and_retains_current_six_ko_en_draft(self):
        with tempfile.TemporaryDirectory(prefix='yamyam-worklist-html-') as temp:
            root=Path(temp);here=root/'batch';media=root/'media';here.mkdir();media.mkdir()
            folder=media/'review & 한글';folder.mkdir()
            final={key:str(folder/name) for key,name in [('index','index.html'),('captioned','captioned.mp4'),('cover','cover.png')]}
            for path in final.values():Path(path).write_bytes(b'disposable fixture only')
            draft=dict(topicId='03.02',narrationKo=[f'현재 한국어 문단 {i}' for i in range(1,7)],
                paragraphsEn=[f'Current English paragraph {i}' for i in range(1,7)],glossary=[])
            relative='projects/fixture/narration-draft.json';write(root/relative,draft)
            row=dict(topicId='03.02',order=1,chapterName='장면',printPages='1',title='검수본',
                narrationDraft=relative,productionComplete=True,humanApproval=False,localFinalReview=final)
            cp=dict(selectedFirstTopic='03.02',scriptDraftCount=111,completedLocalReviewCount=1)
            before=snapshot(root);unchanged=copy.deepcopy((row,cp))
            with patch.multiple(integration,ROOT=root,HERE=here,MEDIA=media):
                integration.build_html({},[row],{},cp,write_delivery=False)
                page=(here/'worklist.html').read_text(encoding='utf8')
                for key in final:self.assertIn(integration.html.escape(Path(final[key]).resolve().as_uri(),quote=True),page)
                self.assertIn('<video controls preload="none"',page)
                self.assertIn('대본 초안 · 한영 6문단',page)
                for paragraph in draft['narrationKo']+draft['paragraphsEn']:self.assertIn(paragraph,page)
                self.assertNotIn('아직 완성 영상 플레이어가 아닙니다.',page)
                self.assertFalse((media/'delivery').exists())
                self.assertEqual(unchanged,(row,cp))
                after=snapshot(root);after.pop('batch/worklist.html')
                self.assertEqual(before,after)
                pending=copy.deepcopy(row);pending.pop('localFinalReview');pending['productionComplete']=False
                integration.build_html({},[pending],{},dict(cp,completedLocalReviewCount=0),write_delivery=False)
                page=(here/'worklist.html').read_text(encoding='utf8')
                self.assertNotIn('<video ',page)
                self.assertIn('아직 완성 영상 플레이어가 아닙니다.',page)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProgressGuard))
    report=dict(scope='Only integrate-planning.py preproduction write guard',
        testsRun=result.testsRun,successful=result.wasSuccessful(),
        failures=[str(x[0]) for x in result.failures],errors=[str(x[0]) for x in result.errors],
        fixtures='Disposable temporary 111-project fixtures; before/after file SHA256 equality checked on every case.',
        mainExecuted=False,realProjectFilesMutated=False,gpuUsed=False,
        integratorSHA256=hashlib.sha256((HERE/'integrate-planning.py').read_bytes()).hexdigest(),
        regressionSHA256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        rejected=['completed counts','voice flags/count/PCM','saved native scene/flag/proof',
                  'started native worker/partial capture','completed output','human review/approval',
                  'platform action','later or unknown project state'],
        remainingBoundary='This helper still initializes drafts and zero production counts only after draft-only guard passes. It is not a progress-preserving merge. Do not call during production; a later merge must explicitly preserve every artifact and approval. The guard rechecks before its first write, but is not a cross-process lock.')
    write(HERE/'integration-progress-guard-audit.json',report)
    raise SystemExit(0 if result.wasSuccessful() else 1)
