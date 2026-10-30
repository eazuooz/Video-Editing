"""Write only finite-batch Motion Canvas entry modules; no rendering or server."""
from pathlib import Path
from scoped_context import ROOT, BATCH, inventory


def main():
    _, rows = inventory(); base = ROOT / 'motion-canvas/src/projects/tech-ten-shorts-20261030'
    for row in rows:
        slug = row['slug']; folder = base / 'entries' / slug; folder.mkdir(parents=True, exist_ok=True)
        files = {
            'project.ts': "import {makeProject} from '@motion-canvas/core';\nimport scene from './scene?scene';\nexport default makeProject({name: " + repr(slug) + ", scenes: [scene]});\n",
            'scene.ts': "import timing from '../../../../../../projects/" + slug + "/production/visual-timing.json';\nimport config from '../../../../../../projects/" + slug + "/production/visual-config.json';\nimport {createTechScene} from '../../scene-factory';\nimport type {Timing, Config} from '../../model';\nexport default createTechScene(timing as Timing, config as unknown as Config);\n",
        }
        for name, contents in files.items():
            path = folder / name
            if path.exists() and path.read_text(encoding='utf8') != contents:
                raise RuntimeError('Preserve changed entry: ' + str(path))
            if not path.exists(): path.write_text(contents, encoding='utf8')
    print('Prepared exact ten scoped Motion Canvas entry routes.')


if __name__ == '__main__': main()
