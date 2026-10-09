<script setup lang="ts">
/**
 * The title slide, and the only slide with no chrome.
 *
 * Title and subtitle are the markdown's `#` and `##`, so the deck writes them where it writes
 * everything else. What is left is the metadata a talk carries — who is speaking, where, and when —
 * which is data rather than prose and arrives as frontmatter.
 *
 * Two marks, each a slot: the venue's above the title and the affiliation's in the bottom-left
 * corner. A mark belongs to the deck, not to the machinery, and this project ships nobody's — so
 * each slot shows a placeholder until the deck names an image. `themeConfig` names one once for a
 * deck, and a slide's prop overrides it. An empty string leaves the slot empty.
 *
 * Bottom right, the slides themselves: a QR code to where they are shared (`answer-first`), so the
 * room can follow on their own screens from the first minute. It is the same `Share` component the
 * conclusion places, read from the same `themeConfig`, without the contact.
 *
 * The placeholders are imported rather than served. Slidev does not serve a theme's `public/` at a
 * deck's root, so a fallback URL pointing there would be a broken image on every cover that named
 * no mark; an import is carried into whichever deck the theme is built into.
 */
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import { resolveAssetUrl } from '@slidev/client/layoutHelper.ts'
import affiliationPlaceholder from '../assets/placeholders/affiliation-logo.svg?url'
import venuePlaceholder from '../assets/placeholders/venue-logo.svg?url'
import Share from '../components/Share.vue'

const props = defineProps<{
  /**
   * Who is speaking. Defaults to the deck's own `author`, which is where Slidev already keeps it —
   * and `speaker` rather than `author` because Slidev reserves that word: on the first slide of a
   * deck, which is where a cover normally lives, it belongs to the headmatter and never reaches a
   * layout as a prop.
   */
  speaker?: string
  /** Where: the conference, the seminar, the course. */
  venue?: string
  /** When, written however the deck wants it read. */
  date?: string
  /** The venue's logo URL, overriding `themeConfig.venueLogo` for this slide. */
  venueLogo?: string
  /** The affiliation's logo URL, overriding `themeConfig.affiliationLogo` for this slide. */
  affiliationLogo?: string
  /** The QR code to the shared slides, overriding `themeConfig.shareQr` for this slide. */
  shareQr?: string
  /** Where that code leads, overriding `themeConfig.shareUrl` for this slide. */
  shareUrl?: string
}>()

const { $slidev } = useSlideContext()

/**
 * The slide's own image, then the deck's, then the placeholder. `??` rather than `||`, so an empty
 * string is an answer — no mark — and not a request for the placeholder. A path the deck names is
 * resolved against the base the deck is hosted under. The placeholder is a bundled import, which
 * Vite resolved already.
 */
function markOrPlaceholder(own: string | undefined, deck: string | undefined, placeholder: string) {
  const named = own ?? deck
  return named == null ? placeholder : resolveAssetUrl(named)
}

const venueLogo = computed(() =>
  markOrPlaceholder(props.venueLogo, $slidev.themeConfigs.venueLogo, venuePlaceholder),
)
const affiliationLogo = computed(() =>
  markOrPlaceholder(props.affiliationLogo, $slidev.themeConfigs.affiliationLogo, affiliationPlaceholder),
)
const meta = computed(() =>
  [props.speaker || $slidev.configs.author, props.venue, props.date].filter(Boolean),
)
</script>

<template>
  <div class="slidev-layout cover">
    <img v-if="venueLogo" class="legible-cover-venue-logo" :src="venueLogo" alt="" />
    <slot />
    <div v-if="meta.length" class="legible-cover-meta">
      <span v-for="line of meta" :key="line">{{ line }}</span>
    </div>
    <img
      v-if="affiliationLogo"
      class="legible-cover-affiliation-logo"
      :src="affiliationLogo"
      alt=""
    />
    <Share
      class="legible-cover-share"
      :share-qr="shareQr"
      :share-url="shareUrl"
      contact=""
    />
  </div>
</template>
