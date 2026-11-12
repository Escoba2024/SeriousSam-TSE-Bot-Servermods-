"""Lossless command-policy reader for the bounded names-only transaction.

Read raw systemctl output: repeated ExecStartPre/ExecStop rows are ordered
commands, not a dictionary. Only reviewed launcher shapes may execute.
"""
import hashlib
from pathlib import Path
import re


EXEC_FIELDS = ("ExecStart", "ExecStartPre", "ExecStop")
SERVICE_POLICY_FIELDS = (
    "ExecStop", "KillMode", "SendSIGKILL", "TimeoutStopUSec", "ExecStart",
    "ExecStartPre", "FragmentPath", "DropInPaths",
)
COMMAND_FIELDS = {"path", "argv[]", "ignore_errors"}
VOLATILE_FIELDS = {"start_time", "stop_time", "pid", "code", "status"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def parse_commands(value):
    commands, end = [], 0
    for match in re.finditer(r"\{([^{}]*)\}", value):
        require(not value[end:match.start()].strip(), "unparsed service command fragment")
        fields = {}
        for field in match[1].split(";"):
            if not field.strip():
                continue
            key, separator, content = field.strip().partition("=")
            require(separator and key in COMMAND_FIELDS | VOLATILE_FIELDS,
                    "unknown service command field")
            require(key not in fields, "duplicate service command field")
            fields[key] = content.strip()
        require(COMMAND_FIELDS <= fields.keys() and fields["path"] and fields["argv[]"] and
                fields["ignore_errors"] in ("yes", "no"), "incomplete service command policy")
        commands.append(dict(path=fields["path"], argv=fields["argv[]"],
                             ignore_errors=fields["ignore_errors"]))
        end = match.end()
    require(not value[end:].strip(), "unparsed service command fragment")
    return commands


def parse_service_policy(raw):
    """Keep every ordered exec record; reject unknown or duplicate scalar rows."""
    policy = {key: [] for key in EXEC_FIELDS}
    for line in raw.splitlines():
        if not line:
            continue
        key, separator, value = line.partition("=")
        require(separator and key in SERVICE_POLICY_FIELDS, "unknown service policy row")
        if key in EXEC_FIELDS:
            policy[key].extend(parse_commands(value))
        else:
            require(key not in policy, "duplicate scalar service policy row")
            policy[key] = value
    return policy


def validate_launch_policy(policy, *, client_root, launch_helper_pins, read_bytes):
    """Allow exact Bash launcher, numeric sleep, and assigned SHA-pinned wait helper.

    The caller supplies already reviewed helper hashes. No interpreter aliases,
    extra arguments, cross-instance helpers, or ignored failures are accepted.
    """
    root = Path(client_root)
    launcher = str(root.parent/("launch-"+root.name+".sh"))
    command = policy["ExecStart"]
    require(len(command) == 1 and command[0]["path"] in ("/bin/bash", "/usr/bin/bash") and
            command[0]["argv"] == command[0]["path"]+" "+launcher and
            command[0]["ignore_errors"] == "no",
            "service launcher does not execute exact reviewed launcher")
    helper = str(root.parent/"wait-server.py")
    for pre in policy["ExecStartPre"]:
        require(pre["ignore_errors"] == "no", "unreviewed pre-start ignore-errors policy")
        if pre["path"] in ("/bin/sleep", "/usr/bin/sleep"):
            require(re.fullmatch(re.escape(pre["path"])+r" [0-9]+(?:\.[0-9]+)?", pre["argv"]),
                    "unreviewed pre-start sleep command")
        else:
            require(pre["path"] == "/usr/bin/python3" and
                    pre["argv"] == "/usr/bin/python3 "+helper and helper in launch_helper_pins,
                    "unreviewed pre-start helper command")
            require(hashlib.sha256(read_bytes(helper)).hexdigest() == launch_helper_pins[helper],
                    "reviewed launch helper drift")
