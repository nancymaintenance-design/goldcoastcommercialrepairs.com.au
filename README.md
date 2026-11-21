# Ellis Gold Coast — Surf Poster V2 + Finale V3

Bilingual commercial property maintenance website for the Gold Coast. Updated on **21 November 2026**.

## Current design decision

**V2 replaces V1.** The user rejected the quiet resort-magazine treatment and requested strong design, extensive animation and a distinctly Gold Coast identity. Continue from **Australian surf posters × beach clubs × tropical summer campaigns**.

The Melbourne website remains a content-structure reference. Its electric-blue, fluorescent-green and architectural-technology visual language must not be reproduced. Do not restore V1's restrained split hero, pale editorial styling or serif-italic display treatment when reusing the base stylesheet.

`DESIGN.md` records the design direction. The canonical runtime colour tokens are in `dist/maximal.css`; `dist/interiors.css` uses the same tokens for internal pages.

## Current scope: V3 shared finale

The user approved the homepage H1 and requested a stronger page ending. **Keep `src/home_v2.py`, the H1/hero composition and motion, `dist/assets/coast-hero.webp`, and `src/assets/coast-hero-original.png` unchanged.** V2 body sections and content remain in place.

V3 replaces the closing enquiry card and shared dark footer with a pool-aqua beach service desk: **BIG PLANS. / SMALL FIXES. / LET’S TALK.** A surfboard-shaped hospitality photograph, striped board and rotating contact ring support the headline; the ring's central label stays upright. Chinese reads **大到项目，/ 小到维修，/ 我们来安排。** The pink footer has six navigation signs, an oversized ELLIS wordmark, the existing preview notice and image credits.

`src/footer_v3.py` renders the two shared components through the existing `build.py` wrappers. `dist/footer.css` owns their styles and is loaded last. V3 reuses the existing reveal, tide, magnetic and tilt interfaces; it adds no enquiry delivery or separate scroll controller. Mobile layouts stack the enquiry scene and keep six footer links in two readable columns. Pause and reduced-motion support remain requirements.

**V3 scoped browser QA completed on 21 November 2026.** English/Chinese desktop and mobile finales were inspected; mobile content width remained 380px without overflow. Chinese footer and circular Contact actions reached the form. Pause stopped the ring and preserved readable text; resume worked. Shared Chinese inner-page CTA/footer views were inspected. All 672 footer/CTA links resolve and duplicate IDs are absent. Reduced-motion CSS was reviewed, without emulating an OS preference switch. The current local Noto Sans SC subset has 676 characters, is 196,788 bytes and retains weights 100–900; Chinese text in all 69 deliverable pages is covered. The V2 checks below are historical evidence, not proof of complete V3 acceptance. The scoped continuation prompt is in `docs/FOOTER_V3_PROMPT.md`.

## Visual system

| Role | V2 value |
| --- | --- |
| Warm dark ink | `#241611` |
| Sunset orange | `#FF642D` |
| Coral pink | `#FF90BF` |
| Pool aqua | `#33E1D3` |
| Sunshine yellow | `#FFE34D` |
| Reading paper | `#FFF8E8` |
| English display | Local **Bowlby One SC**, exposed as **`Surf Display`** in CSS |
| Body | Local DM Sans; Chinese uses a local Noto Sans SC variable subset with dedicated sizing |

The homepage uses a full-bleed coastal scene, oversized poster lettering, adult holidaymakers, pool and striped-umbrella atmosphere, dark outlines, hard offset shadows, overlapping photo posters, wave edges and crossing moving ribbons. Internal pages use the same visual system: poster-like service rows, an uneven property-photo collection, a large news cover story, a bold FAQ search panel and a colourful enquiry desk.

## Content and working features

- Seven primary navigation areas remain unchanged: **Home, Services, Property types, News, FAQ, About us, Contact**.
- Twelve services, eight property types, six articles and ten main FAQs, in Australian English and Simplified Chinese.
- Service and news filters, FAQ search and disclosure, native horizontal galleries, mobile navigation and a local enquiry draft flow.
- At desktop widths **≥1024px**, the property gallery can progress horizontally with ordinary document scrolling. Smaller screens retain a swipeable track and previous/next buttons.
- Motion includes hero/title parallax, wave progression, moving ribbons, parasol rotation, photo focus, pointer tilt and magnetic CTA feedback. An always-available motion control pauses the effects.

## Build and preview

Python 3 generates the static HTML. No frontend package installation is required.

```sh
python3 build.py
```

In the managed Sites environment, use the supported `sites-preview` workflow. For an ordinary local checkout outside that environment:

```sh
python3 -m http.server 8000 --directory dist
```

The generator updates HTML, the preview robots file and favicon. It does not regenerate CSS, JavaScript or image/font assets.

## Source layout

