<script setup lang="ts">
import { resolveAssetUrl } from '@slidev/client/layoutHelper.ts'

/**
 * An image, its caption and its citation, kept together as one thing.
 *
 * As data rather than as three pieces of markup, because the three drift apart otherwise: a figure
 * gets swapped and its caption still describes the old one. The image itself is expected to be
 * regenerated rather than redrawn — `legible.figures` draws the archetypes the method prescribes
 * from the same palette this theme is coloured from.
 */
defineProps<{
  /** The image URL, served by the deck. A path from its root follows the base the deck is under. */
  src: string
  /** What the figure shows. Sits under the image, at the caption size. */
  caption?: string
  /**
   * A footnote number, matching a `Footnote` on this slide and an entry on the references slide.
   * Numbered by hand, which is the whole citation mechanism (`Footnotes`).
   */
  cite?: number | string
  /**
   * The image's text alternative. Defaults to the caption; set it to `''` for a figure the caption
   * already describes in full.
   */
  alt?: string
}>()
</script>

<template>
  <figure class="legible-figure">
    <img :src="resolveAssetUrl(src)" :alt="alt ?? caption ?? ''" />
    <figcaption v-if="caption">
      {{ caption }}<sup v-if="cite">{{ cite }}</sup>
    </figcaption>
  </figure>
</template>
