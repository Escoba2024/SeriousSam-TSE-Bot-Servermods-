"""Pure validation only: no games, mounts, sockets or deployment in these tests."""
import copy,unittest
import qualify_integrated_wine as q
def evidence():
    return {"status":"PASS_60MIN_WINE","bots":8,"human_ai":True,"elapsed_s":3600,"dll_sha256":"candidate","new_throttled_periods":0,"checks":{r:{"telemetry":{"verdict":"ACTIVE_OK"},"slots":{str(i):{"moved":True,"fired":True} for i in range(4)}} for r in ["botA","botB"]},"unmounts":[{"exitcode":0}]}
class PublicGate(unittest.TestCase):
    def test_public_humans_are_allowed_but_all_bot_names_are_required(self):
        bots=list(q.ROSTER)
        self.assertTrue(q.population_ready({"numplayers":"9"},bots+["Human"],8,True))
        self.assertFalse(q.population_ready({"numplayers":"8"},bots[:-1]+["Human"],8,True))
        self.assertFalse(q.population_ready({"numplayers":"9"},bots+["Human"],8,False))
        self.assertTrue(q.population_ready({"numplayers":"4"},bots[:4],4,False))
    def test_complete_same_artifact_evidence_is_required(self):
        q.validate_public_evidence(evidence(),"candidate")
        for key,value in [("status","PASS_LIMITED"),("elapsed_s",3599),("dll_sha256","other"),("bots",4),("new_throttled_periods",1)]:
            e=evidence();e[key]=value
            with self.assertRaises(AssertionError,msg=key):q.validate_public_evidence(e,"candidate")
    def test_inactive_slot_or_failed_cleanup_is_rejected(self):
        e=evidence();e["checks"]["botB"]["slots"]["3"]["fired"]=False
        with self.assertRaises(AssertionError):q.validate_public_evidence(e,"candidate")
        e=evidence();e["unmounts"][0]["exitcode"]=1
        with self.assertRaises(AssertionError):q.validate_public_evidence(e,"candidate")
if __name__=="__main__":unittest.main()
