// The stylesheet entry Slidev pulls in for a theme.
//
// The palette comes first because every rule after it reads one of its custom properties, and
// nothing in this theme states a colour of its own. It is generated — `legible gen-css` writes it
// from the theme file and CI checks the two agree — which is what lets the deck build import a
// stylesheet instead of running the Python toolchain.
import './tokens.css'
import './fonts.css'
import './layout.css'
