# Brand Guidelines

## Brand Identity

### Mission Statement
**"Multiply Your AI"** - UltraAI amplifies artificial intelligence capabilities through intelligent orchestration, making advanced AI accessible and powerful for everyone.

### Brand Values
- **Innovation**: Cutting-edge technology with futuristic vision
- **Amplification**: Making AI more powerful and effective
- **Accessibility**: Advanced capabilities made simple to use
- **Intelligence**: Smart, logical, efficient solutions

## Logo & Typography

### Primary Wordmark: "ULTRA AI"
```css
.brand-wordmark {
  font-family: 'Orbitron', 'JetBrains Mono', monospace;
  font-weight: 700;
  font-size: clamp(2rem, 8vw, 6rem);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  line-height: 1.1;
}
```

#### Typography Specifications
- **Primary Font**: Orbitron (futuristic, cyberpunk)
- **Fallback**: JetBrains Mono (monospace, technical)
- **System Fallback**: monospace
- **Character Spacing**: 10% (0.1em)
- **Case**: Always UPPERCASE for brand text

### Tagline: "MULTIPLY YOUR AI!"
```css
.brand-tagline {
  font-family: 'Orbitron', 'JetBrains Mono', monospace;
  font-weight: 600;
  font-size: clamp(1rem, 3vw, 1.5rem);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--neon-orange);
}
```

## Visual Themes

### Cyberpunk Theme (Primary Brand Expression)

#### Color Treatment
```css
/* Primary brand text */
.brand-text-primary {
  color: #00FFFF; /* Neon Cyan */
  text-shadow: 
    0 0 10px #00FFFF,
    0 0 20px #00FFFF,
    0 0 30px #00FFFF;
}

/* Secondary brand text */
.brand-text-secondary {
  color: #FF6B35; /* Neon Orange */
  text-shadow: 
    0 0 10px #FF6B35,
    0 0 20px #FF6B35;
}
```

#### Visual Elements
- **Neon glow effects** on all brand typography
- **Grid overlays** suggesting digital/matrix aesthetic
- **Billboard-style** presentation in hero areas
- **Urban night** backgrounds with city silhouettes

### Corporate Theme (Professional Alternative)

#### Color Treatment
```css
.brand-text-corporate {
  color: #2563EB; /* Professional Blue */
  text-shadow: none;
  font-weight: 600;
}
```

#### Visual Elements
- **Clean, minimal** presentation
- **Subtle gradients** instead of neon
- **Professional typography** without effects
- **Light backgrounds** with subtle textures

### Classic Theme (Accessible Alternative)

#### Color Treatment
```css
.brand-text-classic {
  color: #1E293B; /* Dark Slate */
  text-shadow: none;
  font-weight: 500;
}
```

## Brand Applications

### Hero/Billboard Presentation
Based on mockup analysis, the brand should be presented as a prominent "billboard" or sign:

```tsx
<div className="brand-billboard">
  <div className="brand-frame">
    <h1 className="brand-wordmark neon-cyan">ULTRA AI</h1>
    <p className="brand-tagline neon-orange">MULTIPLY YOUR AI!</p>
  </div>
  <div className="support-structure">
    {/* Visual scaffolding/frame elements */}
  </div>
</div>
```

### Interface Integration
- **Navigation**: Condensed wordmark in header
- **Loading states**: Animated brand elements
- **Empty states**: Subtle brand presence
- **Modals**: Minimal brand reference

## Voice & Tone

### Personality
- **Confident**: We know AI and make it better
- **Approachable**: Complex technology made simple
- **Progressive**: Always pushing forward
- **Empowering**: Amplifying human capabilities

### Tone Guidelines
- **Technical but accessible**: Use precise language without jargon
- **Action-oriented**: Focus on what users can accomplish
- **Future-focused**: Emphasize advancement and improvement
- **Inclusive**: Technology for everyone

### Messaging Patterns
- "Multiply your [capability]"
- "Amplify your [workflow]"
- "Orchestrate [multiple AI models]"
- "Elevate your [AI experience]"

## Usage Guidelines

### Do's
✅ Use UPPERCASE for all brand text  
✅ Maintain consistent letter spacing  
✅ Apply appropriate theme treatments  
✅ Ensure sufficient contrast ratios  
✅ Scale proportionally across devices  

### Don'ts
❌ Never use lowercase for "ultra ai"  
❌ Don't compress or stretch the wordmark  
❌ Avoid low-contrast color combinations  
❌ Don't use decorative fonts for brand text  
❌ Never place brand text over busy backgrounds without treatment  

## Accessibility Considerations

### Contrast Requirements
- **Cyberpunk**: Neon on dark backgrounds (4.5:1 minimum)
- **Corporate**: Blue on light backgrounds (7:1 preferred)
- **Classic**: Dark text on light backgrounds (7:1 preferred)

### Reduced Motion
When `prefers-reduced-motion` is enabled:
- Remove text glow animations
- Eliminate pulsing effects
- Maintain static brand presentation

### Screen Readers
- Brand text includes proper semantic markup
- Tagline marked as supplementary information
- Visual effects don't interfere with text recognition

## File Assets

### Required Fonts
```css
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
```

### Logo Variations
- **Primary**: Neon cyan wordmark with orange tagline
- **Corporate**: Blue wordmark with dark tagline
- **Monochrome**: Single color for special applications
- **Reversed**: Light versions for dark backgrounds

---

**Next Steps**: Review [Color System](./color-system.md) for complete color specifications.