#!/usr/bin/env python3
"""Stage an explicit finite-ammo native duel harness; never launches it."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
HERE=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('m2_stage_base',HERE/'stage_native.py')
base=importlib.util.module_from_spec(s);s.loader.exec_module(base)

def stage(output,map_name='littletrouble'):
    maps={'littletrouble':('Little Trouble','DM_LittleTrouble.wld'),
          'redstation':('Red Station','RedStation.wld'),
          'hole':('Hole','Hole.wld'),
          'compound':('Compound','KuntaKinte.wld')}
    if map_name not in maps:raise ValueError('explicit known original Retail map required')
    query_name,level_name=maps[map_name]
    output=Path(output).absolute()
    if output.exists() or output.is_symlink():raise ValueError('new output directory required')
    if not output.parent.is_dir():raise ValueError('existing output parent required')
    with tempfile.TemporaryDirectory(prefix='.m2-duel-',dir=output.parent) as temp:
        root=base.stage(Path(temp)/'source')
        runner=root/'tools/qualify_bot_sessions.py';text=runner.read_text()
        text=base.exact(text,"choices=('existing','redstation')","choices=('existing','redstation','duel')")
        text=base.exact(text,"if preset not in ('existing','redstation'):","if preset not in ('existing','redstation','duel'):")
        text=base.exact(text,"observer_fps_cap=5,", "observer_fps_cap=20 if getattr(args,'preset','existing')=='duel' else 5,")
        text=base.exact(text,"                        raise RuntimeError('private Red Station preset did not reach native query')\n", "                        raise RuntimeError('private Red Station preset did not reach native query')\n                    if getattr(args,'preset','existing')=='duel' and state.get('mapname')!='Little Trouble':\n                        raise RuntimeError('private Little Trouble preset did not reach native query')\n")
        text=base.exact(text,"                configure_overlay(game,role)\n", "                configure_overlay(game,role)\n            elif self.preset=='duel':\n                from m2_duel_preset import configure_overlay\n                configure_overlay(game,role)\n")
        text=base.exact(text,"state.get('mapname')!='Little Trouble'", "state.get('mapname')!="+repr(query_name))
        compile(text,'M2-duel-runner','exec');runner.write_text(text)
        preset=(HERE/'m2_duel_preset.py').read_text()
        preset=base.exact(preset,'DM_LittleTrouble.wld',level_name)
        (root/'tools/m2_duel_preset.py').write_text(preset)
        manifest=json.loads((root/'SOURCE_MANIFEST.json').read_text())
        manifest['scenario']='ORIGINAL_RETAIL_LITTLE_TROUBLE_FINITE_AMMO_OWN_INPUT'
        manifest['map']=map_name
        if map_name!='littletrouble':manifest['scenario']='ORIGINAL_RETAIL_'+map_name.upper()+'_FINITE_AMMO_OWN_INPUT'
        manifest['duel_inputs_sha256']={name:hashlib.sha256((HERE/name).read_bytes()).hexdigest() for name in ('stage_duel.py','m2_duel_preset.py')}
        manifest['files_sha256']={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file() and p.name!='SOURCE_MANIFEST.json'}
        (root/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
        if output.exists() or output.is_symlink():raise ValueError('output appeared; refusing overwrite')
        root.rename(output)
    return output
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path)
    p.add_argument('--map',choices=('littletrouble','redstation','hole','compound'),default='littletrouble')
    a=p.parse_args();print(stage(a.output,a.map))
