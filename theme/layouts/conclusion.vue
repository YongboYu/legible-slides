<script setup lang="ts">
/**
 * The close, which stays up through Q&A (`conclusion-stays-up`): the talk's claim as the headline,
 * each research question answered by its number, and the slides handed over beside them.
 *
 * The answers follow `::answers::` as an ordered list, numbered Q1, Q2, … like the questions on the
 * `answer` slide, so the room reads each one against the question it closes. The QR code, its link
 * and the presenter's contact come from `themeConfig` and can be set per slide with the same names.
 * It is the method's answer to the "thank you" slide: there is no layout for one.
 */
import Share from '../components/Share.vue'

defineProps<{
  /** The QR code's image URL, overriding `themeConfig.shareQr`. */
  shareQr?: string
  /** Where the code leads, overriding `themeConfig.shareUrl`. */
  shareUrl?: string
  /** How to reach the presenter, overriding `themeConfig.contact`. */
  contact?: string
}>()
</script>

<template>
  <div class="slidev-layout conclusion">
    <slot />
    <div class="legible-evidence">
      <div class="legible-column legible-numbered">
        <slot name="answers" />
      </div>
      <Share :share-qr="shareQr" :share-url="shareUrl" :contact="contact" />
    </div>
  </div>
</template>
