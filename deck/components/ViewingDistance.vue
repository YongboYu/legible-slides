<script setup lang="ts">
/**
 * How far body type reads, drawn side on: the screen one image height tall, the floor marked off in
 * image heights, and the back row where the body size stops reading.
 *
 * A concept diagram rather than a chart: there is no data behind it, only the sizing rule the
 * canon's `type-scale` states. Every colour and size is a theme token, so a recolour or a retuned
 * type scale reaches it the way it reaches the rest of the deck. The SVG is drawn at the width it
 * lands, so its user units are canvas px and its labels sit at the floor where they are seen.
 */
defineProps<{
  /** Where the back row sits, in image heights. Written by the slide, from the canon's figure. */
  reach: number | string
  /** What the diagram shows. Sits under it, at the caption size, like a figure's. */
  caption?: string
}>()

const ticks = [1, 2, 3, 4]
</script>

<template>
  <figure class="legible-figure viewing">
    <svg class="viewing-svg" width="500" height="290" viewBox="0 0 500 290" role="img"
      aria-label="A screen one image height tall, and a viewer at the back row, further away">
      <line class="viewing-floor" x1="16" y1="230" x2="496" y2="230" />
      <rect class="viewing-screen" x="24" y="130" width="12" height="100" />
      <text class="viewing-label" x="24" y="116">1 image height</text>
      <line class="viewing-sight" x1="36" y1="130" x2="474" y2="168" />
      <line class="viewing-sight" x1="36" y1="230" x2="474" y2="168" />
      <g v-for="tick in ticks" :key="tick">
        <line class="viewing-tick" :x1="30 + tick * 100" y1="224" :x2="30 + tick * 100" y2="236" />
        <text class="viewing-label" :x="30 + tick * 100" y="260" text-anchor="middle">{{ tick }}</text>
      </g>
      <circle class="viewing-person" cx="480" cy="168" r="9" />
      <path class="viewing-person-line" d="M480 177 L480 208 M480 208 L470 230 M480 208 L490 230" />
      <text class="viewing-label viewing-back" x="496" y="146" text-anchor="end">back row</text>
      <text class="viewing-label" x="480" y="260" text-anchor="middle">{{ reach }}</text>
      <text class="viewing-label" x="256" y="286" text-anchor="middle">distance, in image heights</text>
    </svg>
    <figcaption v-if="caption" class="legible-figure-caption">{{ caption }}</figcaption>
  </figure>
</template>

<style scoped>
.viewing-svg {
  display: block;
  overflow: visible;
}

.viewing-floor,
.viewing-tick {
  stroke: var(--neutral-soft);
  stroke-width: 2;
}

.viewing-screen {
  fill: var(--brand);
}

/* The two edges of the screen as the back row sees them: what the room has to resolve. Dashed, so
 * they read as sight lines rather than as anything standing in the room. */
.viewing-sight {
  stroke: var(--neutral);
  stroke-width: 1.5;
  stroke-dasharray: 6 5;
}

.viewing-person {
  fill: var(--ink);
}

.viewing-person-line {
  fill: none;
  stroke: var(--ink);
  stroke-width: 3;
  stroke-linecap: round;
}

.viewing-label {
  fill: var(--neutral);
  font-size: var(--floor-px);
  font-variant-numeric: tabular-nums;
}

.viewing-back {
  fill: var(--ink);
}
</style>
