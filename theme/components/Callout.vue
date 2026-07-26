<script setup lang="ts">
/**
 * An inline box for the one thing on a slide that has to be read as set apart.
 *
 * Not a second message and not a takeaway strip — the claim is the headline and lives nowhere else
 * (`assertion-headline`). A callout is for the definition the rest of the slide leans on, or the
 * number the evidence turns on.
 */
defineProps<{
  /** A short label above the box's content. */
  title?: string
  /**
   * Mark it as the thing to look at. Accent is the attention role and never a data colour, so it is
   * spent on the box's edge with ink text on top of it (`accent-is-attention`).
   */
  accent?: boolean
}>()
</script>

<template>
  <div class="legible-callout" :class="{ 'legible-callout-accent': accent }">
    <div v-if="title" class="legible-callout-title">{{ title }}</div>
    <slot />
  </div>
</template>
