# subaud starter

A minimal [kempt](https://kempt.tools) config that sets up a machine for the
[subaud](https://subaud.tools) suite: tmux, and every suite tool (muster,
galley, kempt, tackle, casebook, muda, diazo) with the skills, Claude Code
plugin and pi channel each release ships. Nothing else: no shell config, no
editor, no personal settings.

## Use it

You need a subaud.tools account with the suite. Your
[account page](https://subaud.tools/account/) gives you one line to paste in a
terminal on the machine:

```sh
curl -fsSL https://subaud.tools/setup.sh | sh -s -- <key>
```

[setup.sh](https://subaud.tools/setup.sh) signs the machine in, installs
Homebrew on a Mac and tmux, installs Claude Code when no agent (Claude Code or
pi) is present, then runs

```sh
kempt init -yes -profile suite https://github.com/subaud-tools/starter.git
```

and opens your agent on "Get me started with subaud."

## What it installs

| Package | What |
|---|---|
| `core` | tmux, and a check that Claude Code or pi is here |
| `kempt` | kempt itself, so `kempt update` keeps it current |
| `muster` | messages between agent sessions on this machine |
| `galley` | review a document with your agent on a page |
| `tackle` | proj, scratch, creel, sift, imprint and cull |
| `casebook` | triage your repos, branches and PRs with your agent |
| `muda` | find and fix delivery waste in your pipelines |
| `diazo` | plan a change with your agent on a shared page |

`kempt update` later pulls this repo and rolls every tool forward.

## Checks

CI checks that `kempt.toml` parses, matches kempt's schema
(`.github/kempt.schema.json`, from `kempt schema`), and that the `suite`
profile selects every package. On a machine with kempt, `kempt lint kempt.toml`
and `kempt plan -manifest kempt.toml -profile suite` check it fully.
