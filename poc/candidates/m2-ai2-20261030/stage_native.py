#!/usr/bin/env python3
"""Stage pinned private session tooling with explicit M2 opt-ins; never launches."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile
import tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PIN='c798853db18e39504cc9ab565d3ef78292610155' # PR73, native ownership/resource guards

def exact(text,before,after):
    if text.count(before)!=1:raise ValueError('native harness source mismatch')
    return text.replace(before,after)

def patch_runner(text):
    text=exact(text,"preset='existing', cecil_p1=False):","preset='existing', cecil_p1=False, m2_combat=False):")
    text=exact(text,'        self.cecil_p1=cecil_p1','        self.cecil_p1=cecil_p1\n        self.m2_combat=m2_combat')
    text=exact(text,"                if self.cecil_p1:script+='bot_bCecilP1=1;\\n'", """                if self.cecil_p1:script+='bot_bCecilP1=1;\\n'
                if self.m2_combat:
                    script=re.sub(r'(?m)^bot_bEnabled\\s*=\\s*1\\s*;', 'bot_bEnabled=0;', script)
                    script+='bot_bCombatWeapon2=1;\\nbot_bCombatLead2=1;\\nbot_bCombatStrafe2=1;\\nbot_fCombatObservationAge=0;\\nbot_iSkillTier=5;\\nbot_iPersonality=2;\\nbot_bEnabled=1;\\n'""")
    text=exact(text,'cecil_p1=args.cecil_p1)','cecil_p1=args.cecil_p1,m2_combat=args.m2_combat)')
    text=exact(text,'                cecil_p1=args.cecil_p1,','                cecil_p1=args.cecil_p1,m2_combat=args.m2_combat,')
    text=exact(text,"    parser.add_argument('--cecil-p1',", "    parser.add_argument('--m2-combat',action='store_true',help='explicit private M2 weapon/lead/strafe and expert-duelist configuration')\n    parser.add_argument('--cecil-p1',")
    text=exact(text,"    if args.join_cancel_probe and", "    if config['max_bots']>2 or args.duration>300:\n        raise ValueError('M2 limited to one/two bots and <=300 seconds')\n    if args.m2_combat and (not args.cecil_p1 or config['strafe_scale']<=0):\n        raise ValueError('M2 smoke requires explicit P1 and positive strafe scale')\n    if args.execute and not args.m2_combat:\n        raise ValueError('M2 execution requires explicit --m2-combat')\n    if args.join_cancel_probe and")
    compile(text,'staged-M2-qualify_bot_sessions.py','exec')
    return text

def stage(output):
    output=Path(output).absolute()
    if output.exists() or output.is_symlink():raise ValueError('new output directory required')
    if not output.parent.is_dir():raise ValueError('existing output parent required')
    archive=subprocess.check_output(['git','-C',str(ROOT),'archive',PIN,'tools','poc/scripts/Phase1HumanAI.ini'])
    with tempfile.TemporaryDirectory(prefix='.m2-native-',dir=output.parent) as temp:
        root=Path(temp)/'source';root.mkdir()
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:tar.extractall(root,filter='data')
        runner=root/'tools/qualify_bot_sessions.py'
        runner.write_text(patch_runner(runner.read_text()))
        manifest={'qualified':False,'upstream':PIN,'stager_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                  'files_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(root.rglob('*')) if p.is_file()}}
        (root/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
        if output.exists() or output.is_symlink():raise ValueError('output appeared; refusing overwrite')
        root.rename(output)
    return output
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('output',type=Path);a=p.parse_args();print(stage(a.output))
