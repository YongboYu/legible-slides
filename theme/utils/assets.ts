import { resolveAssetUrl } from '@slidev/client/layoutHelper.ts'

/**
 * An image URL a deck hands the theme, as the browser has to ask for it where the deck is hosted.
 *
 * A path from the deck's root, `/logo.png` out of its public folder, is resolved against the base
 * the deck is built for, as Slidev does for the images it finds in markdown. A URL that starts with
 * the base already is left as it is: that is an image the deck imports, or one the theme bundles,
 * and Vite gave it the base when it bundled it. Under the default base, `/`, every path is both,
 * and nothing changes. The one path this reads wrong is a public file inside a folder named like
 * the base, `public/talk/` under `/talk/`, which is taken for a resolved one.
 */
export function assetUrl(url: string): string {
  return url.startsWith(import.meta.env.BASE_URL) ? url : resolveAssetUrl(url)
}
