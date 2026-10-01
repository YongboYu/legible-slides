<script setup lang="ts">
/**
 * The talk's answer, straight after the cover (`answer-first`): the result as the headline, and the
 * research questions the talk answers, numbered.
 *
 * The headline and anything that backs the result up are the slide's markdown, as on every content
 * slide; the questions follow `::questions::` as an ordered list. They are numbered Q1, Q2, … so
 * the `conclusion` layout can answer them by the same numbers.
 */
</script>

<template>
  <div class="slidev-layout answer">
    <slot />
    <div class="legible-numbered legible-evidence">
      <slot name="questions" />
    </div>
  </div>
</template>
