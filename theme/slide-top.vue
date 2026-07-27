<script setup lang="ts">
/**
 * Where the chrome is injected: once, for every slide, above the slide's own content.
 *
 * A per-slide layer rather than the global one this pattern was borrowed from, because the chrome is
 * per-slide. Slidev provides a slide's frontmatter and its number from `SlideWrapper`, which wraps
 * the slide and nothing else; a global layer is mounted outside every slide and can therefore only
 * ask where the deck currently *is*. That is a different question, and the wrong one wherever more
 * than one slide is on screen — the overview, and a printed export. The opt-out and the carried
 * locator are properties of this slide, so they have to be read where this slide is.
 */
import Chrome from './components/Chrome.vue'
</script>

<template>
  <Chrome />
</template>
