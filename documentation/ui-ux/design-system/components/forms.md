# Forms

## Overview

Form components in the UltraAI design system reflect the core interface patterns seen in the mockups. From the primary prompt input to model selection dropdowns, forms maintain the cyberpunk aesthetic while ensuring usability across all themes.

## Form Components

### Text Input
The primary text input, used for prompts, search, and text entry.

```tsx
<Input 
  placeholder="Enter a prompt" 
  variant="primary"
  size="lg"
/>
```

#### Cyberpunk Theme
```css
.input-cyberpunk {
  background: hsl(var(--background-secondary) / 0.8);
  border: 2px solid hsl(var(--border));
  color: hsl(var(--foreground));
  font-family: 'JetBrains Mono', monospace;
  font-size: 1rem;
  padding: 16px 20px;
  border-radius: 8px;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.input-cyberpunk::placeholder {
  color: hsl(var(--foreground-muted));
  font-style: italic;
}

.input-cyberpunk:focus {
  outline: none;
  border-color: hsl(var(--neon-cyan));
  box-shadow: 
    0 0 0 1px hsl(var(--neon-cyan)),
    0 0 15px hsl(var(--neon-cyan) / 0.3),
    inset 0 0 15px hsl(var(--neon-cyan) / 0.1);
  background: hsl(var(--background-tertiary) / 0.9);
}

.input-cyberpunk:hover:not(:focus) {
  border-color: hsl(var(--neon-cyan) / 0.7);
  box-shadow: 0 0 10px hsl(var(--neon-cyan) / 0.2);
}
```

#### Corporate Theme
```css
.input-corporate {
  background: white;
  border: 1px solid hsl(var(--border));
  color: hsl(var(--foreground));
  font-family: 'Inter', sans-serif;
  padding: 12px 16px;
  border-radius: 6px;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px hsl(var(--border) / 0.1);
}

.input-corporate:focus {
  outline: none;
  border-color: hsl(var(--corporate-blue));
  box-shadow: 
    0 0 0 3px hsl(var(--corporate-blue) / 0.1),
    0 1px 3px hsl(var(--border) / 0.1);
}
```

### Textarea
Multi-line text input for longer prompts and content.

```tsx
<Textarea 
  placeholder="Enter a detailed prompt or paste your content here..."
  rows={4}
  variant="primary"
/>
```

```css
.textarea-cyberpunk {
  resize: vertical;
  min-height: 120px;
  font-family: 'JetBrains Mono', monospace;
  line-height: 1.6;
}

/* Custom scrollbar for cyberpunk theme */
.textarea-cyberpunk::-webkit-scrollbar {
  width: 8px;
}

.textarea-cyberpunk::-webkit-scrollbar-track {
  background: hsl(var(--background-secondary));
  border-radius: 4px;
}

.textarea-cyberpunk::-webkit-scrollbar-thumb {
  background: hsl(var(--neon-cyan) / 0.6);
  border-radius: 4px;
}

.textarea-cyberpunk::-webkit-scrollbar-thumb:hover {
  background: hsl(var(--neon-cyan) / 0.8);
}
```

### Select Dropdown
Used for model selection, attachment options, and other choices.

```tsx
<Select 
  placeholder="Select a model"
  options={models}
  variant="primary"
/>
```

#### Cyberpunk Theme
```css
.select-cyberpunk {
  position: relative;
  background: hsl(var(--background-secondary) / 0.8);
  border: 2px solid hsl(var(--border));
  color: hsl(var(--foreground));
  font-family: 'JetBrains Mono', monospace;
  padding: 16px 48px 16px 20px;
  border-radius: 8px;
  cursor: pointer;
  backdrop-filter: blur(10px);
  transition: all 0.2s ease;
}

.select-cyberpunk::after {
  content: '▼';
  position: absolute;
  right: 16px;
  top: 50%;
  transform: translateY(-50%);
  color: hsl(var(--neon-cyan));
  font-size: 0.75rem;
  transition: transform 0.2s ease;
}

.select-cyberpunk[aria-expanded="true"]::after {
  transform: translateY(-50%) rotate(180deg);
}

.select-cyberpunk:focus {
  outline: none;
  border-color: hsl(var(--neon-cyan));
  box-shadow: 
    0 0 0 1px hsl(var(--neon-cyan)),
    0 0 15px hsl(var(--neon-cyan) / 0.3);
}
```

