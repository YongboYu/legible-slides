<script setup lang="ts">
/**
 * One citation, inside a `Footnotes` block.
 *
 * The number is the author's to keep: it has to match the marker written in the text above it, and
 * the entry it points at on the references slide.
 */
defineProps<{
  /** The marker this entry answers to. */
  number?: number | string
}>()
</script>

<template>
  <div class="legible-footnote">
    <sup v-if="number" class="legible-footnote-number">{{ number }}</sup>
    <span><slot /></span>
  </div>
</template>
