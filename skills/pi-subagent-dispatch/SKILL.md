---
name: pi-subagent-dispatch
description: Use when dispatching subagents from a pi session (Agent tool) — implementers, reviewers, or any child model call — to pick the model and provider, or when a dispatch fails (extra-usage 400, prompt-capture error, tool-schema `minimum` rejection).
---

# Dispatching pi subagents

Verified 2026-10-04 on pi 1.0.1 and `@tintinweb/pi-subagents` 0.19.0.

## Choosing the model

Who reviews whom is in executing-plans; this is how to carry it out. The `worker` and
`reviewer` agent files carry **no `model:` or `isolated:` lines**, so the dispatch decides.
(Frontmatter is authoritative in pi-subagents: a pinned field can't be overridden at dispatch.)

| Role | Model |
|---|---|
| `worker` (implementer) | omit `model`: it inherits the session model. Routine work: pass a smaller model on the same provider, e.g. a Sonnet model on `claude-bridge`. Never the smallest tier |
| `reviewer` | a model from the **other provider family** from the implementer, on a provider you have signed in to with `/login` |
| Security review or question | the same other-family rule |

Claude runs through the `claude-bridge` provider, on the Claude Code login. Don't use the
direct `anthropic/*` provider for children unless you have signed in to it.

If only one provider family is signed in, stop and ask the user: sign in to another provider
(`/login`), or accept a same-family reviewer for this run. Never substitute one silently.

Dispatch with `isolated: false` (the default). Name the brief and report files in the prompt.

## Failure signatures

| Signature | Cause | Fix |
|---|---|---|
| `400 Third-party apps now draw from your extra usage...` | Server-side classifier keys on pi's harness block in a child's system prompt; built-in `general-purpose` children carry it | Use a custom agent (`worker`, `reviewer`, or a `.pi/agents/*.md`) with its own lean prompt, never `general-purpose` |
| `prompt-capture: no capture for this N-char system prompt` | Seen with `claude-bridge/*` children dispatched `isolated: true` | Dispatch bridge children with `isolated: false` |
| `400 tools.N.custom: For 'number' type, property 'minimum' is not supported` | A tool schema uses JSON-Schema `minimum`, which the direct `anthropic/*` API rejects | Re-dispatch on `claude-bridge/*` |
| `Cannot find module .../dist/bundle/chunks/<provider>-*.js` (e.g. `openai-responses-*`, `anthropic-messages-*`) | The session started before a pi upgrade and never loaded that provider's code; the upgrade replaced the files. Providers already used in the session keep working | Restart pi (resume the session). Check with a fresh `pi -p --no-session --model <m> ...` |

## Smoke test

After a harness change, dispatch each model you plan to use with the prompt
"Reply with exactly the word: ready" and `max_turns: 1`. (A `worker` may answer
`NEEDS_CONTEXT` instead: it wants a brief. That still proves the model runs.)
Outside a session: `pi -p --no-session --model <provider/model> "Reply with exactly the word: ready"`.
