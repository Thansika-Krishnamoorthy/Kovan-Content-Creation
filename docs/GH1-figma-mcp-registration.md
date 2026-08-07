# GH#1 — Register Figma MCP server in Goose Desktop

**Project:** Content creation (Kovan Labs)
**Labels:** project-task, area:figma
**Status:** Registered and verified (Goose Desktop)
**Last updated:** 2026-08-07

## 1. Summary

The Figma Developer MCP server is registered as a **stdio extension in Goose
Desktop** and verified to launch and handshake successfully. Goose can see
the Figma MCP tools that Figma exposes to non-listed MCP clients.

## 2. Where the registration lives

The extension is registered in Goose Desktop's user config
(`~/.config/goose/config.yaml`), under `extensions.figma`:

```yaml
extensions:
  figma:
    enabled: true
    type: stdio
    name: figma
    description: Figma Developer MCP - brand-compliant content creation from Figma templates
    cmd: npx
    args:
    - -y
    - figma-developer-mcp@latest
    - --image-dir=/home/thansika/Documents/Content creation/output
    - --stdio
    envs: {}
    env_keys:
    - FIGMA_API_KEY
    timeout: 300
```

Key points:

- **Explicit image output directory:** `--image-dir` is set to
  `/home/thansika/Documents/Content creation/output`. This removes the
  default (current-working-directory) image write target, so image
  downloads always land in the known `output/` folder.
- **API key via environment:** the `env_keys: [FIGMA_API_KEY]` entry tells
  Goose to inject the `FIGMA_API_KEY` value from its secrets store
  (`~/.config/goose/secrets.yaml`) into the server process. The key is never
  committed to the repo.

## 3. Server launch command

The registered command (equivalent of the docs example):

```bash
npx -y figma-developer-mcp@latest \
  --image-dir="/home/thansika/Documents/Content creation/output" \
  --stdio
```

Verified: `npx -y figma-developer-mcp@latest --help` runs (figma-developer-mcp
v0.13.2, exit 0), and the stdio MCP handshake succeeds:

- `initialize` → `Figma MCP Server v0.13.2` (protocol 2024-11-05)
- `tools/list` → 2 tools: `get_figma_data`, `download_figma_images`

These are exactly the tools Figma exposes to clients not in its supported MCP
client catalog.

## 4. Supported-client limitation (important)

Goose is **not** listed in Figma's supported MCP client catalog, so it is
exposed **only** the read/download subset:

- `figma__get_figma_data`
- `figma__download_figma_images`

It does **not** get the full Figma MCP tool set (no export/edit control). See
`figma_issues_and_alternative_approach.md` and
`docs/figma-template-extraction-workflow.md` (§1) for the full analysis. The
full tool set is available through the **VS Code** client instead.

## 5. Operational constraint

Figma's MCP integration is limited to **6 tool calls per month**. Those calls
were consumed during connection testing and one-time template inspection.
**No routine or automated poster generation may issue Figma MCP tool calls** —
the allowance would be exhausted immediately. Figma MCP is reserved for
rare, human-initiated one-time template extraction. Routine generation uses
the local HTML template workflow (`figma-export/` + `generate_poster.py`).

## 6. Verification / sign-off

- [x] Figma Developer MCP extension added to Goose Desktop
      (`~/.config/goose/config.yaml` → `extensions.figma`).
- [x] Server command launches successfully (`npx ... --help`, exit 0).
- [x] Explicit image output directory set (`--image-dir=.../output`).
- [x] `FIGMA_API_KEY` wired through Goose secrets (`env_keys`) —
      key available to the server process.
- [x] MCP stdio handshake verified: `initialize` OK,
      `tools/list` returns `get_figma_data` + `download_figma_images`.
- [x] Supported-client limitation and 6-calls/month allowance recorded
      (this doc + `figma_issues_and_alternative_approach.md` +
      `docs/figma-template-extraction-workflow.md`).
