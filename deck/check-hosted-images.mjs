// Every image on every slide loads when the deck is hosted under a path.
//
//     node check-hosted-images.mjs <dist> <base>
//
// <dist> is a build made with `slidev build --base <base>`, such as /talk/. It is served here under
// that path, the way a project's GitHub Pages serves a deck, and each slide is opened in Chromium.
// Slidev resolves the images it finds in markdown against the base, and leaves an image a component
// binds to the theme. A path that skips the base still loads at /, so only a hosted build shows it.
// Exits 1 if any image failed to load, after naming each one, or if it found no slides to open.
import { readFile } from 'node:fs/promises'
import { createServer } from 'node:http'
import { extname, join } from 'node:path'
import { chromium } from 'playwright-chromium'

const [dist, base] = process.argv.slice(2)
if (!dist || !base?.startsWith('/') || !base.endsWith('/')) {
  console.error('usage: node check-hosted-images.mjs <dist> </base/>')
  process.exit(2)
}

const types = {
  '.css': 'text/css',
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2',
}

// Only paths under the base exist, so a request that skipped it is a 404, as it is when hosted. A
// path with no extension is a slide's route, and the app answers it.
const server = createServer(async (request, response) => {
  const path = decodeURIComponent(new URL(request.url, 'http://localhost').pathname)
  const file = path.startsWith(base) ? join(dist, path.slice(base.length)) : null
  const route = file && !extname(path) ? join(dist, 'index.html') : file
  const body = route && (await readFile(route).catch(() => null))
  if (!body) {
    response.writeHead(404).end()
    return
  }
  response.writeHead(200, { 'content-type': types[extname(route)] ?? 'application/octet-stream' })
  response.end(body)
}).listen(0)
const root = `http://localhost:${server.address().port}${base}`

const browser = await chromium.launch()
const page = await browser.newPage()
// The overview draws every slide, which is the one count a built deck gives out.
await page.goto(`${root}overview`, { waitUntil: 'networkidle' })
const total = await page.$$eval('.slidev-page', (all) => all.length)

let broken = 0
let loaded = 0
for (let slide = 1; slide <= total; slide++) {
  await page.goto(`${root}${slide}`, { waitUntil: 'networkidle' })
  const images = await page.$$eval('.slidev-page img', (all) =>
    all.map((image) => [image.getAttribute('src'), image.complete && image.naturalWidth > 0]),
  )
  for (const [src, ok] of images) {
    if (ok) {
      loaded++
    } else {
      broken++
      console.log(`slide ${slide}: ${src} did not load under ${base}`)
    }
  }
}
await browser.close()
server.close()

console.log(`${loaded} images loaded and ${broken} did not, over ${total} slides under ${base}`)
process.exit(broken || !total ? 1 : 0)
