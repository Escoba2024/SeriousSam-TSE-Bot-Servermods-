"""Exact source-only failed-guard receipt; no extra read or readiness semantics."""
import ast
import hashlib

PARENT_SHA='b5627e91094594d0e1a0fae52ef8dc36be33f416436b92d0286396d37b31463a'
BEFORE="            require(animator >= 0x10000 and animator % 4 == 0, 'invalid animator pointer')"
AFTER="""            require(animator >= 0x10000 and animator % 4 == 0,
                    'invalid animator pointer animator=0x%08x slot=%d entity=0x%08x entity_id=%d world=0x%08x snapshot_tick=%.17g'
                    % (animator, slot, entity, entity_id, world, tick))"""


def digest(source):return hashlib.sha256(source.encode()).hexdigest()


def transform(source):
 if digest(source)!=PARENT_SHA or source.count(BEFORE)!=1:
  raise ValueError('exact active outer inventory reader required')
 result=source.replace(BEFORE,AFTER,1);ast.parse(result);return result


def reverse(source):
 if source.count(AFTER)!=1:raise ValueError('exact one animator failure context required')
 result=source.replace(AFTER,BEFORE,1)
 if digest(result)!=PARENT_SHA:raise ValueError('whole outer inventory reader inverse differs')
 ast.parse(result);return result
