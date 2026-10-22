// Copyright (C) 2026 Xiao Fan <xiaofan140@gmail.com>
// SPDX-License-Identifier: GPL-3.0-or-later
// Optional local Mermaid rendering; never installs packages or downloads assets.
import fs from 'node:fs/promises';
import path from 'node:path';
import {execFileSync} from 'node:child_process';
import {createRequire} from 'node:module';
import {fileURLToPath, pathToFileURL} from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const help = `Render a Campus Mermaid diagram (run from the repository root).
Required for rendering:
  --input FILE       Mermaid source
  --output PREFIX    Output prefix without an extension
  --runtime DIR      Existing npm prefix containing node_modules/
  --browser FILE     Existing Chrome/Chromium executable
Style:
  --profile NAME     theme/NAME/profile.tex (default: general)
  --root DIR         Repository root (default: current working directory)
  --font-size PX     Final CSS font size (default: 14.6, about 11 TeX pt)
  --latin-font FILE  Font file (default: kpsewhich Carlito-Regular.ttf)
  --cjk-font FILE    Font file (default: kpsewhich FandolHei-Regular.otf)
  --latin-bold FILE  Matching bold font (optional with custom regular font)
  --cjk-bold FILE    Matching bold font (optional with custom regular font)
  --config-only      Print resolved config JSON; needs no runtime or browser
  --no-sandbox       Explicit browser sandbox opt-out for environments needing it
  --help             Show this help
Outputs: PREFIX.svg, PREFIX.pdf, PREFIX.png, PREFIX.render.json.
Layout and size are defined by the source; the PDF is not rescaled.`;

function argumentsFrom(argv) {
  const options = {};
  const flags = new Set(['help', 'config-only', 'no-sandbox']);
  const values = new Set(['input', 'output', 'runtime', 'browser', 'profile', 'root',
    'font-size', 'latin-font', 'cjk-font', 'latin-bold', 'cjk-bold']);
  for (let i = 0; i < argv.length; i++) {
    const name = argv[i].replace(/^--/, '');
    if (!argv[i].startsWith('--') || (!flags.has(name) && !values.has(name))) {
      throw Error(`Unknown argument: ${argv[i]}`);
    }
    if (flags.has(name)) options[name] = true;
    else {
      const value = argv[++i];
      if (!value || value.startsWith('--')) throw Error(`Missing value for --${name}`);
      options[name] = value;
    }
  }
  return options;
}

function mainColor(source) {
  // TeX comments must not supply a color that differs from the active definition.
  source = source.replace(/(?<!\\)%[^\n]*/g, '');
  const match = source.match(/\\definecolor\s*\{maincolor\}\s*\{(HTML|RGB(?:\/cmyk)?|rgb)\}\s*\{([^}]+)\}/);
  if (!match) throw Error('maincolor must be a literal HTML, RGB, RGB/cmyk or rgb definition.');
  if (match[1] === 'HTML') {
    if (!/^[\da-f]{6}$/i.test(match[2].trim())) throw Error('Invalid HTML maincolor.');
    return '#' + match[2].trim().toLowerCase();
  }
  const rgb = match[2].split('/')[0].split(',').map(Number);
  const limit = match[1] === 'rgb' ? 1 : 255;
  if (rgb.length !== 3 || rgb.some(n => !Number.isFinite(n) || n < 0 || n > limit)) {
    throw Error('Invalid RGB maincolor.');
  }
  return '#' + rgb.map(n => Math.round(n * 255 / limit).toString(16).padStart(2, '0')).join('');
}

function resolveTemplate(value, primary, fontSize) {
  if (Array.isArray(value)) return value.map(v => resolveTemplate(v, primary, fontSize));
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, resolveTemplate(v, primary, fontSize)]));
  }
  if (typeof value !== 'string') return value;
  if (value === '{{fontSizeNumber}}') return fontSize;
  return value.replaceAll('{{fontSize}}', String(fontSize)).replace(/\{\{color:(\d+)\}\}/g, (_, percent) => {
    return '#' + [1, 3, 5].map(i => Math.round(
      parseInt(primary.slice(i, i + 2), 16) * Number(percent) / 100 + 255 * (1 - Number(percent) / 100)
    ).toString(16).padStart(2, '0')).join('');
  });
}

