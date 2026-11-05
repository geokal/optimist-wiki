# Publish and update the wiki

## First publication

1. Create an empty **public** GitHub repository, for example `optimist-wiki`. Avoid initializing it with a README, license, or `.gitignore` if this local folder is not already a Git repository.
2. In PowerShell, from this folder, create a repository and push it. Replace the URL with the one GitHub shows for your repository. If this folder is already a Git repository or has a remote, inspect its existing branch and remotes instead of reinitializing or replacing them.

   ```powershell
   git init -b main
   git add .
   git commit -m "Add Optimist wiki showcase"
   git remote add origin https://github.com/YOUR-USERNAME/optimist-wiki.git
   git push -u origin main
   ```

3. On GitHub, open your repository's **Settings → Pages**. Under **Build and deployment → Source**, choose **GitHub Actions**. You need repository administrator or maintainer access. The existing `.github/workflows/pages.yml` is the deployment workflow; you do not need to create another one.
4. Open the **Actions** tab and check the **Publish documentation** workflow. If the first push happened before Pages was enabled, select **Run workflow** on the `main` branch. Check **Settings → Pages → Visit site** after the run succeeds.
5. The usual project-site URL is `https://YOUR-USERNAME.github.io/optimist-wiki/`. Replace both the username and repository name with yours. Add the resulting URL to the repository's About section or share it directly.

The workflow runs on pushes to `main` and can also be started manually. If your default branch has another name, update the `branches` entry in `.github/workflows/pages.yml`. Changes can take several minutes to appear. See GitHub's [Pages configuration guide](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site) and [site URL documentation](https://docs.github.com/en/pages/getting-started-with-github-pages/what-is-github-pages).

## Refresh with a new Qoder export

1. Save a backup or commit your existing work. Copy the new export's `content/` and `meta/` into this repository, reviewing additions and removals carefully. Preserve the site files, `tools/`, and `.github/`.
2. From the repository root, generate the index and sidebar:

   ```powershell
   uv run --no-project python tools/generate_wiki_navigation.py --format-references
   ```

   This rewrites `README.md` and `_sidebar.md`; `--format-references` also moves each Qoder reference list to the end of its Markdown page. The generator reports metadata pages it cannot find; resolve those mappings before publishing. To convert Qoder's `file://` source links to non-clickable paths, also add `--repair-source-links`. Both options rewrite Markdown files, so review or back up the export first; if the original source is public, a link rewrite to that repository may be preferable.
3. If the Architecture Overview Mermaid source changed, regenerate its special Qoder-rendered SVG using [the diagram instructions](tools/README.md). Its source hash prevents a stale diagram being shown. If the definition did not change, the existing SVG remains valid.
4. Preview locally:

   ```powershell
   uv run --no-project python -m http.server 8000
   ```

   Open `http://localhost:8000`, inspect navigation, search and representative diagrams, and stop the server with `Ctrl+C`. The site loads Docsify and Mermaid from a CDN, so the preview needs internet access.
5. Review the changes, then commit and push to `main`. The Pages workflow publishes the updated site.

For agent-assisted updates, invoke `$qoder-wiki-pages` and identify the new export and target repository.

## Troubleshooting

- **No Pages URL or failed deployment:** confirm the repository is public, Pages source is **GitHub Actions**, Actions are enabled, and the workflow ran on the configured branch. Inspect its logs under **Actions**.
- **Old site still displayed:** wait for the workflow to complete, then refresh the page without cache. Verify the push went to the branch named in the workflow.
- **Architecture diagram says its source changed:** regenerate the SVG and manifest as described above.
- **Site remains at “Loading wiki…”:** check your browser's network console and access to `cdn.jsdelivr.net`.

GitHub Pages publishes the workflow's uploaded repository content publicly. Review the export, including metadata and generated examples, before pushing. AI-generated technical documentation should also be checked against the source for accuracy.
