<script setup lang="ts">
/**
 * One claim, evidence in two panes: a figure beside what it shows, a label beside a claim, a before
 * beside an after.
 *
 * Still one message — the two panes are one argument, and a slide whose panes answer two questions
 * is two slides (`one-message`). Content before `::left::` is the headline.
 */
const props = withDefaults(
  defineProps<{
    /**
     * The two panes' widths, as CSS grid columns. Equal by default; `3fr 2fr` gives the evidence
     * the wider half. A ratio, not a free-form layout: the panes stay on the grid
     * (`layout-discipline`).
     */
    ratio?: string
  }>(),
  { ratio: '1fr 1fr' },
)
</script>

<template>
  <div class="slidev-layout two-col-evidence">
    <slot />
    <div class="legible-evidence" :style="{ gridTemplateColumns: props.ratio }">
      <div class="legible-column">
        <slot name="left" />
      </div>
      <div class="legible-column">
        <slot name="right" />
      </div>
    </div>
  </div>
</template>
