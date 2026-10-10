---
# Not a talk: a fixture for check-hosted-images.mjs, which the flagship cannot be. The flagship's
# figures come from its public/, as an author's are meant to; this one is an image a deck imports,
# which Vite has already resolved against the base by the time the theme sees it. The figure is the
# flagship's own, imported from outside this fixture's public folder.
theme: ../../theme
title: An imported figure under a base path
layout: default
---

# An image the deck imports loads where the deck is hosted.

<script setup>
import chart from '../public/colour-alone.png'
</script>

<Figure :src="chart" caption="Passed to the figure as Vite resolved it." />

<Share :share-qr="chart" share-url="https://github.com/YongboYu/legible-slides" />
