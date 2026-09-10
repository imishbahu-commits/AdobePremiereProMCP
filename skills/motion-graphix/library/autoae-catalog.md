# AutoAE viral-hooks catalog — site intelligence + verified template inventory

Crawled 2026-09-10 from `autoae.online` (server-side fetch; the domain itself is
unreachable from the sandbox — curl 000, including `r2.autoae.online` assets and
`npx skills add https://autoae.online` — browser-side only). AutoAE sells credit-based
renders of premium short-form hook templates (mostly by creator Erfan Talebizadeh).
Everything below is public catalog metadata captured for style study and recreation
spec targets. Nothing here is copied template art — names/specs/descriptions are
facts; rebuilds are original.

## Format fingerprint (the premium short-form hook spec)

- Duration **5–7 s** (hook pacing: 1 idea per ~1.2 s)
- Canvas **1080×1920** (9:16 social-vertical first)
- Slots per template: **2–8 text slots**, **0–2 image/media slots**
- Aesthetic: minimal, smooth, flat-2.5D; glassmorphism + gradient mesh + grid/noise
  accents on the premium tier; SaaS/AI-business themes dominate
- Families measured from the front page + detail pages:

| Family | Subcategories (verbatim taxonomy) |
|---|---|
| Animated Flowchart | 3D Flowchart, Comparison Chart, Dynamic Chart, Hierarchy Chart, Process Steps, Pyramid Chart, Timeline, Venn diagram |
| Text Animation | 3D Title Showcase, Bullet-points Steps, Call-to-action, Counter Animation, Highlight Text, Quote Animation, Title Animation |
| UI Animation | Apple Style, Button & Toggle, Cursor Animation, Input Interaction, Loading & Progress, Menu & Navigation, Notification & Popup, Real-world motion style, Search Interaction |
| Logo Animation | 3D Logo Reveal, Dynamic Reveal, Neon Reveal, Particle Reveal, Simple Reveal |
| Engagement Mockup | device mockups, card walls/grids, ranking lists, search-bar interactions |

## Template inventory (36 entries, specs from detail pages where fetched)

| Template | Dur | Slots (T/I) | Family |
|---|---|---|---|
| Growth Line Chart Animation \| Percentage Data Visual | 6s | 8T/2I | Flowchart/Dynamic Chart |
| Data Trend Line Animation \| Single Metric Drop | — | — | Flowchart/Engagement Mockup |
| Tech 2 Data Set Line Chart Animation \| Percentage Data Visual | — | — | Flowchart/Dynamic |
| Line Chart Logo Tracking \| Dark Mode Trend Reveal | — | — | Flowchart |
| Dynamic Growth Chart Animation | — | — | Flowchart |
| Finance Numeric Value \| Percentage Drop Graph | — | — | Flowchart/Mockup |
| Professional Metric Growth Chart | — | — | Flowchart |
| Chart Animation with Smooth Ascent | — | — | Flowchart |
| Dynamic Line Graph Animation with Highlight | — | — | Flowchart |
| SaaS UI Animation \| Padlock Document & Button Reveal | 7s | 3T/1I | UI (Apple Style lane) |
| SaaS UI \| Cursor Interaction & Text Reveal | — | — | UI/Cursor |
| SaaS UI \| Cursor Typing Input with Popup | — | — | UI/Input |
| SaaS App UI \| Phone Mockup & Map Search | — | — | UI/Search |
| SaaS Search Bar UI \| Hook Question & CTA Card | — | — | UI/Search + CTA |
| SaaS Chat UI Text Reveal \| Interactive Input Field | — | — | UI/Input |
| Real-world UI \| Floppy Disk Buttons & Progress | — | — | UI/Real-world |
| Sequential Text Reveal Explainer \| Abstract Shape Transitions | 5s | 3T/2I | Text/Abstract |
| SaaS Headline Reveal Sequence \| 7 Dynamic Text Cards | — | — | Text/Title + Mockup |
| UI Text Sequence Animation \| 5 Key Points | — | — | UI/Steps |
| Animated Character Text Point Showcase \| 5 Key Points | — | — | Mockup/Text |
| Animated Character Text Reveal \| 4 Lines of Text | — | — | Text + Mockup |
| Animated Character Showcase \| Stacked Elements | — | — | Text/Mockup |
| Word-by-Word Text Build-up \| Sequential Reveal | — | — | Text/Title |
| Vintage Lined Paper Text Reveal \| Storytelling Intro | — | — | Text/Story |
| Car Drive Text Reveal \| 2 Headline Statements | — | — | Text/Title |
| SaaS Numeric Highlight Card \| Single Metric Display | — | — | Text/Stat + Mockup |
| Glassmorphism Text Reveal \| 3D Logo Showcase | 5s | 2T/1I | Text + Logo/3D |
| Modern Glassmorphism Text Reveal & Scene Transition | — | — | Text/Glass |
| Geometric Shape Logo Reveal \| Brand Intro | — | — | Logo/Simple→Geo |
| Tech Hierarchy Animation \| 5 Branching Logo Reveals | — | — | Logo + Flowchart/Hierarchy |
| Multiple Logo Showcase Animation \| 6 Brand Marks | — | — | Logo/Simple |
| Dynamic Text Reveal \| Brand Logo Showcase | — | — | Logo/Dynamic |
| AI Business Explainer \| 3 Connected Concepts | — | — | Flowchart/Process |
| Finance Platform Animation \| 5 Connected Institutions | — | — | Flowchart/Hierarchy |
| AutoAE SaaS Launch S3 series (Pt.1 Search Bar → Pt.6 Device End Card: Content Grid, Tag Selection, Ranking List, 3D Card Wall) | — | — | UI + Mockup series |

`—` = front-page entry (specs on its detail page, same 5–7 s / 1080×1920 pattern).

## Reuse notes for our builds

- The taxonomy maps 1:1 onto our `motion-graphix` categories; slot specs become
  composition props (textSlots[], imageSlots[], duration 150–210 frames @30fps, 1080×1920).
- Their "Apple Style" UI lane ≈ our design-review checklist (glass, 8pt grid, spring-ease).
- To see the actual motion of any entry: user-side screen-record → gallery upload
  (sandbox cannot fetch `r2.autoae.online`), or the AutoAE Skill flow
  (`npx skills add https://autoae.online`, Node ≥24, browser auth, credit renders)
  from a machine with normal egress.
- Preview URL scheme (for future reference): `https://r2.autoae.online/previews/<id>-<hash>.jpg`
  page images proxied via `autoae.online/_next/image?url=…&w=3840&q=75`.
