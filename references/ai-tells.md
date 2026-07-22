# The AI-tells reference

A catalogue of the patterns that make prose read as machine-written, plus fixes. Two things to hold in mind while using it:

1. **No single item here is proof of anything.** Humans use em-dashes. Humans say "crucial." The tell is never one word — it's the *density* and *co-occurrence* of these patterns. A page with three "delve"s, a rule-of-three in every paragraph, and a restate-everything conclusion reads as AI. One em-dash does not.
2. **This is a diagnostic list, not a banned-words filter.** Don't find-and-replace your way through it. If you swap "delve" for "explore" and change nothing else, you still sound like a machine that owns a thesaurus. Fix the underlying habit — reaching for inflated diction, hedging instead of committing, explaining what the reader already knows.

---

## 1. Inflated diction (the "elevation" reflex)

Grand words bolted onto flat subjects. The machine reaches for the fancier synonym by default; a person reaches for the word they'd actually say.

**Verbs/adjectives that signal reaching:** delve, underscore, boasts, showcase, leverage (as a verb), foster, garner, robust, crucial, pivotal, vibrant, meticulous, seamless, comprehensive, nuanced, multifaceted, enhance, bolster, utilize, facilitate, endeavor, myriad, plethora.

**"Tapestry nouns" — abstractions that lend false weight:** tapestry, landscape, realm, mosaic, ecosystem, symphony, labyrinth, beacon, cornerstone, bedrock, testament, kaleidoscope, odyssey.

Fix: use the plain word. *utilize → use. facilitate → help. purchase → buy. endeavored to → tried to. a myriad of → many, or a number.* And when you catch a "tapestry noun," ask what concrete thing it's standing in for and name that instead.

> **Before:** "We endeavored to facilitate a more streamlined utilization of available resources."
> **After:** "We tried to make better use of what we had."

---

## 2. Throat-clearing and connective clichés

Openers and transitions that fill space before the point arrives.

- "It's important to note that…"
- "In today's fast-paced world / digital landscape…"
- "In the ever-evolving landscape of…"
- "When it comes to…"
- "Whether you're X or Y…"
- "plays a crucial / pivotal role in…"
- "stands as a testament to…"
- "It's worth noting that…"
- "This article will explore / discuss…"

Fix: delete the opener and start on the actual sentence. The point is almost always the second sentence — promote it.

> **Before:** "In today's fast-paced digital landscape, email remains a crucial tool that plays a pivotal role in how businesses communicate."
> **After:** "Email is still how most business gets done."

---

## 3. The three signature constructions

These three are weighted heavily by "slop" scorers because they're so distinctive. If you write one, you've likely written the others nearby.

**Rule-of-three triples** — "adjective, adjective, and adjective," "verb, verb, and verb," relentlessly.
> **Before:** "The tool is powerful, intuitive, and versatile, helping teams plan, build, and ship faster."
> **After:** "The tool is fast, and it stays out of your way."

**"Not only… but also" / forced parallelism.**
> **Before:** "The policy not only affected businesses but also influenced everyday citizens."
> **After:** "The policy hit businesses first. Then it trickled down to everyone else."

**The negation pivot — "It's not just X, it's Y" / "It's not X. It's Y."** This one is a signature AI cadence; treat it as almost a hard stop.
> **Before:** "It's not just a notebook. It's a system for thinking."
> **After:** "I use it as a notebook, though it's grown into how I plan my week."

---

## 4. Structural tells

- **Uniform paragraph length** — every paragraph three or four sentences, every section the same shape. Real writing has a one-line paragraph sitting next to a seven-line one.
- **Restate-everything conclusions** — "Despite its challenges, X remains promising, and its importance will only grow." Cut it. End on your last real point, not a summary of the points above.
- **Bulleting prose that should flow** — chopping connected reasoning into bold-header + colon bullets. Lists are for genuinely list-like things (steps, options, specs). If the items depend on each other, write sentences.
- **Over-explaining / closing every point with its significance** — "…highlighting the enduring importance of collaboration." Trust the reader to see why it matters; delete the significance clause.

---

## 5. Punctuation and typography

- **Em-dash overuse** — several per paragraph, standing in for commas, colons, and parentheses all at once. Em-dashes are fine; a cluster of them is the tell. Roughly one per few paragraphs is a safe ceiling.
- **Curly/smart quotes and apostrophes** where a person typing in a plain editor would produce straight ones — a copy-paste-from-chatbot fingerprint. Match whatever the surrounding context uses.
- **Title Case On Every Heading** — humans usually sentence-case ("Impact of technology," not "The Impact Of Technology And Digitalization").
- **Emoji section bullets/headers** (✅ 🚀 💡 🔑) and reflexive **bold** on every key term. Use sparingly and only where the context actually calls for it.

---

## 6. Tonal tells

**Relentless positivity.** Everything is exciting, delightful, vibrant; nothing is merely fine, boring, or bad. Real assessment includes the negative.
> **Before:** "This charming café offers a delightful array of beverages sure to please any palate."
> **After:** "The coffee's good. The pastries are stale by afternoon."

**Hedging / over-qualifying.** "often," "typically," "generally," "can be," "may," "in some cases," stacked so the writer is never wrong and never says anything.
> **Before:** "This can often be a factor that may, in some cases, contribute to slower performance."
> **After:** "This slows things down."

**Corporate neutrality / no stance.** Presenting "both sides," committing to nothing.
> **Before:** "There are various perspectives on remote work, each with its own merits and drawbacks."
> **After:** "Remote work is better for focus and worse for junior people, who learn by osmosis."

**Vague attribution.** "studies show," "experts agree," "researchers say," "many believe" — with no name, number, or date. Either name the source (person, year, figure) or cut the claim.
> **Before:** "Studies have shown that many users find the feature valuable."
> **After:** "In their March 2025 survey, 61% of the 400 respondents said they'd used it that week."

---

## 7. Why detectors "see" all of this (brief)

AI-text detectors measure two things above all: **predictability** (how closely each word matches what a language model would expect — low = machine-like) and **uniformity** (how little the rhythm, sentence length, and vocabulary vary). Every pattern above is a symptom of one or both: inflated-but-safe diction is predictable; uniform paragraphs and relentless parallelism are uniform.

This is why you can't reliably beat a detector by swapping words — and why you shouldn't try to. Detectors are unreliable (they falsely flag non-native English speakers and neurodivergent writers at high rates) and they change constantly; tuning to today's scorer is a moving target. But the traits that genuinely lower predictability and raise variance — real voice, specific detail, varied rhythm, an actual opinion — are the same traits that make writing *good*. Optimize for the writing, and the detector takes care of itself. See SKILL.md for the positive craft that does this.