#### Select Options Panel
```css
.select-options-cyberpunk {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  z-index: 50;
  background: hsl(var(--background-tertiary) / 0.95);
  border: 2px solid hsl(var(--neon-cyan));
  border-radius: 8px;
  margin-top: 4px;
  backdrop-filter: blur(20px);
  box-shadow: 
    0 0 20px hsl(var(--neon-cyan) / 0.3),
    0 10px 30px hsl(var(--background) / 0.8);
  max-height: 200px;
  overflow-y: auto;
}

.select-option-cyberpunk {
  padding: 12px 20px;
  cursor: pointer;
  transition: all 0.15s ease;
  font-family: 'JetBrains Mono', monospace;
  border-bottom: 1px solid hsl(var(--border) / 0.3);
}

.select-option-cyberpunk:hover {
  background: hsl(var(--neon-cyan) / 0.1);
  color: hsl(var(--neon-cyan));
}

.select-option-cyberpunk:last-child {
  border-bottom: none;
}

.select-option-cyberpunk[aria-selected="true"] {
  background: hsl(var(--neon-cyan) / 0.2);
  color: hsl(var(--neon-cyan));
}
```

### File Upload
Based on the mockup "Upload attachments (optional)" pattern.

```tsx
<FileUpload 
  placeholder="Upload attachments (optional)"
  accept=".pdf,.doc,.txt"
  multiple
/>
```

```css
.file-upload-cyberpunk {
  position: relative;
  background: hsl(var(--background-secondary) / 0.8);
  border: 2px dashed hsl(var(--border));
  border-radius: 8px;
  padding: 24px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  backdrop-filter: blur(10px);
}

.file-upload-cyberpunk:hover {
  border-color: hsl(var(--neon-cyan) / 0.7);
  background: hsl(var(--background-tertiary) / 0.8);
}

.file-upload-cyberpunk.dragover {
  border-color: hsl(var(--neon-cyan));
  background: hsl(var(--neon-cyan) / 0.05);
  box-shadow: 
    0 0 20px hsl(var(--neon-cyan) / 0.3),
    inset 0 0 20px hsl(var(--neon-cyan) / 0.1);
}

.file-upload-icon {
  width: 48px;
  height: 48px;
  margin: 0 auto 16px;
  color: hsl(var(--neon-cyan));
  opacity: 0.7;
}

.file-upload-text {
  font-family: 'JetBrains Mono', monospace;
  color: hsl(var(--foreground-muted));
  font-size: 0.875rem;
}

.file-upload-text strong {
  color: hsl(var(--neon-cyan));
}
```

## Form Layout Patterns

### Primary Analysis Form
Based on the mockup layout with prompt, attachments, model selection, and cost display.

```tsx
<div className="analysis-form">
  <div className="form-section">
    <Textarea 
      placeholder="Enter a prompt"
      className="prompt-input"
    />
  </div>
  
  <div className="form-section">
    <FileUpload placeholder="Upload attachments (optional)" />
  </div>
  
  <div className="form-section">
    <Select 
      placeholder="Select a model"
      options={models}
      value="LLM-1"
    />
  </div>
  
  <div className="cost-section">
    <div className="cost-display">
      <span className="cost-label">COST ESTIMATE</span>
      <span className="cost-value">$0.40</span>
    </div>
  </div>
  
  <Button variant="primary" size="lg" className="submit-button">
    GENERATE
  </Button>
</div>
```

```css
.analysis-form {
  max-width: 480px;
  margin: 0 auto;
  padding: 32px;
  background: hsl(var(--card) / 0.8);
  border: 2px solid hsl(var(--border));
  border-radius: 16px;
  backdrop-filter: blur(20px);
  box-shadow: 
    0 0 40px hsl(var(--neon-cyan) / 0.1),
    0 20px 40px hsl(var(--background) / 0.8);
}

.form-section {
  margin-bottom: 24px;
}

.cost-section {
  margin-bottom: 32px;
  padding: 16px 0;
  border-top: 1px solid hsl(var(--border) / 0.3);
  border-bottom: 1px solid hsl(var(--border) / 0.3);
}

.cost-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.cost-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  color: hsl(var(--foreground-muted));
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.cost-value {
  font-family: 'Orbitron', monospace;
  font-size: 1.5rem;
  font-weight: 700;
  color: hsl(var(--neon-orange));
  text-shadow: 0 0 10px hsl(var(--neon-orange) / 0.5);
}

.submit-button {
  width: 100%;
}
```

### Form Validation

