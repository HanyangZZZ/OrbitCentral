#!/usr/bin/env node
/**
 * Export the slideshow as a single-page PDF.
 * Measures the full scroll height under print media, then generates a PDF
 * whose page size exactly matches the content — one page, no pagination.
 */
import puppeteer from 'puppeteer-core';

const URL = 'http://localhost:8090';
const OUT = 'Orbit-Presentation.pdf';
const CHROME = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

(async () => {
  const browser = await puppeteer.launch({
    executablePath: CHROME,
    headless: 'new',
    args: ['--no-sandbox', '--disable-gpu'],
  });

  const page = await browser.newPage();

  // Use a wide viewport so content renders in its natural wide layout
  await page.setViewport({ width: 1400, height: 900 });
  await page.goto(URL, { waitUntil: 'networkidle0', timeout: 30000 });

  // Wait extra for Mermaid diagrams and live API data
  await new Promise(r => setTimeout(r, 5000));

  // Switch to print media so @media print CSS is active during measurement
  await page.emulateMediaType('print');
  await new Promise(r => setTimeout(r, 500));

  // Measure the full content dimensions (print CSS is active: no sidebar,
  // cover min-height:0, etc.)
  const dims = await page.evaluate(() => ({
    width: document.documentElement.scrollWidth,
    height: document.documentElement.scrollHeight,
  }));

  console.log(`Content size: ${dims.width} × ${dims.height} px`);

  // Generate a single-page PDF with exact content dimensions
  await page.pdf({
    path: OUT,
    width: `${dims.width}px`,
    height: `${dims.height + 2}px`,   // +2 avoids sub-pixel overflow onto page 2
    printBackground: true,
    margin: { top: 0, right: 0, bottom: 0, left: 0 },
  });

  console.log(`✅ Exported → ${OUT} (${dims.width}×${dims.height}px, 1 page)`);
  await browser.close();
})();