function texFont(filename) {
  const found = execFileSync('kpsewhich', [filename], {encoding: 'utf8'}).trim();
  if (!found) throw Error(`Missing TeX font: ${filename}`);
  return found;
}

async function fontCSS(options) {
  const specs = [
    ['CampusLatin', options['latin-font'] || texFont('Carlito-Regular.ttf'), 400],
    ['CampusCJK', options['cjk-font'] || texFont('FandolHei-Regular.otf'), 400],
    ['CampusLatin', options['latin-bold'] || (!options['latin-font'] && texFont('Carlito-Bold.ttf')), 700],
    ['CampusCJK', options['cjk-bold'] || (!options['cjk-font'] && texFont('FandolHei-Bold.otf')), 700],
  ];
  let css = '';
  for (const [family, file, weight] of specs) {
    if (!file) continue;
    const mime = path.extname(file).toLowerCase() === '.otf' ? 'font/otf' : 'font/ttf';
    css += `@font-face{font-family:"${family}";font-weight:${weight};src:url(data:${mime};base64,${(await fs.readFile(file)).toString('base64')});}\n`;
  }
  return css;
}

async function main() {
  const options = argumentsFrom(process.argv.slice(2));
  if (options.help) { console.log(help); return; }
  const root = path.resolve(options.root || '.');
  const profile = options.profile || 'general';
  if (!/^[a-zA-Z0-9_-]+$/.test(profile)) throw Error('Use a profile directory name, not a path.');
  const fontSize = Number(options['font-size'] || 14.6);
  if (!Number.isFinite(fontSize) || fontSize <= 0) throw Error('Font size must be positive.');
  const primary = mainColor(await fs.readFile(path.join(root, 'theme', profile, 'profile.tex'), 'utf8'));
  const template = JSON.parse(await fs.readFile(path.join(here, '../assets/config.json'), 'utf8'));
  const config = resolveTemplate(template, primary, fontSize);
  if (options['config-only']) { console.log(JSON.stringify(config, null, 2)); return; }
  for (const key of ['input', 'output', 'runtime', 'browser']) {
    if (!options[key]) throw Error(`--${key} is required for rendering. See --help.`);
  }
  const runtime = path.resolve(options.runtime);
  const require = createRequire(path.join(runtime, 'package.json'));
  const puppeteer = require('puppeteer');
  const mermaidDir = path.join(runtime, 'node_modules/mermaid');
  const cliDir = path.join(runtime, 'node_modules/@mermaid-js/mermaid-cli');
  const definition = await fs.readFile(options.input, 'utf8');
  const fonts = await fontCSS(options);
  const prefix = path.resolve(options.output);
  await fs.mkdir(path.dirname(prefix), {recursive: true});
  const browser = await puppeteer.launch({executablePath: path.resolve(options.browser),
    args: options['no-sandbox'] ? ['--no-sandbox'] : []});
  try {
    const page = await browser.newPage();
    const warnings = [];
    page.on('console', msg => { if (['warn', 'error'].includes(msg.type())) warnings.push(msg.text()); });
    await page.setViewport({width: 1600, height: 1200, deviceScaleFactor: 2});
    // Use only local package assets. Sources are never sent to a rendering service.
    await page.setRequestInterception(true);
    page.on('request', request => /^(https?|wss?):/.test(request.url()) ? request.abort() : request.continue());
    await page.goto(pathToFileURL(path.join(cliDir, 'dist/index.html')).href);
    await page.addStyleTag({content: fonts + '\nbody{margin:0;background:white;}' + config.themeCSS});
    await page.addScriptTag({path: path.join(mermaidDir, 'dist/mermaid.js')});
    const zen = /^\s*zenuml\b/m.test(definition);
    if (zen) await page.addScriptTag({path: path.join(runtime,
      'node_modules/@mermaid-js/mermaid-zenuml/dist/mermaid-zenuml.js')});
    const raw = await page.evaluate(async ({config, definition, fonts, fontSize, zen}) => {
      await Promise.all([
        document.fonts.load(`${fontSize}px CampusLatin`, 'Agent User Tool'),
        document.fonts.load(`bold ${fontSize}px CampusLatin`, 'Agent'),
        document.fonts.load(`${fontSize}px CampusCJK`, '输入材料任务反馈'),
        document.fonts.load(`bold ${fontSize}px CampusCJK`, '系统'),
      ]);
      await document.fonts.ready;
      if (zen) await window.mermaid.registerExternalDiagrams([window['mermaid-zenuml']]);
      window.mermaid.initialize(config);
      const rendered = await window.mermaid.render('campusDiagram', definition);
      document.getElementById('container').innerHTML = rendered.svg;
      const svg = document.querySelector('#container > svg');
      svg.style.maxWidth = 'none'; svg.style.display = 'block';
      let vb = svg.viewBox.baseVal;
      if (!vb.width || !vb.height) {
        const r = svg.getBoundingClientRect();
        svg.setAttribute('viewBox', `0 0 ${r.width} ${r.height}`); vb = svg.viewBox.baseVal;
      }
      svg.setAttribute('width', vb.width); svg.setAttribute('height', vb.height);
      const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
      const style = document.createElementNS('http://www.w3.org/2000/svg', 'style');
      style.textContent = fonts + config.themeCSS;
      defs.appendChild(style); svg.prepend(defs);
      const s = svg.getBoundingClientRect();
      const texts = [...svg.querySelectorAll('text,tspan,foreignObject div,foreignObject span,foreignObject p')]
        .filter(el => !el.childElementCount && el.textContent.trim()).map(el => {
          const r = el.getBoundingClientRect();
          return {text: el.textContent, font: getComputedStyle(el).fontFamily,
            size: getComputedStyle(el).fontSize,
            clipped: r.width > 0 && (r.left < s.left - 1 || r.right > s.right + 1 || r.top < s.top - 1 || r.bottom > s.bottom + 1)};
        });
      return JSON.stringify({width: vb.width, height: vb.height, texts,
        svg: new XMLSerializer().serializeToString(svg)});
    }, {config, definition, fonts, fontSize, zen});
    const result = JSON.parse(raw);
    if (!(result.width > 0 && result.height > 0)) throw Error('Diagram has no renderable dimensions.');
    await page.setViewport({width: Math.ceil(result.width), height: Math.ceil(result.height), deviceScaleFactor: 2});
    await fs.writeFile(prefix + '.svg', result.svg);
    await page.screenshot({path: prefix + '.png', clip: {x: 0, y: 0, width: Math.ceil(result.width), height: Math.ceil(result.height)}});
    await page.pdf({path: prefix + '.pdf', width: `${result.width}px`, height: `${result.height}px`,
      margin: {top: 0, bottom: 0, left: 0, right: 0}, printBackground: true, pageRanges: '1'});
    const cdp = await page.createCDPSession();
    await cdp.send('DOM.enable'); await cdp.send('CSS.enable');
    const {root: dom} = await cdp.send('DOM.getDocument');
    const {nodeIds} = await cdp.send('DOM.querySelectorAll', {nodeId: dom.nodeId,
      selector: 'svg text,svg tspan,svg foreignObject div,svg foreignObject span,svg foreignObject p'});
    const actualFonts = new Map();
    for (const nodeId of nodeIds) {
      for (const f of (await cdp.send('CSS.getPlatformFontsForNode', {nodeId})).fonts) actualFonts.set(f.postScriptName, f);
    }
    delete result.svg;
    const report = {...result, profile, primary, fontSize, actualFonts: [...actualFonts.values()], warnings,
      command: process.argv.slice(1), versions: {
        mermaid: JSON.parse(await fs.readFile(path.join(mermaidDir, 'package.json'))).version,
        cli: JSON.parse(await fs.readFile(path.join(cliDir, 'package.json'))).version,
      }};
    await fs.writeFile(prefix + '.render.json', JSON.stringify(report, null, 2) + '\n');
    const clipped = result.texts.filter(t => t.clipped);
    console.log(`${options.output}: ${result.width.toFixed(1)} x ${result.height.toFixed(1)} CSS px; ${clipped.length} text bounds warnings.`);
    if (clipped.length) process.exitCode = 2;
  } finally { await browser.close(); }
}

main().catch(error => { console.error(error.message); process.exitCode = 1; });
