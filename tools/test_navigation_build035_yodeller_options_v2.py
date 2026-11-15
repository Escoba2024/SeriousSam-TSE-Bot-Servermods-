"""Actual paired production option calls using the emitted Runner CLI."""
import argparse,ast,json,os,unittest
from pathlib import Path
FROZEN=Path('/srv/tse-nav20-035-yodeller600-diag0-root-v2-frozen-20261115')
FRESH=Path('/srv/tse-nav20-035-yodeller600-diag0-disabled-v2-20261115')

def read(p):
    with os.fdopen(os.open(p.resolve(strict=True),os.O_RDONLY|os.O_NOATIME|os.O_NOFOLLOW),'rb')as f:return f.read()

def production_options(root):
    runner=ast.parse(read(root/'run-a4.py'));parser=argparse.ArgumentParser()
    for n in ast.walk(runner):
        if (isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and n.func.attr=='add_argument' and
            isinstance(n.func.value,ast.Name) and n.func.value.id=='parser'):
            args=[ast.literal_eval(x)for x in n.args];kw={}
            for v in n.keywords:
                kw[v.arg]={'float':float,'int':int}[v.value.id]if v.arg=='type'else ast.literal_eval(v.value)
            parser.add_argument(*args,**kw)
    cli=parser.parse_args(['yodeller'])
    tree=ast.parse(read(root/'adapter_policy.py'));fun=next(n for n in tree.body if isinstance(n,ast.FunctionDef)and n.name=='options')
    scope={};exec(compile(ast.Module(body=[fun],type_ignores=[]),'actual-adapter-options','exec'),scope)
    hard={};exec(compile(read(root/'a4_hard_map_policy.py'),'actual-hardmap-options','exec'),hard)
    return cli,scope['options'],hard['options']

class Production(unittest.TestCase):
    def test_both_actual_options_accept_actual_final_cli(self):
        root=FRESH if FRESH.exists()else FROZEN
        cli,adapter,hard=production_options(root)
        self.assertEqual((cli.map,cli.seconds,cli.diagnostics),('yodeller',600,0))
        adapter(cli.map,cli.seconds,cli.diagnostics)
        hard(cli.map,cli.seconds,cli.diagnostics,json.loads(read(root/'map-catalog.json'))['maps'])

    def test_both_actual_production_functions_reject_other_windows(self):
        cli,adapter,hard=production_options(FRESH)
        catalog=json.loads(read(FRESH/'map-catalog.json'))['maps']
        cases=[('trouble',600,0),('yodeller',300,1),('yodeller',599,0),('yodeller',601,0),('yodeller',600,1),('yodeller',600,False),('yodeller',True,0),('yodeller',float('nan'),0),('yodeller',float('inf'),0)]
        for args in cases:
            with self.subTest(args=args),self.assertRaises(ValueError):adapter(*args)
            with self.subTest(args=args),self.assertRaises(ValueError):hard(*args,catalog)
        with self.assertRaises(ValueError):hard('yodeller',600,0,{})

    def test_actual_hardmap_nonoptions_functions_are_byte_ast_unchanged(self):
        import prepare_navigation_build035_yodeller as h
        def funcs(p):return {n.name:ast.dump(n,include_attributes=False)for n in ast.parse(read(p)).body if isinstance(n,ast.FunctionDef)and n.name!='options'}
        self.assertEqual(funcs(FRESH/'a4_hard_map_policy.py'),funcs(h.PARENT/'a4_hard_map_policy.py'))

if __name__=='__main__':unittest.main(verbosity=2)
