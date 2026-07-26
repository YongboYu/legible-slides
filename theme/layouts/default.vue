<script setup lang="ts">
/**
 * Not a fifth layout: the same one, under the name Slidev falls back to.
 *
 * A slide that names no layout would otherwise get Slidev's built-in default, which has no headline
 * zone and no place for the chrome — the method's structure would become something an author has to
 * remember to ask for. Aliasing it means the skeleton is what you get by default and the deck opts
 * *out* of it, never in.
 */
import AssertionEvidence from './assertion-evidence.vue'
</script>

<template>
  <AssertionEvidence>
    <slot />
  </AssertionEvidence>
</template>
