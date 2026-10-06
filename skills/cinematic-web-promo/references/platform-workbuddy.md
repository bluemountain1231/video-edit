# WorkBuddy and CodeBuddy Adapter

## WorkBuddy Desktop

Use the official Skills UI:

1. Generate or obtain `cinematic-web-promo-workbuddy.zip`.
2. Open the Skills panel.
3. Choose add/upload local skill package.
4. Upload the archive and enable the skill.
5. Trigger it with a natural-language website-promo request.

Do not assume WorkBuddy Desktop exposes a stable `~/.workbuddy/skills` directory. Prefer package upload so the application can configure and audit the skill.

If WorkBuddy cannot execute Bash scripts, use `scripts/preflight.ps1` on Windows or equivalent built-in tools. If the desktop sandbox does not expose the imported package path, use agent-native browser/media tools and treat bundled scripts as reference implementations.

## CodeBuddy or WorkBuddy Enterprise Workspace

Use the project root:

```text
<workspace>/.codebuddy/skills/cinematic-web-promo/SKILL.md
```

Project skills take priority over user skills. Use `/cinematic-web-promo` or let the host match the `description`. Optional WorkBuddy/CodeBuddy frontmatter such as `allowed-tools` is deliberately omitted so the same package remains safe and portable.

## Permissions

Before capture or rendering, confirm authorization for:

- local file reads/writes;
- browser/session access;
- system command execution;
- third-party music or media downloads;
- any external data transfer.

Keep media-license evidence in `assets/media-license-manifest.json` and do not publish draft-only reference music.
