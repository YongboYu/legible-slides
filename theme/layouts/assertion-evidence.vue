<script setup lang="ts">
/**
 * The default: an assertion headline and the one piece of evidence that proves it.
 *
 * There is nothing to configure, which is the design. The headline is the slide's `#`, everything
 * after it is the evidence, and the zones around them belong to the chrome — a slide's only
 * decision is what it is trying to land (`one-message`).
 */
</script>

<template>
  <div class="slidev-layout assertion-evidence">
    <slot />
  </div>
</template>
