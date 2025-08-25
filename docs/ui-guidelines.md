---
applyTo: "{frontend/**/*.{css,scss},frontend/**/*.vue}"
---

# UI Guidelines

## Theme Support

- A toggle is provided to switch between light and dark mode
- Application should have a modern and clean design

## Color Scheme

### Light Mode
```css
:root {
  --primary: #4F46E5;
  --background: #FFFFFF;
  --text: #1F2937;
  --surface: #F3F4F6;
}
```

### Dark Mode
```css
:root[data-theme="dark"] {
  --primary: #818CF8;
  --background: #111827;
  --text: #F9FAFB;
  --surface: #1F2937;
}
```

## Component Guidelines

1. Use consistent spacing
   - Padding: 1rem (16px) for containers
   - Margin: 0.5rem (8px) between elements

2. Typography
   - Use system font stack
   - Base size: 16px
   - Scale using relative units (rem)

3. Interactive Elements
   - Clear hover states
   - Focus indicators for accessibility
   - Loading states for async actions

4. Responsive Design
   - Mobile-first approach
   - Breakpoints at standard sizes:
     - sm: 640px
     - md: 768px
     - lg: 1024px
     - xl: 1280px
