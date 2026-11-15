"""Pure selection boundaries; no evidence or Native accesses."""
import unittest
import re
from trouble034_ram_conclusions import select_native,owner_context


class Selection(unittest.TestCase):
    def row(self,spawn=1,good=True,serial=4):
        return dict(good=good,spawn=spawn,read_serial=serial,tick=2,entity=7,world=8,
            health=25,weapons=dict(owned=7,current=3),position=[0,1,2],translation=[1,0,0],last_buttons=1)
    def test_only_same_life_valid_rows_and_original_serials(self):
        value=select_native([self.row(),self.row(2,serial=5),self.row(good=False,serial=6)],1)
        self.assertEqual([r['read_serial'] for r in value['observations']],[4])
        self.assertIn('NOT_ACTION_ACK',value['status'])
    def test_empty_unknown_never_zero_health_or_inventory(self):
        self.assertEqual(select_native([self.row(2)],1),dict(status='UNKNOWN_NO_GOOD_SAME_LIFE_OBSERVATIONS',observations=[]))
    def test_decreasing_health_is_observation_not_gain(self):
        a=self.row();b=self.row(serial=9);b['health']=10
        value=select_native([a,b],1)
        self.assertEqual(value['health_range'],[10,25]);self.assertEqual(value['owned_counts'],{'7':2})
        self.assertEqual(value['observations'][1]['read_serial'],9)


class PrintedSourceTime(unittest.TestCase):
    def matches(self,printed,actual):
        row=('[CecilDriverFinalV1] local=0 tick=20 actor=7 gen=(1,1) exit_actor=7 baseline_map_pin=1 map_known=0 life_link=1 '
             'pre_supply=(0,-1) supply=(0,0,0,0,0,0,0,0,0,0,0,0,0) wp=(0,0) post_mode=0 arb=(0,0,0,0,0,0) '
             'weapon=(0,0,0,0,0,0,0,0,0,0,0) safe=(1,0,0,0,'+str(actual)+',0,0,0,0,0,0,0,0) '
             'submitted=1 action=(0,0,0) rot=(0,0,0) view=(0,0,0) buttons=0')
        g=dict(logs=dict(botA=row,botB=''),source=dict(botA=[],botB=[]),bind=lambda *args:dict(status='FIXTURE_SOURCE_ONLY'))
        c=dict(G=g,source_event=lambda role,line,text:dict(fields=dict(re.findall(r'(\w+)=([^\s]+)',text))))
        event=dict(role='botA',line=2,fields=dict(reason='owner_lost',entity=7,generation=1,event_time_known=1,time=printed))
        return owner_context(c,dict(typed_rows=[event]))['exact_source_time_rows']
    def test_integer_print_does_not_mean_half_a_second(self):
        self.assertEqual(self.matches('159',159.1),0)
        self.assertEqual(self.matches('159',159.0000004),1)
    def test_exponent_spelling_keeps_nine_significant_digits(self):
        self.assertEqual(self.matches('1.59e2',159.001),0)
        self.assertEqual(self.matches('1.59e2',159.0000004),1)
    def test_zero_print_can_only_witness_exact_zero(self):
        self.assertEqual(self.matches('0',0.000001),0)
        self.assertEqual(self.matches('-0',0.0),1)
    def test_negative_print_is_not_a_coarse_interval(self):
        self.assertEqual(self.matches('-159',-159.001),0)
        self.assertEqual(self.matches('-159',-159.0000004),1)
    def test_power_of_ten_lower_bin_is_narrower(self):
        self.assertEqual(self.matches('10',9.99999996),0)
        self.assertEqual(self.matches('10',10.00000004),1)


if __name__=='__main__':unittest.main(verbosity=2)
