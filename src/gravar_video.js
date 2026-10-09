#!/usr/bin/env node
// Grava assets/fontes/video.html quadro a quadro e codifica em MP4 (H.264) com ffmpeg.
// Requer Node.js, o pacote puppeteer e ffmpeg no PATH. O vídeo sai sem áudio: a narração é humana.
//
// Uso:
//   node src/gravar_video.js --saida video.mp4 [--guia] [--fps 30] [--inicio 0] [--fim 999] [--chrome CAMINHO]
const path = require('path');
const { spawn } = require('child_process');
const puppeteer = require('puppeteer');

const arg = (nome, padrao) => { const i = process.argv.indexOf('--' + nome); return i > 0 ? process.argv[i + 1] : padrao; };
const RAIZ = path.resolve(__dirname, '..');
const tempos = require(path.join(RAIZ, 'assets', 'fontes', 'video-tempos.json'));
const saida = arg('saida', 'video.mp4');
const guia = process.argv.includes('--guia');
const fps = +arg('fps', tempos.fps);
const inicio = +arg('inicio', 0);
const fim = Math.min(+arg('fim', tempos.total), tempos.total);

(async () => {
  const navegador = await puppeteer.launch({ headless: 'shell', executablePath: arg('chrome', undefined),
    args: ['--no-sandbox', '--disable-gpu', '--hide-scrollbars', '--font-render-hinting=none'] });
  const pagina = await navegador.newPage();
  await pagina.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  const url = 'file://' + path.join(RAIZ, 'assets', 'fontes', 'video.html') + (guia ? '?guia' : '');
  await pagina.goto(url, { waitUntil: 'networkidle0' });
  await pagina.evaluate(() => document.fonts.ready);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg',
    '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', saida],
    { stdio: ['pipe', 'inherit', 'inherit'] });
  const n = Math.round((fim - inicio) * fps);
  for (let k = 0; k < n; k++) {
    await pagina.evaluate(t => window.render(t), inicio + k / fps);
    const img = await pagina.screenshot({ type: 'jpeg', quality: 92 });
    if (!ff.stdin.write(img)) await new Promise(r => ff.stdin.once('drain', r));
    if (k % (fps * 10) === 0) process.stdout.write(`${((inicio + k / fps)).toFixed(0)} s de ${fim.toFixed(0)} s\n`);
  }
  ff.stdin.end();
  await new Promise(r => ff.on('close', r));
  await navegador.close();
  console.log('ok:', saida);
})();
