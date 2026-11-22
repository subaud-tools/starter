"""Checks the starter offline, in two parts; with no argument it runs both.

manifest: kempt.toml parses, matches kempt's JSON Schema (written by
`kempt schema`, kept in .github/kempt.schema.json), and the suite profile
selects every package in the file except the ones a machine adopts on top
(ADOPTABLE). It also checks that Claude Code is denied every path pi's
permission policy denies: the deny list merged into ~/.claude/settings.json
must be the pi policy's path denies, translated by claude_denies below, so
the two cannot drift. kempt itself is not public, so CI checks the manifest's
shape here; `kempt lint` and `kempt plan -profile suite` are the checks to run
on a machine that has kempt.

private: no tracked file holds a home path, an email address other than a
noreply one, a 12-digit number (an AWS account id) or a private key. This
repo is public; a hit names the file, line and kind, never the text."""

import fnmatch
import json
import pathlib
import re
import subprocess
import sys
import tomllib

# Packages a machine adopts on top of the suite (`kempt adopt <name>`).
ADOPTABLE = {"pi", "neovim"}

# Allow exceptions in pi's path policy that Claude Code's deny rules cannot
# express: a `!` carve-out reaches only rules relative to the current
# directory, never one under ~/. Claude Code denies these along with the rest
# of their folder, and the README says so.
NOT_CARVED = {"~/.ssh/*.pub"}

PRIVATE = [
    ("home path", re.compile(r"(?:/Users|/home)/[A-Za-z][\w.-]*")),
    ("email address", re.compile(r"[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")),
    ("12-digit number", re.compile(r"\b\d{12}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

root = pathlib.Path(__file__).resolve().parent.parent


def claude_denies(paths):
    """pi's path policy as Claude Code Read deny rules, in the policy's order.

    A path under ~/ keeps its place, with a trailing /* widened to /** since
    Claude Code's * stops at a slash. A file-name pattern is denied anywhere
    on the machine (//**/), unless the policy allows some names inside it:
    then it is denied under the current directory, the only place Claude
    Code's `!` carve-out reaches, and the allowed names are carved out after
    it."""
    denied = [p for p, rule in paths.items() if isinstance(rule, dict) and rule.get("action") == "deny"]
    allowed = [p for p, rule in paths.items() if rule == "allow" and p != "*"]
    rules, carved = [], set()
    for path in denied:
        if path.startswith("~/"):
            rules.append("Read(%s)" % (path[:-2] + "/**" if path.endswith("/*") else path))
            continue
        inside = [a for a in allowed if not a.startswith("~/") and fnmatch.fnmatchcase(a, path)]
        if not inside:
            rules.append(f"Read(//**/{path})")
            continue
        rules.append(f"Read({path})")
        rules += [f"Read(!{a})" for a in inside]
        carved.update(inside)
    return rules, sorted(set(allowed) - carved - NOT_CARVED)


def check_claude_denies(manifest):
    packages = manifest.get("packages", {})
    policies = [s["merge"]["permission"]["path"] for s in packages.get("pi", {}).get("json-merge", [])
                if "permission" in s.get("merge", {})]
    merges = [s for name, package in packages.items() if name not in ADOPTABLE
              for s in package.get("json-merge", []) if s.get("file") == "~/.claude/settings.json"]
    if len(policies) != 1:
        return ["kempt.toml: expected one pi permission policy with a path table"]
    want, unhandled = claude_denies(policies[0])
    errors = [f"kempt.toml: pi's policy allows {p} inside a denied path, which no Claude Code rule covers"
              for p in unhandled]
    if len(merges) != 1 or merges[0].get("arrays", "append") != "append":
        return errors + ["kempt.toml: expected one appending json-merge into ~/.claude/settings.json "
                         "outside the packages to adopt"]
    have = merges[0].get("merge", {}).get("permissions", {}).get("deny", [])
    for rule in want:
        if rule not in have:
            errors.append(f"kempt.toml: Claude Code's deny list lacks {rule}, which pi's policy denies")
    for rule in have:
        if rule not in want:
            errors.append(f"kempt.toml: Claude Code's deny list has {rule}, which pi's policy does not deny")
    if not errors and have != want:
        errors.append("kempt.toml: Claude Code's deny list is not in the order of pi's policy "
                      "(a ! rule must follow the rule it carves out of)")
    return errors


def check_manifest():
    import jsonschema

    manifest = tomllib.loads((root / "kempt.toml").read_text())
    schema = json.loads((root / ".github" / "kempt.schema.json").read_text())

    errors = [f"kempt.toml: {e.message}"
              for e in jsonschema.Draft202012Validator(schema).iter_errors(manifest)]

    packages = set(manifest.get("packages", {}))
    suite = manifest.get("profiles", {}).get("suite")
    if suite is None:
        return errors + ["kempt.toml: no [profiles.suite]"]
    selected = set(suite.get("packages", []))
    for name in sorted(packages - selected - ADOPTABLE):
        errors.append(f"kempt.toml: package {name} is not in the suite profile")
    for name in sorted(selected & ADOPTABLE):
        errors.append(f"kempt.toml: the suite profile selects {name}, which a machine adopts on top")
    for name in sorted(ADOPTABLE - packages):
        errors.append(f"kempt.toml: ADOPTABLE names {name}, which has no package")
    for name in sorted(selected - packages):
        errors.append(f"kempt.toml: the suite profile names {name}, which has no package")
    errors += check_claude_denies(manifest)
    if not errors:
        print(f"kempt.toml: ok ({len(packages)} packages: {len(selected)} in the suite profile, "
              f"{len(ADOPTABLE)} to adopt)")
    return errors


def check_private():
    files = subprocess.run(["git", "ls-files", "-z"], cwd=root, check=True,
                           capture_output=True, text=True).stdout.split("\0")
    errors = []
    for name in filter(None, files):
        try:
            text = (root / name).read_text()
        except (UnicodeDecodeError, IsADirectoryError):
            continue
        for n, line in enumerate(text.splitlines(), 1):
            for kind, pattern in PRIVATE:
                for m in pattern.finditer(line):
                    if kind == "email address" and "noreply" in m.group().lower():
                        continue
                    errors.append(f"{name}:{n}: {kind}")
    if not errors:
        print(f"private: ok ({len([f for f in files if f])} tracked files)")
    return errors


checks = {"manifest": check_manifest, "private": check_private}
names = sys.argv[1:] or list(checks)
errors = []
for name in names:
    errors += checks[name]()
for e in errors:
    print(e, file=sys.stderr)
if errors:
    sys.exit(1)
