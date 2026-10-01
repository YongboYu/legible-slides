<script setup lang="ts">
/**
 * The persistent half of `ae-skeleton`: the footer, with the section locator bottom left and the
 * page number opposite it.
 *
 * It is injected once by `slide-top.vue` rather than placed by each layout, so a content slide
 * cannot be built without it and a deck cannot drift into carrying it on some slides only. The
 * locator is what pays for `no-section-dividers` — orientation is on every slide, so no slide has
 * to be spent announcing where the talk has got to. What it shows is `section-locator`'s: the map
 * of every section by default, or the current one with its position when the deck sets
 * `themeConfig.locator: label`.
 */
import { computed } from 'vue'
import { useSlideContext } from '@slidev/client'

const { $slidev, $frontmatter, $page } = useSlideContext()

/** The one layout that carries no chrome: a cover is where orientation starts. */
const CHROME_FREE_LAYOUT = 'cover'

/**
 * Which layout this slide is on — resolved the way Slidev resolves it, not merely read.
 *
 * A slide that names no layout still has one: the deck's `defaults`, or `cover` on the first slide
 * and `assertion-evidence` after it. Reading the frontmatter alone would miss the common case,
 * which is a cover that never had to say it was one.
 */
const layout = computed(
  () =>
    $frontmatter.layout ??
    $slidev.configs.defaults?.layout ??
    ($page.value === 1 ? CHROME_FREE_LAYOUT : 'default'),
)

const shown = computed(
  () => $frontmatter.chrome !== false && layout.value !== CHROME_FREE_LAYOUT,
)

/** The map, unless the deck asks for the single label with a count. */
const style = computed(() => ($slidev.themeConfigs.locator === 'label' ? 'label' : 'map'))

/** One slide's frontmatter, by number. Slidev keeps it on the slide's route. */
function frontmatterOf(no: number) {
  return $slidev.nav.slides[no - 1]?.meta?.slide?.frontmatter ?? {}
}

interface Section {
  name: string
  /** Held for questions after the talk: outside the map and the count. */
  backup: boolean
}

/**
 * The section a slide is in: the one it declares, or the last one a slide before it declared.
 *
 * Carrying forward is the point: a run of slides on one part of the argument is one section, and
 * making each of them restate its name is the kind of repetition that ends in two of them
 * disagreeing. `section: ''` clears it. Whether a section is a backup is said once, where the
 * section is declared, and travels with it.
 */
function sectionAt(no: number, own = frontmatterOf(no)): Section | undefined {
  for (let at = no; at >= 1; at--) {
    const declaring = at === no ? own : frontmatterOf(at)
    if (declaring.section === undefined) continue
    return declaring.section ? { name: declaring.section, backup: declaring.backup === true } : undefined
  }
  return undefined
}

/** This slide's section. Its own frontmatter comes from the slide context, which is live. */
const current = computed(() => sectionAt($page.value, $frontmatter))

/** The talk's sections, in the order the deck first declares them. Backups are not among them. */
const sections = computed(() => {
  const names: string[] = []
  for (let no = 1; no <= $slidev.nav.total; no++) {
    const { section, backup } = frontmatterOf(no)
    if (section && backup !== true && !names.includes(section)) names.push(section)
  }
  return names
})

const position = computed(() => (current.value ? sections.value.indexOf(current.value.name) + 1 : 0))
</script>

<template>
  <div v-if="shown" class="legible-chrome">
    <div v-if="current" class="legible-locator">
      <span v-if="current.backup" class="legible-section-label">{{ current.name }}</span>
      <span v-else-if="style === 'label'" class="legible-section-label">
        {{ current.name }}<span class="legible-section-count"> · {{ position }}/{{ sections.length }}</span>
      </span>
      <span v-else class="legible-section-map">
        <template v-for="(name, index) of sections" :key="name">
          <span v-if="index > 0" class="legible-section-separator">·</span>
          <span :class="{ 'legible-section-current': name === current.name }">{{ name }}</span>
        </template>
      </span>
    </div>
    <div class="legible-page">{{ $page }} / {{ $slidev.nav.total }}</div>
  </div>
</template>
