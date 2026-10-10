<script setup lang="ts">
/**
 * The slides, handed over: a QR code to where they are shared, the link written out under it, and
 * on the close the presenter's contact.
 *
 * `answer-first` puts it on the cover and `conclusion-stays-up` on the last main slide, and both
 * layouts place this one component, so the two cannot drift apart. Each value is set once for a
 * deck in `themeConfig` and overridden per slide by a prop of the same name. The code is an image
 * the deck serves from its own `public/`, generated for the deck's own link; until a deck names
 * one, the slot shows a placeholder the theme bundles, and `''` leaves it empty.
 */
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'
import qrPlaceholder from '../assets/placeholders/share-qr.svg?url'
import { assetUrl } from '../utils/assets'

const props = defineProps<{
  /** The QR code's image URL, overriding `themeConfig.shareQr`. */
  shareQr?: string
  /** Where the code leads, written out under it, overriding `themeConfig.shareUrl`. */
  shareUrl?: string
  /** How to reach the presenter, overriding `themeConfig.contact`. The cover passes `''`. */
  contact?: string
}>()

const { $slidev } = useSlideContext()

/**
 * `??` rather than `||`, so an empty string is an answer — no code — and not the placeholder. A
 * path the deck names follows the base the deck is hosted under (`assetUrl`).
 */
const qr = computed(() => assetUrl(props.shareQr ?? $slidev.themeConfigs.shareQr ?? qrPlaceholder))
const url = computed(() => props.shareUrl ?? $slidev.themeConfigs.shareUrl ?? '')
const contact = computed(() => props.contact ?? $slidev.themeConfigs.contact ?? '')

/** The link as a room reads it aloud: no scheme, no trailing slash. */
const shownUrl = computed(() => url.value.replace(/^https?:\/\//, '').replace(/\/$/, ''))
</script>

<template>
  <div v-if="qr || url || contact" class="legible-share">
    <img v-if="qr" class="legible-share-qr" :src="qr" :alt="url ? `QR code to ${url}` : ''" />
    <a v-if="url" class="legible-share-caption" :href="url">{{ shownUrl }}</a>
    <span v-if="contact" class="legible-share-caption">{{ contact }}</span>
  </div>
</template>
