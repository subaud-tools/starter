# subaud starter

A minimal [kempt](https://kempt.tools) config that sets up a machine for the
[subaud](https://subaud.tools) suite: tmux, Ghostty and yazi, every suite
tool (muster, galley, kempt, tackle, casebook, muda, diazo) with the skills,
Claude Code plugin and pi channel each release ships, and the way of working:
shared rules and process skills for your agent. No shell config and no
personal settings; every file it links over yours is backed up first.

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
| `core` | tmux |
| `terminal` | Ghostty and FiraCode Nerd Font on a Mac, and yazi: proj opens sessions in Ghostty and runs yazi in its sidebar |
| `way-of-working` | the shared rules (`way-of-working.md`), loaded by Claude Code through one import line in `~/.claude/CLAUDE.md` and by pi as `~/.pi/agent/APPEND_SYSTEM.md`, and the process skills, each linked into `~/.claude/skills` and `~/.pi/agent/skills` |
| `kempt` | kempt itself, so `kempt update` keeps it current |
| `muster` | messages between agent sessions on this machine |
| `galley` | review a document with your agent on a page |
| `tackle` | proj, scratch, creel, sift, imprint and cull |
| `casebook` | triage your repos, branches and PRs with your agent |
| `muda` | find and fix delivery waste in your pipelines |
| `diazo` | plan a change with your agent on a shared page |

`kempt update` later pulls this repo and rolls every tool forward.

## Packages to adopt

Two packages are not in `suite`; a machine adopts them on top of it. Ask your
agent, or run the command yourself:

| Package | What | Adopt it |
|---|---|---|
| `pi` | the pi coding agent on your Claude Code login (the claude-bridge provider), its extensions, the worker and reviewer subagents, and a permission policy that asks before any command off its allow list | `kempt adopt pi`, then apply (below) |
| `neovim` | Neovim with a LazyVim config, ripgrep, fd and FiraCode Nerd Font; an existing `~/.config/nvim` is backed up first | `kempt adopt neovim && kempt apply -yes` |

`kempt adopt` only saves the choice; `kempt apply` installs it. On a Mac, `pi`
installs with npm from Homebrew's `node@24`, which Homebrew leaves off PATH;
kempt 0.23.0 and later put it on PATH for its own run, so one apply installs
`node@24`, pi and pi's extensions (the package also adds one line to
`~/.zprofile` so later shells have it):

```sh
kempt adopt pi
kempt apply -yes
pi --version
```

The account page's line does the same with ` pi` on its end.

## Checks

CI checks that `kempt.toml` parses, matches kempt's schema
(`.github/kempt.schema.json`, from `kempt schema`), and that the `suite`
profile selects every package but the two to adopt. It also fails when a
tracked file holds a home path, an email address other than a noreply one, a
12-digit number or a private key. Run both with `python .github/check.py`. On
a machine with kempt, `kempt lint kempt.toml` and
`kempt plan -manifest kempt.toml -profile suite` check it fully.

The process skills are adapted in part from
[obra/superpowers](https://github.com/obra/superpowers) (MIT); its license is
in `LICENSES/superpowers`.
