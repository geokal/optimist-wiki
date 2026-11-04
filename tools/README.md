# Updating the architecture diagram

The Architecture Overview page displays an SVG exported with Qoder's installed
diagram renderer. The Markdown remains the source; a SHA-256 check prevents an
old SVG from being displayed if the Mermaid definition changes.

To regenerate it, use Node.js, an installed Playwright package, a Chromium-based
browser, and the `app.asar` from the Qoder installation. For example, on this
machine:

```powershell
node tools/export_architecture_diagram.cjs `
  --qoder-asar 'C:/Users/bigbu/AppData/Local/Programs/Qoder/.qoder-versions/0.5.3/resources/app.asar' `
  --browser 'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe' `
  --playwright-module 'C:/Users/bigbu/.agents/skills/playwright/node_modules/playwright'
```

Adjust the paths for your installation. The export updates both
`assets/diagrams/architecture-overview.svg` and its JSON manifest. Review and
commit both files together. The current script checks for the existing diagram's
11 nodes and 17 connections; update that check if the architecture changes.

Qoder is needed only when regenerating this SVG, not for viewing or publishing
the wiki. The export contains the rendered diagram, not Qoder application code.