#### Error States
```css
.input-error {
  border-color: hsl(var(--error));
  box-shadow: 0 0 0 1px hsl(var(--error)), 0 0 10px hsl(var(--error) / 0.3);
}

.error-message {
  color: hsl(var(--error));
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  margin-top: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}
```

#### Success States
```css
.input-success {
  border-color: hsl(var(--success));
  box-shadow: 0 0 0 1px hsl(var(--success)), 0 0 10px hsl(var(--success) / 0.3);
}

.success-message {
  color: hsl(var(--success));
  font-size: 0.75rem;
  font-family: 'JetBrains Mono', monospace;
  margin-top: 8px;
}
```

### Form Labels
```css
.form-label {
  display: block;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.875rem;
  font-weight: 500;
  color: hsl(var(--foreground));
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.025em;
}

.form-label.required::after {
  content: ' *';
  color: hsl(var(--error));
}
```

## Responsive Form Design

### Mobile Adaptations
```css
@media (max-width: 768px) {
  .analysis-form {
    padding: 24px 16px;
    margin: 16px;
    max-width: none;
  }
  
  .cost-display {
    flex-direction: column;
    gap: 8px;
    text-align: center;
  }
  
  .form-section {
    margin-bottom: 20px;
  }
  
  /* Larger touch targets */
  .input-cyberpunk,
  .select-cyberpunk {
    padding: 18px 20px;
    font-size: 1.125rem;
  }
}
```

### Tablet Optimizations
```css
@media (min-width: 768px) and (max-width: 1024px) {
  .analysis-form {
    max-width: 600px;
    padding: 40px;
  }
}
```

## Accessibility Features

### Focus Management
```css
.form-control:focus-visible {
  outline: 2px solid hsl(var(--ring));
  outline-offset: 2px;
}

/* Skip focus ring for mouse users */
.form-control:focus:not(:focus-visible) {
  outline: none;
}
```

### Screen Reader Support
```tsx
<label htmlFor="prompt-input" className="sr-only">
  Enter your analysis prompt
</label>
<textarea
  id="prompt-input"
  aria-describedby="prompt-help"
  aria-required="true"
  placeholder="Enter a prompt"
/>
<div id="prompt-help" className="sr-only">
  Describe what you'd like to analyze. Be specific for better results.
</div>
```

### High Contrast Mode
```css
@media (prefers-contrast: high) {
  .input-cyberpunk {
    background: hsl(var(--background));
    border-width: 3px;
  }
  
  .input-cyberpunk:focus {
    box-shadow: none;
    border-color: hsl(var(--foreground));
  }
}
```

## Implementation Example

```tsx
import React, { useState } from 'react';
import { useTheme } from '../theme/ThemeContext';

interface FormInputProps {
  type?: 'text' | 'email' | 'password';
  placeholder?: string;
  value?: string;
  onChange?: (value: string) => void;
  error?: string;
  success?: string;
  required?: boolean;
  disabled?: boolean;
  className?: string;
}

const FormInput: React.FC<FormInputProps> = ({
  type = 'text',
  placeholder,
  value,
  onChange,
  error,
  success,
  required = false,
  disabled = false,
  className = ''
}) => {
  const { theme } = useTheme();
  const [focused, setFocused] = useState(false);
  
  const baseClasses = 'form-control transition-all duration-200';
  const themeClasses = `input-${theme.style}`;
  const stateClasses = {
    error: error ? 'input-error' : '',
    success: success ? 'input-success' : '',
    disabled: disabled ? 'input-disabled' : '',
    focused: focused ? 'input-focused' : ''
  };
  
  const allClasses = [
    baseClasses,
    themeClasses,
    ...Object.values(stateClasses),
    className
  ].filter(Boolean).join(' ');
  
  return (
    <div className="form-field">
      <input
        type={type}
        className={allClasses}
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange?.(e.target.value)}
        onFocus={() => setFocused(true)}
        onBlur={() => setFocused(false)}
        required={required}
        disabled={disabled}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={error ? 'field-error' : success ? 'field-success' : undefined}
      />
      {error && (
        <div id="field-error" className="error-message">
          <span className="error-icon">⚠</span>
          {error}
        </div>
      )}
      {success && (
        <div id="field-success" className="success-message">
          <span className="success-icon">✓</span>
          {success}
        </div>
      )}
    </div>
  );
};

export default FormInput;
```

---

**Next**: Review [Containers](./containers.md) for layout component specifications.