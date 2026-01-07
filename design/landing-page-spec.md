# Tempo Landing Page - Design Specification

## Overview
A minimalistic single-page landing site for Tempo, an automated Claude Code runner. The design should feel technical but approachable—like a developer tool that respects your time.

---

## Design Principles

### Aesthetic
- **Minimalistic**: Lots of whitespace, only essential elements
- **Technical but warm**: Developer-focused without feeling cold
- **Balanced corners**: 4-6px border radius (not pill-shaped, not sharp)
- **Confident typography**: Clear hierarchy, no decorative fonts

### Color Palette (3-4 colors max)
- **Background**: Off-white or very light gray (#FAFAFA or #F5F5F5)
- **Primary text**: Near-black (#1A1A1A)
- **Accent**: Deep blue or teal (#2563EB or #0D9488)
- **Secondary**: Medium gray (#6B7280)
- **Optional dark mode**: Dark gray background (#0F0F0F), light text

---

## Layout (Single Page, Top to Bottom)

### Section 1: Hero (Above the fold)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                          ◷ TEMPO                            │
│                                                             │
│         Run Claude Code overnight.                          │
│         Automatically.                                      │
│                                                             │
│    [ Brief one-liner description ]                          │
│                                                             │
│         ┌──────────────────────────────┐                    │
│         │  Download for macOS ↓        │                    │
│         └──────────────────────────────┘                    │
│                                                             │
│         Linux  ·  Windows  ·  View on GitHub                │
│                                                             │
│                    12,847 downloads                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

#### Logo: "TEMPO"
- The "O" in TEMPO could be stylized as a clock or timer icon (◷)
- Or: A simple hourglass/timer icon next to the wordmark
- Font: Monospace or geometric sans-serif (e.g., JetBrains Mono, Space Grotesk, or Inter)
- Weight: Bold/Semi-bold for the wordmark

#### Headline
- Main: "Run Claude Code overnight. Automatically."
- Or: "Sleep while Claude codes."
- Sub: "Tempo handles rate limits, waits for reset, and continues your task—no intervention needed."

#### Primary CTA
- Large button: "Download for macOS" (auto-detects OS)
- Below: Text links for other platforms: "Linux · Windows · View on GitHub"

#### Download Counter
- Small, subtle text below CTA
- Format: "12,847 downloads" or "12.8k downloads"
- Optional: Small upward trend icon

---

### Section 2: How It Works (Optional, brief)

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                      How it works                           │
│                                                             │
│   ┌─────────┐      ┌─────────┐      ┌─────────┐            │
│   │    1    │      │    2    │      │    3    │            │
│   │  Start  │  →   │  Wait   │  →   │  Done   │            │
│   │  task   │      │  smart  │      │         │            │
│   └─────────┘      └─────────┘      └─────────┘            │
│                                                             │
│   Give Tempo      Hits rate limit?   Wake up to            │
│   a big task      It waits until     completed work        │
│                   credits reset                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

- Three simple steps with icons or numbers
- Very brief text under each
- Can be horizontal cards or vertical list

---

### Section 3: Install Commands

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│                       Installation                          │
│                                                             │
│   macOS / Linux                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ curl -fsSL https://tempo.dev/install.sh | bash    ⎘│   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   Windows PowerShell                                        │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ irm https://tempo.dev/install.ps1 | iex           ⎘│   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

- Code blocks with copy button (⎘ icon)
- Monospace font
- Subtle background (slightly darker than page)
- Border radius: 4-6px

---

### Section 4: Footer

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Tempo · GitHub · MIT License                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

- Minimal footer
- Links: GitHub repo, License
- Optional: Made by [name]

---

## Component Specifications

### Buttons
- Primary: Filled with accent color, white text
- Secondary: Outlined or text-only
- Border radius: 6px
- Padding: 12px 24px
- Font weight: Medium (500)

### Code Blocks
- Background: #F1F5F9 (light mode) or #1E293B (dark mode)
- Font: JetBrains Mono or SF Mono
- Border radius: 6px
- Border: 1px solid #E2E8F0

### Typography
- Headline: 48-56px, Bold
- Subheadline: 18-20px, Regular, secondary color
- Body: 16px, Regular
- Code: 14px, Monospace

---

## Logo Concepts

### Option A: Timer Icon + Wordmark
```
◷ TEMPO
```
- Simple clock/timer icon (quarter filled or with motion lines)
- Clean wordmark next to it

### Option B: Integrated Letter
```
TEMP◷
```
- The "O" is replaced with a minimal clock face

### Option C: Abstract
```
⏱ tempo
```
- Lowercase wordmark
- Stopwatch or hourglass icon

---

## Responsive Behavior

### Desktop (1200px+)
- Centered content, max-width 800px
- Generous whitespace

### Tablet (768px - 1199px)
- Same layout, slightly reduced spacing

### Mobile (< 768px)
- Stack elements vertically
- Full-width buttons
- Smaller headline (36px)

---

## Animations (Subtle)

- Button hover: Slight lift (translateY -2px) + shadow
- Code block copy: Brief checkmark animation
- Download counter: Optional count-up on page load
- No flashy animations—keep it professional

---

## Reference Sites (Aesthetic inspiration)
- linear.app (clean, minimal)
- vercel.com (developer-focused)
- raycast.com (balanced warmth)
- arc.net (confident typography)

---

## Files Needed
1. Desktop design (1440px width)
2. Mobile design (375px width)
3. Logo in SVG format
4. Dark mode variant (optional)

