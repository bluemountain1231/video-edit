# Codex Adapter

## Discovery

Use the current official local roots:

- user: `$HOME/.agents/skills/cinematic-web-promo`;
- repository: `<repo>/.agents/skills/cinematic-web-promo`;
- custom/admin: use the path reported by the Codex host or administrator.

Codex scans `.agents/skills` from the working directory through the repository root and follows symlinked skill folders. App-managed environments may expose additional configured roots.

## Invocation and Root Resolution

Invoke explicitly with `$cinematic-web-promo`; use `/skills` to inspect discovery. The host catalog includes the `SKILL.md` path, so set `CWP_SKILL_DIR` to its parent directory before running bundled scripts.

Keep `agents/openai.yaml`. Codex uses it for UI metadata and default invocation text; other hosts can ignore it.

## Browser and Files

Prefer Codex's active browser/computer tools when the task depends on a signed-in session. Run Playwright capture only for public or explicitly authorized pages. Keep final deliverables in the host-approved output directory.

## Installation Check

After installation, verify:

```bash
test -f "$HOME/.agents/skills/cinematic-web-promo/SKILL.md"
```

Then restart Codex only if live discovery does not show the update.
