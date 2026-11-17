"""Checks kempt.toml offline: it parses, matches kempt's JSON Schema (written by
`kempt schema`, kept in .github/kempt.schema.json), and the suite profile
selects every package in the file except the ones a machine adopts on top
(ADOPTABLE). kempt itself is not public, so CI checks
the manifest's shape here; `kempt lint` and `kempt plan -profile suite` are
the checks to run on a machine that has kempt."""

import json
import pathlib
import sys
import tomllib

import jsonschema

# Packages a machine adopts on top of the suite (`kempt adopt <name>`).
ADOPTABLE = {"pi", "neovim"}

root = pathlib.Path(__file__).resolve().parent.parent
manifest = tomllib.loads((root / "kempt.toml").read_text())
schema = json.loads((root / ".github" / "kempt.schema.json").read_text())

errors = [e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(manifest)]

packages = set(manifest.get("packages", {}))
suite = manifest.get("profiles", {}).get("suite")
if suite is None:
    errors.append("no [profiles.suite]")
else:
    selected = set(suite.get("packages", []))
    for name in sorted(packages - selected - ADOPTABLE):
        errors.append(f"package {name} is not in the suite profile")
    for name in sorted(selected & ADOPTABLE):
        errors.append(f"the suite profile selects {name}, which a machine adopts on top")
    for name in sorted(ADOPTABLE - packages):
        errors.append(f"ADOPTABLE names {name}, which has no package")
    for name in sorted(selected - packages):
        errors.append(f"the suite profile names {name}, which has no package")

for e in errors:
    print(f"kempt.toml: {e}", file=sys.stderr)
if errors:
    sys.exit(1)
print(f"kempt.toml: ok ({len(packages)} packages: {len(selected)} in the suite profile, "
      f"{len(ADOPTABLE)} to adopt)")
