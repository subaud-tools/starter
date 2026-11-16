# subaud starter

A minimal [kempt](https://kempt.tools) config that sets up a machine for the
[subaud](https://subaud.tools) suite with Claude Code: tmux, Claude Code, and
every suite tool (muster, galley, kempt, tackle, casebook, muda, diazo) with
the skills, Claude Code plugin and pi channel each release ships. Nothing
else: no shell config, no editor, no personal settings.

## Use it

You need a subaud.tools account with the suite. In a terminal:

```sh
curl -fsSL https://kempt.tools/install.sh | sh
kempt init -profile suite https://github.com/subaud-tools/starter.git
```

The first line signs this machine in and installs kempt: it prints a link
(<https://subaud.tools/account/machine>) and a code, and waits while you open
the link, type the code and allow the machine. The second installs everything below.
Then run `claude` and say "Get me started with subaud."

On a Mac, tmux and Claude Code come from [Homebrew](https://brew.sh); install
it first if `brew` is missing. On Linux, Claude Code comes from npm and needs
Node.js 22 or later.

## What it installs

| Package | What |
|---|---|
| `core` | tmux; Claude Code (Homebrew cask on a Mac, npm on Linux) |
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
