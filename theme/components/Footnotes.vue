<script setup lang="ts">
/**
 * The foot of the evidence pane, where the slide's citations sit.
 *
 * Manual numbering rather than a citation engine: a talk cites a handful of sources, and a whole
 * BibTeX toolchain would be a large dependency bought for a small job. Write the marker in the text
 * yourself — `<sup>1</sup>` — and give the matching `Footnote` the same number.
 */
withDefaults(
  defineProps<{
    /** A hairline above the block. Drop it where the evidence already ends in a rule. */
    separator?: boolean
  }>(),
  { separator: true },
)
</script>

<template>
  <div class="legible-footnotes" :class="{ 'legible-footnotes-separated': separator }">
    <slot />
  </div>
</template>