| File | Responsibility |
| --- | --- |
| `DESIGN.md` | V2 design baseline, V3 finale decisions and locked hero scope |
| `src/content.json` | Editable bilingual service, property, article and FAQ content |
| `src/home_v2.py` | V2 surf-poster homepage composition, used by `build.py` |
| `src/footer_v3.py` | Shared V3 enquiry finale and footer; called by existing generator wrappers |
| `build.py` | Shared navigation, internal-page templates, metadata and route generation |
| `dist/style.css` | Existing layout and component foundation; V2 overrides remain required |
| `dist/maximal.css` | Canonical V2 tokens, global theme, homepage and shared motion styling |
| `dist/interiors.css` | V2 internal-page layouts and responsive overrides |
| `dist/footer.css` | V3 finale layout, contact-ring motion and responsive overrides |
| `dist/fonts.css` | Existing local body/base font declarations |
| `dist/surf-font.css`、`dist/chinese-font.css` | Local Bowlby One SC and Noto Sans SC declarations |
| `dist/app.js` | Existing navigation, filters, search, carousels and enquiry drafts |
| `dist/motion.js` | V2 scroll/pointer progress controller and motion preferences |
| `dist/assets/` | Local imagery, fonts and favicon |
| `src/assets-sources.json`, `src/font-sources.json` | Asset provenance |
| `docs/FOOTER_V3_PROMPT.md` | Chinese continuation prompt limited to the V3 finale |

Keep the current stylesheet order: `style.css` → `surf-font.css` → `chinese-font.css` → `maximal.css` → `interiors.css` → `footer.css`. Load `app.js` before `motion.js`, both deferred. The existing motion controller operates on pages with the `maximal` body class.

## Motion contract

CSS owns colour and transforms. `motion.js` writes `--page-progress`, `--hero-progress`, `--tide-progress`, `--parallax`, `--card-focus`, `--tilt-x/y` and `--magnet-x/y`. Only the decorative cursor orb's position is set directly. Pointer effects require a fine pointer and a desktop viewport; tilt is limited to 6 degrees and magnetic displacement to 5px.

The controller uses dirty-flagged animation frames and one scroll/resize listener. It does not block native scrolling. System reduced-motion takes priority over user activation; explicit pause shows all reveal content, stops ongoing effects and returns pinned sections to normal flow. The sole saved preference is a motion-paused boolean. No personal information is stored by this controller.

Desktop pin tracks need `scroll-snap-type: none` and `scroll-behavior: auto`; mobile and paused layouts retain normal gallery interaction. Keep the motion control, keyboard focus, visible labels and native pointer usable while refining effects.

## Preview boundary and evidence

This remains a design preview. Pages deliberately contain `noindex`, and `robots.txt` disallows crawling. The form generates, copies and downloads an enquiry draft locally. It does not send an enquiry or upload selected photos; the text download includes photo filenames only.

Gold Coast contact details, operating arrangements, a public domain and a real enquiry destination still require confirmed company information. Do not copy Melbourne's city-specific contacts. The generated hero and attributed stock property photographs are illustrative, not records of completed Ellis projects.

The live content structure of https://www.melbournecommercialrepairs.com.au/ was inspected on 20 November 2026. Its latest twelve service categories were retained. The original generated hero is retained at `src/assets/coast-hero-original.png`; imagery attribution is recorded in `src/assets-sources.json` and the image-credits pages.

## Validation status

**V3 status:** scoped implementation and browser verification are complete as recorded above. The historical checks below refer to V2.

- **V2 static checks passed:** 69 HTML files, consisting of 34 routes per language plus a 404 page; unique H1s, preview noindex, internal links, static resources, language alternates and anchors checked.
- **JavaScript syntax checks:** the interaction and motion scripts have passed `node --check` during implementation.
- **Retained foundation records, before the V2 restyle:** desktop presentation; English/Chinese mobile layout in a 390px frame with a 375px content viewport; mobile menu opening and Escape close; service filtering; FAQ search and disclosure; local enquiry draft generation.
- **V2 browser validation completed for the representative views and interactions recorded below.** This does not claim an exhaustive device or operating-system matrix.
- Actual enquiry dispatch and public search indexing are not enabled or tested.

See `CODEX_HANDOFF.md` for the current continuation prompt and remaining launch inputs.


## V2 recorded verification — before Finale V3 / V3前验证记录

- 69 deliverable HTML pages; 1,970 internal links and 256 local source references resolved. All normal pages retain seven navigation items and 34 EN/ZH route pairs.
- Desktop browser: new full-bleed hero, poster service index, scroll-linked property collection (observed track advance to 786 px with sticky top at 82 px), Chinese FAQ layout, and no horizontal page overflow.
- Mobile browser: English and Chinese homepages, service and contact layouts at a 380 px content viewport; page width matched the viewport. Chinese hero title stayed within the frame after Noto Sans SC loaded.
- Mobile menu exposed all seven links and closed with Escape. Motion pause set motion-paused and stopped the sun animation. Service Systems filter showed 4 of 12 entries; Chinese FAQ search for 海盐 showed 1 of 10 entries.
- Local Noto Sans SC supplied the Chinese glyphs during V2. Current V3 subset size and coverage are recorded above; the font source manifest retains the official source.
- Python generation, node --check for both JavaScript files, git diff --check, and frontend project strict audit passed (0 findings).
- Persistent corner motion control remains reachable while scrolling. Contact remains a browser-local draft, with no actual delivery.
