# Claude Code Adapter

## Discovery

Use:

- personal: `~/.claude/skills/cinematic-web-promo/SKILL.md`;
- project: `<repo>/.claude/skills/cinematic-web-promo/SKILL.md`;
- plugin: `<plugin>/skills/cinematic-web-promo/SKILL.md`.

Claude Code discovers project skills from the starting directory and parent directories to the repository root. It watches existing skill roots for live changes.

## Invocation and Root Resolution

Invoke with `/cinematic-web-promo` or ask naturally for a matching website promo. Claude Code provides `${CLAUDE_SKILL_DIR}` for bundled resources. Resolve helpers with:

```bash
export CWP_SKILL_DIR="${CLAUDE_SKILL_DIR}"
```

Do not add Claude-only frontmatter to the shared `SKILL.md`; the shared `name` and `description` remain valid Agent Skills metadata. Do not add broad `allowed-tools` permissions: website capture, shell execution, and local writes should remain subject to the user's normal permission settings.

## Browser and Files

Use the browser or MCP capability already available in Claude Code for authenticated pages. Otherwise install the pinned Playwright helper under `scripts/`. Keep project-specific copies in `.claude/skills`; use the personal root only for workflows intended across all repositories.

## Installation Check

Run `claude` in a project, then invoke `/cinematic-web-promo`. If a newly created top-level `~/.claude/skills` directory is not detected, restart Claude Code once.
