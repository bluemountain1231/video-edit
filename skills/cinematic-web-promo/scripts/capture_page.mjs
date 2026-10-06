#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
import {chromium} from 'playwright';

const args = process.argv.slice(2);
const value = (flag, fallback) => {
  const i = args.indexOf(flag);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};

const url = value('--url');
const outDir = path.resolve(value('--out', 'captures'));
const width = Number(value('--width', '1920'));
const height = Number(value('--height', '1080'));
const locale = value('--locale', 'en-US');
const hide = value('--hide', '');

if (!url) {
  console.error('Usage: capture_page.mjs --url https://example.com [--out captures] [--locale en-US]');
  process.exit(2);
}

await fs.mkdir(outDir, {recursive: true});
const browser = await chromium.launch({headless: true});
const context = await browser.newContext({viewport: {width, height}, locale, deviceScaleFactor: 1});
const page = await context.newPage();
await page.goto(url, {waitUntil: 'networkidle', timeout: 90000});
await page.evaluate(async () => {
  const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
  const max = document.documentElement.scrollHeight - innerHeight;
  for (let y = 0; y <= max; y += Math.max(420, Math.floor(innerHeight * 0.72))) {
    scrollTo({top: y, behavior: 'instant'});
    await delay(180);
  }
  scrollTo({top: 0, behavior: 'instant'});
  await delay(600);
});

if (hide) {
  const selectors = hide.split(',').map((x) => x.trim()).filter(Boolean);
  await page.addStyleTag({content: selectors.map((s) => `${s}{display:none!important}`).join('\n')});
}

await page.screenshot({path: path.join(outDir, 'hero.png'), fullPage: false});
await page.screenshot({path: path.join(outDir, 'full-page.png'), fullPage: true});
const documentHeight = await page.evaluate(() => document.documentElement.scrollHeight);
await fs.writeFile(
  path.join(outDir, 'capture.json'),
  JSON.stringify({url, capturedAt: new Date().toISOString(), viewport: {width, height}, documentHeight, locale, hiddenSelectors: hide}, null, 2),
);
await browser.close();
console.log(outDir);
