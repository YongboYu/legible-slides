<script setup lang="ts">
/**
 * How a process model is forecast: the log counted into a directly-follows graph a day, each
 * arrow's counts read as a time series, and every series forecast into next week's graph.
 *
 * A concept diagram, drawn here because its evidence is a process rather than data: there is no
 * number in it for the figure script to draw from. Every colour and size is a theme token, so a
 * recolour reaches it the way it reaches the charts.
 *
 * Colour never says anything alone in it (`never-sole-channel`). The forecast graph is told apart
 * from the observed one by its dashed arrows and its label, and its colour only repeats them.
 */
defineProps<{
  /** What the diagram shows. Sits under it, at the caption size, like a figure's. */
  caption?: string
  /** A footnote number, as on `Figure`. */
  cite?: number | string
}>()
</script>

<template>
  <figure class="legible-figure pipeline">
    <ol class="pipeline-steps">
      <li class="pipeline-step">
        <svg class="pipeline-glyph" viewBox="0 0 72 48" aria-hidden="true">
          <rect class="pipeline-row" x="4" y="6" width="64" height="8" />
          <rect class="pipeline-row" x="4" y="20" width="64" height="8" />
          <rect class="pipeline-row" x="4" y="34" width="64" height="8" />
        </svg>
        <span>The event log</span>
      </li>
      <li class="pipeline-how">counted each day</li>
      <li class="pipeline-step">
        <svg class="pipeline-glyph" viewBox="0 0 72 48" aria-hidden="true">
          <path class="pipeline-edge" d="M16 12 L56 12 M16 12 L56 36 M56 12 L56 36" />
          <circle class="pipeline-node" cx="12" cy="12" r="6" />
          <circle class="pipeline-node" cx="60" cy="12" r="6" />
          <circle class="pipeline-node" cx="60" cy="36" r="6" />
        </svg>
        <span>A directly-follows graph a day</span>
      </li>
      <li class="pipeline-how">each arrow read across the days</li>
      <li class="pipeline-step">
        <svg class="pipeline-glyph" viewBox="0 0 72 48" aria-hidden="true">
          <polyline class="pipeline-series" points="4,30 14,18 24,26 34,10 44,22 54,16 68,34" />
        </svg>
        <span>A time series per arrow</span>
      </li>
      <li class="pipeline-how">each series forecast a week ahead</li>
      <li class="pipeline-step pipeline-forecast">
        <svg class="pipeline-glyph" viewBox="0 0 72 48" aria-hidden="true">
          <path class="pipeline-edge" d="M16 12 L56 12 M16 12 L56 36 M56 12 L56 36" />
          <circle class="pipeline-node" cx="12" cy="12" r="6" />
          <circle class="pipeline-node" cx="60" cy="12" r="6" />
          <circle class="pipeline-node" cx="60" cy="36" r="6" />
        </svg>
        <span>Next week's graph, forecast</span>
      </li>
    </ol>
    <figcaption v-if="caption">
      {{ caption }}<sup v-if="cite">{{ cite }}</sup>
    </figcaption>
  </figure>
</template>

<style scoped>
.pipeline-steps {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin: 0;
  padding: 0;
  list-style: none;
}

.pipeline-step {
  display: grid;
  grid-template-columns: 72px 1fr;
  align-items: center;
  column-gap: var(--zone-gap);
  color: var(--ink);
  font-size: var(--body-px);
  line-height: 1.3;
}

/* What turns one step into the next. At the floor and in the text neutral: it labels the arrow
 * between two steps, and the steps are what the eye reads. Indented to the steps' text, under the
 * arrow it draws, so the column of glyphs stays a column. */
.pipeline-how {
  margin-left: calc(72px + var(--zone-gap));
  color: var(--neutral);
  font-size: var(--floor-px);
}

.pipeline-how::before {
  content: '↓ ';
}

.pipeline-glyph {
  width: 72px;
  height: 48px;
}

.pipeline-row {
  fill: var(--neutral-soft);
}

.pipeline-edge,
.pipeline-series {
  fill: none;
  stroke: var(--brand);
  stroke-width: 3;
  stroke-linecap: round;
  stroke-linejoin: round;
}

.pipeline-node {
  fill: var(--surface);
  stroke: var(--brand);
  stroke-width: 3;
}

/* The forecast: dashed arrows, and labelled as one. The colour repeats what the dash and the words
 * say. Its steps are as solid as the observed graph's: what is forecast is the arrows' counts. */
.pipeline-forecast .pipeline-edge,
.pipeline-forecast .pipeline-node {
  stroke: var(--brand-strong);
}

.pipeline-forecast .pipeline-edge {
  stroke-dasharray: 6 5;
}
</style>
