<script setup lang="ts">
/**
 * The title slide, and the only slide with no chrome.
 *
 * Title and subtitle are the markdown's `#` and `##`, so the deck writes them where it writes
 * everything else. What is left is the metadata a talk carries — who is speaking, where, and when —
 * which is data rather than prose and arrives as frontmatter.
 *
 * The logo reaches the slide as a URL the deck serves: a mark belongs to the deck, not to the
 * machinery, and this project ships none. `themeConfig.logo` sets it once for a deck; a slide may
 * override it.
 */
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'

const props = defineProps<{
  /**
   * Who is speaking. Defaults to the deck's own `author`, which is where Slidev already keeps it —
   * and `speaker` rather than `author` because Slidev reserves that word: on the first slide of a
   * deck, which is where a cover normally lives, it belongs to the headmatter and never reaches a
   * layout as a prop.
   */
  speaker?: string
  /** Where: the conference, the seminar, the course. */
  venue?: string
  /** When, written however the deck wants it read. */
  date?: string
  /** A logo URL, overriding `themeConfig.logo` for this slide. */
  logo?: string
}>()

const { $slidev } = useSlideContext()

const logo = computed(() => props.logo || $slidev.themeConfigs.logo || '')
const meta = computed(() =>
  [props.speaker || $slidev.configs.author, props.venue, props.date].filter(Boolean),
)
</script>

<template>
  <div class="slidev-layout cover">
    <img v-if="logo" class="legible-cover-logo" :src="logo" alt="" />
    <slot />
    <div class="legible-cover-rule" />
    <div v-if="meta.length" class="legible-cover-meta">
      <span v-for="line of meta" :key="line">{{ line }}</span>
    </div>
  </div>
</template>
