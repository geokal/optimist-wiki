#!/usr/bin/env node
// Re-export just the documentation SVG. The installed application bundle is
// read into an isolated, offline browser and is never copied into the repository.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const root = path.resolve(__dirname, '..');
const sourcePath = path.join(root, 'content/Architecture Overview/Architecture Overview.md');

function readAsarFile(archive, relativePath) {
  const fd = fs.openSync(archive, 'r');
  try {
    const prefix = Buffer.alloc(16);
    fs.readSync(fd, prefix, 0, prefix.length, 0);
    const header = Buffer.alloc(prefix.readUInt32LE(12));
    fs.readSync(fd, header, 0, header.length, 16);
    let entry = JSON.parse(header.toString('utf8'));
    for (const segment of relativePath.split('/')) entry = entry.files[segment];
    if (entry.unpacked) throw new Error('Expected an archived renderer file.');
    const body = Buffer.alloc(entry.size);
    fs.readSync(fd, body, 0, body.length, 8 + prefix.readUInt32LE(4) + Number(entry.offset));
    return body;
  } finally {
    fs.closeSync(fd);
  }
}

async function main() {
  const args = process.argv.slice(2);
  const option = name => {
    const index = args.indexOf(name);
    return index < 0 ? undefined : args[index + 1];
  };
  const archive = option('--qoder-asar');
  const browserPath = option('--browser');
  if (!archive || !browserPath) {
    throw new Error('Usage: node tools/export_architecture_diagram.cjs --qoder-asar <installed app.asar> --browser <Chromium executable> [--playwright-module <installed playwright directory>]');
  }
  const {chromium} = require(option('--playwright-module') || 'playwright');
  const markdown = fs.readFileSync(sourcePath, 'utf8');
  const block = [...markdown.matchAll(/```mermaid\s*\n([\s\S]*?)```/g)]
    .find(match => match[1].includes('System Level (MEO)') && match[1].includes('External Systems'));
  if (!block) throw new Error('Architecture overview diagram was not found.');
  const source = block[1].replace(/\r\n?/g, '\n').trim();
  const sourceSha256 = crypto.createHash('sha256').update(source).digest('hex');
  const runtime = readAsarFile(archive, 'out/preload/pluginViewDiagramRuntime.cjs');
  const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'architecture-theme.json'), 'utf8'));
  const browser = await chromium.launch({headless: true, executablePath: browserPath});
  try {
    const page = await browser.newPage({viewport: {width: 1600, height: 1600}});
    await page.route(/^https?:/, route => route.abort());
    await page.setContent('<!doctype html><body style="margin:0;background:#252b26"><div id="diagram"></div></body>');
    await page.addScriptTag({content: runtime.toString('utf8')});
    const output = await page.evaluate(async ({source, config}) => {
      const renderer = globalThis.__qoderPluginViewMermaidRuntime;
      renderer.initialize(config);
      const {svg} = await renderer.render('architecture-overview', source);
      const container = document.querySelector('#diagram');
      container.innerHTML = svg;
      const element = container.querySelector('svg');
      const [, , width, height] = element.getAttribute('viewBox').split(/[\s,]+/).map(Number);
      element.setAttribute('width', String(width));
      element.setAttribute('height', String(height));
      element.style.maxWidth = 'none';
      element.style.background = '#252b26';
      return {
        svg: new XMLSerializer().serializeToString(element), width, height,
        nodes: [...element.querySelectorAll('.node')].map(node => ({
          id: node.id, label: node.textContent, transform: node.getAttribute('transform'),
        })),
        edges: element.querySelectorAll('.flowchart-link').length,
      };
    }, {source, config});
    if (output.nodes.length !== 11 || output.edges !== 17) {
      throw new Error(`Incomplete export: ${output.nodes.length} nodes, ${output.edges} edges.`);
    }
    const directory = path.join(root, 'assets/diagrams');
    fs.mkdirSync(directory, {recursive: true});
    fs.writeFileSync(path.join(directory, 'architecture-overview.svg'), output.svg + '\n');
    fs.writeFileSync(path.join(directory, 'architecture-overview.json'), JSON.stringify({
      source: 'content/Architecture Overview/Architecture Overview.md',
      sourceSha256,
      svgSha256: crypto.createHash('sha256').update(output.svg + '\n').digest('hex'),
      renderer: 'Qoder installed diagram runtime; Mermaid 11.16.0; qoder-flowchart-v1',
      width: output.width, height: output.height,
      nodes: output.nodes.length, edges: output.edges,
    }, null, 2) + '\n');
    console.log(`Exported ${output.nodes.length} nodes and ${output.edges} edges; ${output.width} x ${output.height}; source SHA-256 ${sourceSha256}.`);
  } finally {
    await browser.close();
  }
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
