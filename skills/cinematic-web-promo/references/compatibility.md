# Three-Host Compatibility Router

The core `SKILL.md`, scripts, references, and Remotion starter follow the Agent Skills folder model. Installation and invocation differ by host.

| Host | Personal/user installation | Project installation | Invocation |
|---|---|---|---|
| Codex | `~/.agents/skills/cinematic-web-promo` | `<repo>/.agents/skills/cinematic-web-promo` | `$cinematic-web-promo` or `/skills` |
| Claude Code | `~/.claude/skills/cinematic-web-promo` | `<repo>/.claude/skills/cinematic-web-promo` | `/cinematic-web-promo` or natural language |
| WorkBuddy Desktop | Upload `cinematic-web-promo-workbuddy.zip` in Skills | Use WorkBuddy's local import UI | Natural language or Skills panel |
| CodeBuddy workspace | Use the Settings import UI | `<workspace>/.codebuddy/skills/cinematic-web-promo` | `/cinematic-web-promo` or automatic match |

Read only the platform-specific reference selected in `SKILL.md`:

- `platform-codex.md`
- `platform-claude-code.md`
- `platform-workbuddy.md`

## Installers

macOS/Linux:

```bash
scripts/install_skill.sh codex-user
scripts/install_skill.sh codex-project /absolute/repo
scripts/install_skill.sh claude-user
scripts/install_skill.sh claude-project /absolute/repo
scripts/install_skill.sh workbuddy-package /absolute/output/cinematic-web-promo-workbuddy.zip
scripts/install_skill.sh codebuddy-project /absolute/workspace
```

Windows PowerShell uses the same target names:

```powershell
./scripts/install_skill.ps1 codex-user
./scripts/install_skill.ps1 claude-project C:\path\to\repo
./scripts/install_skill.ps1 workbuddy-package C:\path\to\cinematic-web-promo-workbuddy.zip
```

Both installers refuse replacement by default. Pass `--force` in Bash or `-Force` in PowerShell to move the existing destination to a timestamped backup before installing.

## Package All Three Hosts

Run:

```bash
scripts/package_three_targets.sh /absolute/output-directory
```

This produces three archives with the same validated core and host-specific package names. The WorkBuddy archive is directly uploadable from its Skills panel. Codex and Claude archives unpack to a `cinematic-web-promo/` folder that can be moved into the documented user or project skill root.

## Path Fallbacks

Some older or app-managed Codex installations use a configured custom root such as `~/.codex/skills`. Do not replace the official `~/.agents/skills` default with that assumption; use the installer's `custom` target when the host explicitly reports another root.

WorkBuddy Desktop does not publish a stable user filesystem directory in its official UI workflow. Prefer package upload. Treat `~/.workbuddy/skills` as a non-authoritative compatibility path and use it only when the installed WorkBuddy build explicitly documents it.
