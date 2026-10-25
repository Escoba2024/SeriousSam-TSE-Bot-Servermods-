#!/usr/bin/env python3
"""Read-only Red Station GameSpy runtime config gate; never implies gameplay qualification.

Return 0 when configuration matches, 8 on absent/inconsistent/wrong evidence,
2 for invalid CLI usage. Fixture checks are always marked SIMULATED.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gamespy_query

STATUS_EXPECTED = {
    'gamename': 'serioussamse',
    'gamever': '1.07',
    'mapname': 'Red Station',
    'gametype': 'Fragmatch',
    'difficulty': 'Hard',
    'infiniteammo': '1',
    'maxplayers': '16',
}
RULES_EXPECTED = {'difficulty': 'Hard', 'infiniteammo': '1'}


def validate(status, rules):
    """Only validate complete, consistent, explicit server responses."""
    errors = []
    for name, response in [('status', status), ('rules', rules)]:
        if not isinstance(response, dict):
            return [name + ': response is not an object']
        if response.get('final') != '':
            errors.append(name + ': GameSpy final marker missing or invalid')
    for key, expected in STATUS_EXPECTED.items():
        if status.get(key) != expected:
            errors.append('status.' + key + '=' + repr(status.get(key)) + ' expected ' + repr(expected))
    if not isinstance(status.get('hostname'), str) or not status['hostname'].startswith('ssam.ai | Red Station'):
        errors.append('status.hostname is not the expected ssam.ai session')
    for key, expected in RULES_EXPECTED.items():
        if rules.get(key) != expected:
            errors.append('rules.' + key + '=' + repr(rules.get(key)) + ' expected ' + repr(expected))
        if status.get(key) != rules.get(key):
            errors.append('inconsistent status/rules.' + key)
    return errors


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    inputs=parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument('--address',help='live query host:query-port, read-only')
    inputs.add_argument('--status-json',type=Path,help='synthetic status fixture')
    parser.add_argument('--rules-json',type=Path,help='synthetic rules fixture; requires --status-json')
    args=parser.parse_args(argv)
    if bool(args.status_json) != bool(args.rules_json):
        parser.error('both --status-json and --rules-json required together')
    fixture=bool(args.status_json)
    evidence='SYNTHETIC_FIXTURE' if fixture else 'LIVE_GAMESPY_QUERY'
    errors=[]
    try:
        if fixture:
            status=json.loads(args.status_json.read_text(encoding='utf8'))
            rules=json.loads(args.rules_json.read_text(encoding='utf8'))
        else:
            host,port=gamespy_query.parse_hostport(args.address)
            status=gamespy_query.query(host,port,'\\status\\',timeout=1,attempts=1)
            rules=gamespy_query.query(host,port,'\\rules\\',timeout=1,attempts=1)
        errors=validate(status,rules)
    except (OSError, ValueError, TypeError, gamespy_query.QueryError) as exc:
        errors=[str(exc)]
    verdict=('SIMULATED_CONFIG_PASS' if fixture else 'LIVE_CONFIG_OBSERVED_PASS') if not errors else 'CONFIG_BLOCKED'
    print(json.dumps({'verdict':verdict,'evidence_class':evidence,'release_qualified':False,
                      'problems':errors},sort_keys=True))
    return 0 if not errors else 8

if __name__=='__main__':
    sys.exit(main())
