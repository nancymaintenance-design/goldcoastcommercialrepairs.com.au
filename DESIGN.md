---
version: alpha
colors:
  ink: "#241611"
  orange: "#FF642D"
  pink: "#FF90BF"
  aqua: "#33E1D3"
  sun: "#FFE34D"
  paper: "#FFF8E8"
typography:
  display:
    fontFamily: "Surf Display, Noto Sans SC, Manrope, PingFang SC, Microsoft YaHei, sans-serif"
  body:
    fontFamily: "DM Sans, Noto Sans SC, PingFang SC, Microsoft YaHei, sans-serif"
rounded:
  poster: "0px"
  button: "999px"
spacing:
  section: "96px"
  mobileSection: "64px"
components:
  hero:
    kind: "Full-bleed beach photograph and oversized surf-poster type"
  gallery:
    kind: "Native horizontal photo collection with optional scroll-linked progression"
  finale:
    kind: "V3 pool-aqua service desk, surfboard photo, contact ring and pink signpost footer"
---

## Overview

Brand and content website for Ellis commercial property maintenance on the Gold Coast. On 20 November 2026 the user explicitly rejected the quiet resort-editorial V1 and asked for strong visual conflict and extensive animation. The user then clarified that the result must not resemble the Melbourne commercial maintenance site. This decision supersedes the V1 palette and typography in CODEX_HANDOFF.md.

The V2 direction is **Australian surf posters, beach clubs, striped umbrellas and tropical summer campaigns**. Sunshine, surf and hospitality photographs connect the visuals to actual commercial spaces. Full-bleed images, chunky poster typography, crossed moving ribbons, wave boundaries and offset photo posters establish the distinctive identity.

## V3 shared finale — 21 November 2026

The user approved the homepage H1 and requested a stronger ending. **V2 remains the main-page baseline; V3 changes only the closing enquiry section and shared footer.** Keep `src/home_v2.py`, the approved H1, hero composition, crop and motion, `dist/assets/coast-hero.webp`, and `src/assets/coast-hero-original.png` unchanged. Existing body sections, navigation and business content remain outside this change.

The finale is a **Gold Coast beach service desk**. A pool-aqua enquiry section carries three oversized lines: **BIG PLANS. / SMALL FIXES. / LET’S TALK.** Chinese reads **大到项目，/ 小到维修，/ 我们来安排。** A tall surfboard-shaped hospitality photograph and striped board sit beside the headline. The contact ring rotates around a stable central label; both it and the plain-text enquiry link lead to the matching-language contact page. The scene is illustrative property imagery, not a completed-project claim.

A warm-yellow and pink wave joins the enquiry section to the pink footer. Six clearly labelled navigation signs sit above one oversized **ELLIS** wordmark, followed by the preview notice, image credits and a striped hem. This replaces the previous closing card and dark three-column footer; do not add those old blocks back below the new composition.

Implementation lives in `src/footer_v3.py` and `dist/footer.css`. `build.py` delegates its existing `cta()` and `footer()` functions to the new module, so the approved homepage source stays locked. Load `footer.css` after `interiors.css`. Keep V3 selectors scoped to the new `coast-outro` and `shore-footer` components.

V3 reuses `data-reveal`, `data-tide`, `data-magnetic`, `data-tilt` and the existing motion-state classes. No additional scroll controller is required. At mobile widths, stack the enquiry composition and use two columns of stable navigation signs. Check English and Chinese headline wrapping, central-label readability, link focus, photo overlap and footer clearance. System reduced motion and explicit pause must show all content and stop continuous movement; background-tab behaviour remains integrated with the existing controller.

**V3 scoped browser QA completed on 21 November 2026.** English and Chinese desktop finales and both mobile footer views were inspected, with no horizontal overflow at a 380px mobile content viewport. The Chinese footer Contact link and circular enquiry link reached the contact form. The motion toggle stopped the rotating ring and kept all CTA words visible; motion was restored. A Chinese services-page CTA and contact-page footer were also inspected. Reduced-motion CSS was reviewed statically; OS-level reduced-motion switching was not emulated. All 672 footer/CTA links across 69 deliverable pages resolve, and duplicate IDs are absent. The current local Chinese font subset is 196,788 bytes, covers 676 characters at weights 100–900, and covers the Chinese text in all 69 deliverable HTML pages. V2 verification records describe the earlier version and must not be presented as complete V3 acceptance evidence. No live enquiry delivery is introduced by this visual change.

## Colors

Orange, hot coral pink, pool aqua and sunlight yellow carry the identity. Ink is a warm dark brown, not an industrial navy. Paper is only a reading surface. Do not use electric-blue engineering backgrounds or lime-green technical accent systems from the Melbourne reference.

Runtime canonical values live in `dist/maximal.css` as `--gc-ink`, `--gc-orange`, `--gc-pink`, `--gc-aqua`, `--gc-sun`, and `--gc-paper`. Legacy tokens are mapped there to those same values; `dist/interiors.css` consumes the shared variables. This document records the same normative values, not a second generation pipeline.

## Typography

English display is local Bowlby One SC, exposed as `Surf Display` in `dist/surf-font.css`. Body text uses local DM Sans. Chinese uses a local variable Noto Sans SC subset (100–900, 676 required Chinese characters) with separate display sizes and line heights. Titles can be very large but must remain within the viewport. Required business terms remain in visible HTML. Avoid the V1 serif-italic resort treatment.

## Layout

Seven navigation categories and all content routes remain. The hero is a full photographic scene with overlaid poster type, not a split cream/image card. Page sections alternate sun yellow, warm ink, coral pink, pool aqua and orange. Photos are laid out as poster collections and coastal film strips.

Desktop >=1024 supports a sticky horizontal property collection driven by ordinary document scroll. At narrower sizes it is an ordinary swipeable gallery with explicit previous/next controls. Navigation remains accessible during animations.

## Elevation & Depth

Use dark outlines, hard coloured offset shadows, tilted printed-paper surfaces and photo overlap. Pointer tilt is limited to 6 degrees. Avoid soft dashboard cards, glassmorphism and architectural exploded 3D models.

## Shapes

Wave silhouettes, parasol radial wedges, sunbursts, beach-towel stripes and bold poster rectangles. These shapes come from the coastal subject. Use circles for the sun and umbrellas, not as arbitrary decorative dots.

## Components

Shared navigation, buttons, filters, disclosures and form states retain their existing behaviour. Add a persistent corner motion toggle. Do not add fake project statistics, customers, contact details or sending states.

Motion includes hero picture/title parallax, word entrances, crossing ribbons, rotating parasol graphics, photo masks, desktop horizontal scroll progression, photo tilt and magnetic CTA feedback. A single requestAnimationFrame controller updates scroll variables only when needed. No scroll blocking or autoplay audio.

System reduced-motion or explicit pause shows all content, stops continuous effects, neutralises transforms and returns pinned galleries to normal flow. Touch users retain swiping and clear buttons. Hover effects supplement visible labels.

## Do's and Don'ts

- Keep the Gold Coast identity visible in layout, colour, typography and motion, not just the photograph.
- Preserve Australian English and Chinese content and internal route relationships.
- Maintain readable contrast and visible focus; test desktop and a narrow mobile viewport.
- Do not turn the design back into the Melbourne architecture/technology visual system.
- Do not treat a generic change of colour as the redesign.
- Do not add unrelated application workflows or claim live enquiry delivery.
