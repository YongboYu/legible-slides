// This deck's stylesheet entry, which Slidev loads after the theme's own.
//
// `tokens.css` is generated from themes/palette.json by `legible gen-css` and committed like a
// lockfile, so building this deck never runs Python. It lands after the theme's tokens and wins on
// order, which is what makes these colours the deck's rather than whichever palette the theme
// checkout happens to be wearing.
//
// Add your own stylesheets here. Keep the tokens import first: every rule you write should read a
// custom property from it rather than state a colour of its own, so recolouring stays one edit to
// the palette and one `legible gen-css` run.
import './tokens.css'
