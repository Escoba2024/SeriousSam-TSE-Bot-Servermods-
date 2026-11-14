"""Pure checks of existing Retail107 native session fields for Hard gates.

Offsets are the same verified fields used by the initial fleet-rule receipt.
This module neither reads a process nor changes a session or configuration.
"""
import struct


FIELDS = {
    'difficulty': ('<i', 0x1c),
    'infiniteammo': ('<i', 0x54),
    'fraglimit': ('<i', 0x2c),
    'timelimit': ('<i', 0x30),
    'blood': ('<i', 0x88),
    'gibs': ('<i', 0x8c),
    'spawn': ('<f', 0x84),
}
EXPECTED = dict(difficulty=2, infiniteammo=1, fraglimit=0,
                timelimit=0, blood=3, gibs=0, spawn=0)


def validate_session(sample):
    try:
        raw = bytes.fromhex(sample['session156_hex'])
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError('missing or malformed native session bytes') from error
    if len(raw) != 156:
        raise ValueError('complete native session156 required')
    values = {key: struct.unpack_from(fmt, raw, offset)[0]
              for key, (fmt, offset) in FIELDS.items()}
    if values != EXPECTED:
        raise ValueError('native Hard/session rules differ')
    return values


def validate_query(query):
    if query.get('difficulty') != 'Hard':
        raise ValueError('actual query difficulty is not Hard')
