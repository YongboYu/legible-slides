<script setup lang="ts">
/**
 * The sources, from data.
 *
 * Numbered, so a `Footnote` marker earlier in the deck lines up with an entry here. The entries are
 * frontmatter rather than markdown because that is what they are — a list of records, each a title
 * and where to find it — and because a deck that writes them as prose ends up numbering them by
 * hand. The prop keeps the name the academic theme's `index` layout gave it, since this is that
 * layout narrowed to one job.
 *
 * It is a slide about sources, not a divider: it proves something — where the claims came from —
 * which is why the method can ship it while refusing `section` (`no-section-dividers`).
 */
interface IndexEntry {
  /** How the source is cited: author, year, title — whatever the field expects. */
  title: string
  /** Where to find it. Optional, because a book has no URL. */
  uri?: string
}

withDefaults(defineProps<{ indexEntries?: IndexEntry[] }>(), { indexEntries: () => [] })
</script>

<template>
  <div class="slidev-layout references">
    <slot />
    <div class="legible-evidence">
      <ol class="legible-references">
        <li v-for="entry of indexEntries" :key="entry.title" class="legible-reference">
          <span>
            {{ entry.title }}
            <a v-if="entry.uri" class="legible-reference-uri" :href="entry.uri">{{ entry.uri }}</a>
          </span>
        </li>
      </ol>
    </div>
  </div>
</template>
