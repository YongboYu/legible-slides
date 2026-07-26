<script setup lang="ts">
/**
 * Where the chrome is injected: once, for every slide, above the slide's own content.
 *
 * A per-slide layer rather than a global one, and that is a deliberate correction to the pattern
 * this borrows from. A global layer is mounted once outside the slide, so its px are the viewport's
 * and its chrome neither scales with the canvas the type scale is written against nor lands on an
 * exported page. This layer is mounted inside each slide's own box, which is what makes the
 * chrome's px the same px as the deck's.
 */
import Chrome from './components/Chrome.vue'
</script>

<template>
  <Chrome />
</template>
