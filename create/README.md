# create-legible-slides

Starts a Slidev talk built to the [legible-slides](https://github.com/YongboYu/legible-slides)
method, with no clone:

```bash
npm create legible-slides my-talk
cd my-talk
pnpm install && pnpm dev
```

It stamps the starter into `my-talk/`, which has to be new or empty. The starter is one skeleton
slide per layout of the `slidev-theme-legible` theme, a palette that clears the accessibility floor,
and the checks, wired as a pre-commit hook and a CI workflow. The deck is named after its directory.
It pins the theme and the `legible-slides` checks to this package's version. Its own README says
what lives where, and the rules are in
[`docs/method.md`](https://github.com/YongboYu/legible-slides/blob/main/docs/method.md).

From a checkout of legible-slides, `node create/index.js my-talk` stamps the starter in
`skill/template/` instead, so a change to it can be tried before it is released.
