# Design System Specification - AgroPulse

This document maps all colors, layout guides, typographies, and component metrics of the AgroPulse design system.

---

## 1. Color Palette

| Token | HEX | RGB | Component / Usage |
|---|---|---|---|
| **Primary** | `#22c55e` | `rgb(34,197,94)` | Active buttons, navigation active states, success badges. |
| **Dark Primary** | `#16a34a` | `rgb(22,163,74)` | Button hover states. |
| **Neutral Dark** | `#0f172a` | `rgb(15,23,42)` | Navigation bar background. |
| **Base Background** | `#f1f5f9` | `rgb(241,245,249)`| Main content background. |
| **Card White** | `#ffffff` | `rgb(255,255,255)`| Layout card components. |
| **Text Dark** | `#1f2933` | `rgb(31,41,51)` | Default body typography. |
| **Text Muted** | `#64748b` | `rgb(100,116,139)`| Subtitles and descriptive text. |

---

## 2. Typography

- **Font Family**: `Arial, Helvetica, sans-serif` globally.
- **Weights**:
  - Regular: `400`
  - Semibold: `600`
  - Bold: `700`
- **Sizes Hierarchy**:
  - Hero Header (`h1`): `2.6rem` to `3rem`
  - Content Title (`h2`): `2.4rem`
  - Card Title (`h3`): `1.5rem`
  - Body copy: `1rem`
  - Muted captions: `0.85rem`

---

## 3. UI Layout & Spacing
- **Container**: Max width configured to `1200px` for dashboards, and `950px` for comparisons.
- **Card Padding**: Padded with `25px` or `30px` depending on card layout focus.
- **Border Radius**: Card components round using `16px`. Buttons and inputs use `8px` or `10px`.
- **Drop Shadows**: Standard card drop shadows are set to `0 10px 25px rgba(0,0,0,0.08)`.
- **Responsive Breakpoint Grid**: Uses CSS Grid template `repeat(auto-fit, minmax(260px, 1fr))` to naturally fold elements on mobile viewports (< 768px).
