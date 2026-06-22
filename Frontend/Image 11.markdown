---
name: Agri-Tech Precision
colors:
  surface: '#fbf9f8'
  surface-dim: '#dcd9d9'
  surface-bright: '#fbf9f8'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f6f3f2'
  surface-container: '#f0eded'
  surface-container-high: '#eae8e7'
  surface-container-highest: '#e4e2e1'
  on-surface: '#1b1c1c'
  on-surface-variant: '#514532'
  inverse-surface: '#303030'
  inverse-on-surface: '#f3f0f0'
  outline: '#847560'
  outline-variant: '#d6c4ac'
  surface-tint: '#7e5700'
  primary: '#7e5700'
  on-primary: '#ffffff'
  primary-container: '#ffb300'
  on-primary-container: '#6b4900'
  inverse-primary: '#ffba38'
  secondary: '#1b6d24'
  on-secondary: '#ffffff'
  secondary-container: '#a0f399'
  on-secondary-container: '#217128'
  tertiary: '#29695b'
  on-tertiary: '#ffffff'
  tertiary-container: '#8fcebd'
  on-tertiary-container: '#15594c'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdeac'
  primary-fixed-dim: '#ffba38'
  on-primary-fixed: '#281900'
  on-primary-fixed-variant: '#604100'
  secondary-fixed: '#a3f69c'
  secondary-fixed-dim: '#88d982'
  on-secondary-fixed: '#002204'
  on-secondary-fixed-variant: '#005312'
  tertiary-fixed: '#afefdd'
  tertiary-fixed-dim: '#94d3c1'
  on-tertiary-fixed: '#00201a'
  on-tertiary-fixed-variant: '#065043'
  background: '#fbf9f8'
  on-background: '#1b1c1c'
  surface-variant: '#e4e2e1'
typography:
  headline-lg:
    fontFamily: Montserrat
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 48px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Montserrat
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Montserrat
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.01em
  data-num:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '700'
    lineHeight: 24px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  container-max: 1280px
  gutter: 24px
  margin-mobile: 16px
  stack-sm: 8px
  stack-md: 16px
  stack-lg: 32px
  section-gap: 64px
---

## Brand & Style
The design system focuses on a professional agri-tech aesthetic that bridges the gap between sophisticated AI technology and grounded agricultural practice. The visual personality is centered on reliability and sustainability, moving away from "tech-bro" tropes in favor of a clean, editorial-influenced minimalism. 

The emotional response should be one of confidence and clinical accuracy. By utilizing high-quality whitespace and a disciplined color application, the UI establishes itself as a serious tool for quality control. No decorative illustrations are permitted; instead, use high-resolution photography and data-driven visualizations to communicate value.

## Colors
The palette is rooted in the lifecycle of the product. The primary Mango Yellow (#FFB300) is used sparingly for active states and primary actions to maintain its impact. The Deep Green (#2E7D32) serves as the anchor for sustainability and success states.

- **Primary (Mango):** Reserved for the "check" action, progress bars, and critical highlights.
- **Secondary (Forest):** Used for navigation headers, success badges, and "Matang" status.
- **Surface:** A soft Off-white (#FAFAFA) reduces eye strain and provides a premium, "paper-like" feel compared to pure white.
- **Text:** Dark Charcoal (#333333) ensures AAA accessibility and a professional, grounded tone.

## Typography
The system uses a pairing of Montserrat for impact and Inter for functional clarity. All numeric data must follow Indonesian formatting (e.g., "92,34%" using a comma for decimals).

- **Headlines:** Montserrat is used for page titles and section headers to provide a confident, modern architectural feel.
- **Body & Data:** Inter is used for all functional text, descriptions, and system feedback. Its neutral tone ensures that the AI's findings are presented as objective facts.
- **Labels:** Uppercase styling should be avoided; use semi-bold weight for emphasis instead to maintain a friendly tone.

## Layout & Spacing
The design follows a 12-column fixed grid for desktop and a single-column fluid stack for mobile. 

- **Grid:** Use a 24px gutter to provide significant breathing room between data cards.
- **Vertical Rhythm:** A base-8 scale is used for all internal component spacing (8px, 16px, 24px).
- **Mobile Adaptivity:** On mobile, margins reduce to 16px. Section gaps should be reduced to 40px to keep the analysis results "above the fold" after an upload.

## Elevation & Depth
Depth is created through tonal layering rather than aggressive shadows. 

- **Surface Layering:** Use thin, low-contrast borders (1px solid #E0E0E0) for cards.
- **Shadows:** Apply a single "Ambient" shadow style for the primary analysis card: `0 4px 20px rgba(0, 0, 0, 0.05)`.
- **Interaction:** On hover, cards should lift slightly by increasing the shadow spread and shifting -2px on the Y-axis. 
- **Upload Area:** Use a dashed border for the dropzone to imply a physical slot or "insert" area.

## Shapes
The design system utilizes "Rounded" (Level 2) geometry to appear approachable and organic, reflecting the natural shape of the fruit.

- **Standard Components:** Buttons, inputs, and small alerts use a 0.5rem (8px) radius.
- **Content Containers:** Main analysis cards and the upload dropzone use a `rounded-lg` 1rem (16px) radius to create a soft, modern framing.
- **Status Badges:** Use a fully pill-shaped radius to distinguish them from interactive buttons.

## Components

### Buttons
- **Primary:** Background #FFB300, Text #333333, Bold. No gradients.
- **Secondary:** Transparent background, Border 2px solid #2E7D32, Text #2E7D32.

### Status Badges (Indonesian)
- **Mentah (Unripe):** Background #E0E0E0, Text #616161.
- **Matang (Ripe):** Background #E8F5E9, Text #2E7D32.
- **Busuk (Overripe/Decayed):** Background #FFEBEE, Text #C62828.

### Progress Bars (Confidence Score)
A thin 8px track with a rounded cap. The fill color should dynamically change based on the confidence level (Yellow for processing, Green for high-certainty results). Include the percentage to the right using the `data-num` style.

### Upload Dropzone
A large, 16px rounded container with a #FAFAFA background and #2E7D32 dashed border. It should include a "Camera" or "File" icon and a clear instruction: "Seret foto mangga di sini atau klik untuk memilih file."

### Recommendation Cards
Small cards placed below the analysis result. Each card should feature a small icon (e.g., a clock for storage time, a fridge for cooling) and a concise instruction in Indonesian (e.g., "Simpan di suhu ruangan").