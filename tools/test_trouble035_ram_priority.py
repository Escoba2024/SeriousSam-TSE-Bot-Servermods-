"""Pure evidence predicates, not a reimplementation of BotSupplyTick."""
import copy
import unittest
from trouble035_ram_priority import priority_status

class Priority(unittest.TestCase):
    def fixture(self):
        binding=dict(status='BOUND_SOURCE_LIFE',local=1,native_spawn=2.5)
        b=dict(key=[0,'botA',1,7,3,20],binding=binding,
            decision=dict(fields=dict(input=[1,3,3,100,0,7.9],item=[220,220],goal=[27,27],attempt=[10,10],deadline=[30,30])),
            arbitration=dict(fields=dict(refresh=[1,0])))
        d=dict(role='botA',typed=dict(local=1,tick=20,actor=7,gen=[3,3],exit_actor=7,life_link=1,supply=[1,1,1,1,15,0,0,0]))
        goal=dict(binding=copy.deepcopy(binding),fields=dict(entity='220',kind='0',weapon='9'))
        return b,d,goal
    def test_actual_samecall_evidence_proves_new_source_priority_only(self):
        self.assertEqual(priority_status(*self.fixture()),'OBSERVED_NEW_CLOSE_FIRST_WEAPON_SOURCE_PRIORITY')
    def test_missing_or_crosscall_or_changed_generation_never_promotes(self):
        b,d,g=self.fixture()
        self.assertNotEqual(priority_status(b,None,g),'OBSERVED_NEW_CLOSE_FIRST_WEAPON_SOURCE_PRIORITY')
        for key,value in [('tick',21),('gen',[3,4]),('actor',8)]:
            bad=copy.deepcopy(d);bad['typed'][key]=value
            self.assertNotEqual(priority_status(b,bad,g),'OBSERVED_NEW_CLOSE_FIRST_WEAPON_SOURCE_PRIORITY')
    def test_armed_special_stale_health_or_replaced_attempt_not_new_branch(self):
        b,d,g=self.fixture()
        cases=[]
        x=copy.deepcopy(b);x['decision']['fields']['input'][2]=11;cases.append((x,d,g))
        x=copy.deepcopy(b);x['decision']['fields']['deadline']=[30,31];cases.append((x,d,g))
        x=copy.deepcopy(b);x['arbitration']['fields']['refresh']=[0,0];cases.append((x,d,g))
        x=copy.deepcopy(d);x['typed']['supply'][4]=143;cases.append((b,x,g))
        x=copy.deepcopy(d);x['typed']['supply'][5]=1;cases.append((b,x,g))
        x=copy.deepcopy(g);x['fields']['weapon']='3';cases.append((b,d,x))
        x=copy.deepcopy(g);x['binding']['native_spawn']=3.5;cases.append((b,d,x))
        for args in cases:
            self.assertNotEqual(priority_status(*args),'OBSERVED_NEW_CLOSE_FIRST_WEAPON_SOURCE_PRIORITY')

if __name__=='__main__':unittest.main(verbosity=2)
