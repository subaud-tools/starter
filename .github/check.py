"""Checks the starter offline, in two parts; with no argument it runs both.

manifest: kempt.toml parses, matches kempt's JSON Schema (written by
`kempt schema`, kept in .github/kempt.schema.json), and the suite profile
selects every package in the file except the ones a machine adopts on top
(ADOPTABLE). kempt itself is not public, so CI checks the manifest's shape
here; `kempt lint` and `kempt plan -profile suite` are the checks to run on a
machine that has kempt.

private: no tracked file holds a home path, an email address other than a
noreply one, a 12-digit number (an AWS account id) or a private key. This
repo is public; a hit names the file, line and kind, never the text."""

import json
import pathlib
import re
import subprocess
import sys
import tomllib

# Packages a machine adopts on top of the suite (`kempt adopt <name>`).
ADOPTABLE = {"pi", "neovim"}

PRIVATE = [
    ("home path", re.compile(r"(?:/Users|/home)/[A-Za-z][\w.-]*")),
    ("email address", re.compile(r"[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}\b")),
    ("12-digit number", re.compile(r"\b\d{12}\b")),
    ("private key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
]

root = pathlib.Path(__file__).resolve().parent.parent


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
