<script setup lang="ts">
/**
 * The persistent half of `ae-skeleton`: the locator pill, the accent rule and the page number.
 *
 * It is injected once by `slide-top.vue` rather than placed by each layout, so a content slide
 * cannot be built without it and a deck cannot drift into carrying it on some slides only. The
 * locator is what pays for `no-section-dividers` — orientation is on every slide, so no slide has
 * to be spent announcing where the talk has got to.
 */
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'

const { $slidev, $frontmatter, $page } = useSlideContext()

/**
 * Layouts that carry no chrome. The cover is where orientation starts, so there is nothing for a
 * locator to remind anyone of, and a page number on a title slide counts a slide nobody is
 * counting.
 */
const CHROME_FREE_LAYOUTS = ['cover']

/**
 * Which layout this slide is on — resolved the way Slidev resolves it, not merely read.
 *
 * A slide that names no layout still has one: the deck's `defaults`, or `cover` on the first slide
 * and `assertion-evidence` after it. Reading the frontmatter alone would miss the common case,
 * which is a cover that never had to say it was one.
 */
const layout = computed(
  () =>
    $frontmatter.layout ??
    $slidev.configs.defaults?.layout ??
    ($page.value === 1 ? 'cover' : 'default'),
)

const shown = computed(
  () => $frontmatter.chrome !== false && !CHROME_FREE_LAYOUTS.includes(layout.value),
)

/**
 * This slide's locator, or the last one a slide before it set.
 *
 * Carrying forward is the point: a run of slides on one part of the argument is one section, and
 * making each of them restate its name is the kind of repetition that ends in two of them
 * disagreeing. A slide sets `locator` when the section changes, and `locator: ''` clears it.
 */
const locator = computed(() => {
  if ($frontmatter.locator !== undefined) return $frontmatter.locator
  for (let no = $page.value - 1; no >= 1; no--) {
    const declared = $slidev.nav.slides[no - 1]?.meta?.slide?.frontmatter?.locator
    if (declared !== undefined) return declared
  }
  return undefined
})
</script>

<template>
  <div v-if="shown" class="legible-chrome">
    <div v-if="locator" class="legible-locator">{{ locator }}</div>
    <div class="legible-rule" />
    <div class="legible-page">{{ $page }} / {{ $slidev.nav.total }}</div>
  </div>
</template>
