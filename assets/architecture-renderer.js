// Generated from the Markdown with Qoder's locally installed renderer.
// Only the diagram output is published; no Qoder application code is distributed.
const manifestUrl = new URL('./diagrams/architecture-overview.json', import.meta.url);
const svgUrl = new URL('./diagrams/architecture-overview.svg', import.meta.url);

export async function renderArchitecture(id, source) {
  const normalized = source.replace(/\r\n?/g, '\n').trim();
  const hash = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(normalized));
  const actual = Array.from(new Uint8Array(hash), byte => byte.toString(16).padStart(2, '0')).join('');
  const [manifestResponse, svgResponse] = await Promise.all([fetch(manifestUrl), fetch(svgUrl)]);
  if (!manifestResponse.ok || !svgResponse.ok) throw new Error('Architecture diagram asset is unavailable.');
  const manifest = await manifestResponse.json();
  if (actual !== manifest.sourceSha256) {
    throw new Error('Architecture source changed. Regenerate its SVG using tools/export_architecture_diagram.cjs.');
  }
  return {svg: await svgResponse.text()};
}
