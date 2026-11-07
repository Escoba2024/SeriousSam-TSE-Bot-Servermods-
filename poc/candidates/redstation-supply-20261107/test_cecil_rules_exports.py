#!/usr/bin/env python3
"""Compare compiled rules with the pinned analysis JSON, without publishing NAV data."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile

PIN = "953b477e53fdc5a5d84c8ae8d759c84fdf6c973c"
FIELDS = ("weapon_id", "min_distance", "max_distance", "damage_rating",
          "accuracy", "strafe", "special", "shot_frequency")
MEMBERS = ("id",) + FIELDS[1:]


def number(value):
    return {"TRUE": 1.0, "FALSE": 0.0}.get(value) if value in ("TRUE", "FALSE") else float(value.rstrip("f"))


def main():
    exports = Path(sys.argv[1])
    weapons = json.loads((exports / "weapons.json").read_text())
    settings = json.loads((exports / "settings.json").read_text())
    assert weapons["source_commit"] == settings["source_commit"] == PIN
    assert len(weapons["rows"]) == 30 and len(settings["rows"]) == 119
    preset_names = ("Dummy", "Easy", "Normal", "Hard")
    expected = []
    code = ['#include "cecil_rules.h"', '#include <cstdio>', 'int main(){']
    for row in weapons["rows"]:
        coop = int(row["mode"] == "Cooperative")
        i = row["table_order"]
        expected.append([float(row[k]) for k in FIELDS])
        args = ",".join(f"double(w.{member})" for member in MEMBERS)
        code.append(f'{{const auto& w=botcore::CecilWeapons({coop})[{i}];std::printf("' +
                    " ".join(["%.17g"] * len(FIELDS)) + '\\n",' + args + ');}')
    for p, name in enumerate(preset_names):
        values = [r for r in settings["rows"] if r["preset"] in (name, "ConstructorOnly")]
        assert len(values) == 32, (name, len(values))
        for row in values:
            member = row["parameter"]
            assert member.isidentifier()
            expected.append([number(row["source_value"])])
            code.append(f'std::printf("%.17g\\n",double(botcore::CecilPreset({p}).{member}));')
    code.append("}")
    with tempfile.TemporaryDirectory(prefix="cecil-rules-exports-") as tmp:
        source = Path(tmp) / "probe.cpp"
        binary = Path(tmp) / "probe"
        source.write_text("\n".join(code))
        subprocess.run(["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror",
                        "-I", str(Path(__file__).resolve().parent), str(source), "-o", str(binary)],
                       check=True)
        actual = [[float(v) for v in row.split()]
                  for row in subprocess.check_output([str(binary)], text=True).splitlines()]
    assert actual == expected, "compiled table/preset differs from pinned source export"
    print("PASS: 30 original weapon rows + 4 x 32 settings (119 source assignments)")


if __name__ == "__main__":
    main()
