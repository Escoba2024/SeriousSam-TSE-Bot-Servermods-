"""Private exact original-server kill tokens; no name normalization or clocks.

Template strings copied exactly from the pinned existing behavior_hazards reader.
"""
import re
PATTERNS={'telefrag': '^(.+) telefragged (.+)$', 'knife': '^(.+) cut (.+) into pieces$', 'lead': '^(.+) poured lead into (.+)$', 'blast': '^(.+) blew (.+) away$', 'cannon': '^(.+) smashed (.+) with a cannon$', 'nuke': '^(.+) nuked (.+)$', 'generic': '^(.+) killed (.+)$', 'drowned': '^(.+) drowned$', 'burning': '^(.+) burst into flames$', 'spike': '^(.+) fell into a spike-hole$', 'freezing': '^(.+) has frozen$', 'acid': '^(.+) dissolved$', 'selfblast': '^(.+) blew himself away$', 'suicide': '^(.+) has committed suicide$', 'abyss': '^(.+) went over the edge$', 'brush': '^(.+) was squashed$', 'impact': '^(.+) swashed$', 'heat': '^(.+) stood in the sun for too long$', 'unknown_other': '^(.+) passed away$', 'missing': '^(.+) is missing in action$', 'pierced': '^(.+) was pierced$', 'enemy_telefrag': '^(.+) was telefragged$'}

def parse_kills(text,names):
    def slot(name):
        values=names.get(name,set())
        return next(iter(values))if len(values)==1 else None
    out=[]
    for number,line in enumerate(text.splitlines(),1):
        hits=[(kind,m)for kind,pattern in PATTERNS.items()if(m:=re.fullmatch(pattern,line))]
        if len(hits)>1 and any(kind=='selfblast'for kind,m in hits):hits=[h for h in hits if h[0]=='selfblast']
        if len(hits)>1:raise ValueError('ambiguous death template')
        if not hits:continue
        kind,m=hits[0];tokens=list(m.groups())
        out.append(dict(line=number,kind=kind,tokens=tokens,killer_slot=slot(tokens[0])if len(tokens)==2 else None,victim_slot=slot(tokens[-1]),native_time='UNKNOWN',native_life='UNKNOWN',name_join='EXACT_UNIQUE_QUERY_TOKEN_ONLY'))
    return out
