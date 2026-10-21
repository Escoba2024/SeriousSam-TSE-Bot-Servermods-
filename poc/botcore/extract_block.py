#!/usr/bin/env python3
"""Extract the human-AI block from an integrated BotDriver.cpp.

The block is the body of `if (bot_bHumanAI) { ... }` in the combat decision
section. It is the only part of the GameMP integration that cannot be built on
Linux, so test_botdriver_block.cpp compiles exactly that text against stubbed
engine types. Extracting instead of copying keeps a single source of truth.

Usage:
    python3 extract_block.py <path-to-BotDriver.cpp> > block.inc

Exit codes: 0 = extracted, 2 = block not found (file not patched yet).
"""
import sys

START = '      if (bot_bHumanAI) {'
END = ('      } else if (player!=NULL && deathmatch && '
       'player->GetHealth()>0 && player->m_penWeapons!=NULL) {')


def main(argv):
    if len(argv) != 2:
        sys.stderr.write(__doc__)
        return 2
    text = open(argv[1], encoding='utf-8', errors='replace').read()
    text = text.replace('\r\n', '\n')
    if START not in text or END not in text:
        sys.stderr.write('human-AI block not found in %s (patch not applied?)\n' % argv[1])
        return 2
    start = text.index(START)
    end = text.index(END, start)
    # Keep any engine adapter called by the block in the same source of truth.
    helper = 'static uint32_t BotCombatUsableWeapons('
    if helper in text:
        hstart = text.index(helper)
        body = text.index('{', hstart) + 1
        hend = text.index('\n}\n', body)
        sys.stdout.write('const auto BotCombatUsableWeapons=[](CPlayerWeapons *weapons) {' + text[body:hend] + '\n};\n')
    sys.stdout.write(text[start:end])
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
