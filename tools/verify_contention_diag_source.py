"""Exact passive-only inverse of qualified contention diagnostics to Build027."""
import hashlib
from pathlib import Path

PAIRS=[('static bool BotCecilNearerLocalSupply(CPlayer* player,INDEX slot,uint32_t item,double cost,double observedAt){', '// Scalar receipt of the existing first qualifying local owner; no pointers escape.\n// Unknown means not qualified in this evaluation, never proof of no contender.\nstruct SCecilSupplyClaimReceipt {\n  bool valid=false;INDEX local=-1;long map=0;uint32_t entity=0,generation=0,item=0;int goal=-1;\n  double cost=0,seen=0,localTime=0,progress=0,attempt=0,deadline=0;\n};\nstatic bool BotCecilNearerLocalSupply(CPlayer* player,INDEX slot,uint32_t item,double cost,double observedAt,\n    SCecilSupplyClaimReceipt* receipt=NULL){\n  if(receipt)*receipt=SCecilSupplyClaimReceipt();'), ('       !owner->m_penWeapons||BotCecilHasRanged(BotCecilItemInput(owner,peer,1000)))continue;\n    return true;', '       !owner->m_penWeapons||BotCecilHasRanged(BotCecilItemInput(owner,peer,1000)))continue;\n    if(receipt){\n      receipt->valid=true;receipt->local=other;receipt->map=claim.map;\n      receipt->entity=claim.entity;receipt->generation=claim.generation;receipt->item=claim.item;receipt->goal=claim.goal;\n      receipt->cost=claim.cost;receipt->seen=claim.seen;receipt->localTime=claim.localTime;\n      receipt->progress=claim.progress;receipt->attempt=claim.attempt;receipt->deadline=claim.deadline;\n    }\n    return true;'), ('    int best=-1;bool bestContested=false;double bestScore=std::numeric_limits<double>::infinity(),bestCost=0;botcore::CecilItem chosen;', '    int best=-1;bool bestContested=false;double bestScore=std::numeric_limits<double>::infinity(),bestCost=0;botcore::CecilItem chosen;\n    SCecilSupplyClaimReceipt bestReceipt;double bestClaimCost=0;'), ('      const bool contested=preferUncontested&&BotCecilNearerLocalSupply(player,slot,item.id,cost-length,observedAt);', '      SCecilSupplyClaimReceipt candidateReceipt;\n      const bool contested=preferUncontested&&BotCecilNearerLocalSupply(player,slot,item.id,cost-length,observedAt,diagnostics?&candidateReceipt:NULL);'), ('special_flags=%lu\\n",\n            slot,tick,(unsigned long)s.generation', 'special_flags=%lu preference_evaluated=%d contested=%d owner_valid=%d owner_local=%d claim_cost=%.17g owner_cost=%.17g\\n",\n            slot,tick,(unsigned long)s.generation'), ('            std::fabs(BotCecilHeight(player,displacement)),score,from,to,(unsigned long)flags);', '            std::fabs(BotCecilHeight(player,displacement)),score,from,to,(unsigned long)flags,\n            (int)preferUncontested,(int)contested,(int)candidateReceipt.valid,candidateReceipt.local,cost-length,candidateReceipt.cost);'), ('        best=(int)i;bestContested=contested;bestScore=score;bestCost=cost;chosen=item;', '        best=(int)i;bestContested=contested;bestScore=score;bestCost=cost;chosen=item;\n        if(diagnostics){bestReceipt=candidateReceipt;bestClaimCost=cost-length;}'), ('special_flags=%lu\\n",\n        slot,tick,attempt,eligible,emitted', 'special_flags=%lu generation=%lu prefer_uncontested=%d contested=%d owner_valid=%d owner_local=%d claim_cost=%.17g observed_common=%.17g owner_map=%ld owner_entity=%lu owner_generation=%lu owner_item=%lu owner_goal=%d owner_cost=%.17g owner_seen_common=%.17g owner_local_time=%.17g owner_progress_local=%.17g owner_attempt_local=%.17g owner_deadline_local=%.17g\\n",\n        slot,tick,attempt,eligible,emitted'), ('best,s.goals.Distance(best),bestCost,bestScore,from,to,(unsigned long)flags);', 'best,s.goals.Distance(best),bestCost,bestScore,from,to,(unsigned long)flags,\n        (unsigned long)s.generation,(int)preferUncontested,(int)bestContested,(int)bestReceipt.valid,bestReceipt.local,\n        bestClaimCost,observedAt,bestReceipt.map,(unsigned long)bestReceipt.entity,(unsigned long)bestReceipt.generation,\n        (unsigned long)bestReceipt.item,bestReceipt.goal,bestReceipt.cost,bestReceipt.seen,bestReceipt.localTime,\n        bestReceipt.progress,bestReceipt.attempt,bestReceipt.deadline);')]
BASE_HEADER_SHA256='5530062bdac71b3649a5db0f7af4a4e90daafc60a343bbddf8b2189a878565a0'
BASE_SHA256='3a319f7b5c4f6a24a2a7b55fa0b523041b692f5e7fb38ad1b316613b3bc186cd'

def inverse(text):
    for before,after in reversed(PAIRS):
        if text.count(after)!=1:raise ValueError('exact unique contention diagnostic inverse required')
        text=text.replace(after,before,1)
    return text

def verify(text):
    original=inverse(text)
    if hashlib.sha256(original.encode()).hexdigest()!=BASE_HEADER_SHA256:
        raise ValueError('full Build027 header changed beyond exact diagnostic additions')
    start=original.index('static bool BotCecilNearerLocalSupply(')
    end=original.index('static void BotCecilChooseGoal(',start)
    if hashlib.sha256(original[start:end].encode()).hexdigest()!=BASE_SHA256:
        raise ValueError('owner/selection behavior changed beyond passive receipt')
    return original

if __name__=='__main__':
    p=Path(__file__).resolve().parents[1]/'poc/candidates/redstation-supply-20261107/BotSupplyNative.h'
    verify(p.read_text());print('PASS_EXACT_CONTENTION_OWNER_AND_SELECTION_INVERSE_ONLY')
