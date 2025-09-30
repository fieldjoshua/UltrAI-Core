# Copy Improvement Snippets - Ready to Use

Quick reference for copy-paste implementation of improved user-facing text.

---

## IntroScreen.tsx Snippets

### Main Value Prop
```tsx
// REPLACE lines 156-164
<span
  className="text-2xl font-bold block mb-4"
  style={{
    background: 'linear-gradient(90deg, #00ff9f, #00d4ff, #bd00ff)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    backgroundClip: 'text',
    textShadow: 'none',
  }}
>
  Smarter AI Answers, Better Value
</span>
Ask once, get answers from GPT-4, Claude, Gemini, and more—combined into 
one comprehensive response.
<span className="font-bold text-white">
  {' '}Pay per query, not per month
</span>.
```

### Sub-bullets
```tsx
// REPLACE lines 166-192
<div className="flex justify-center gap-6 text-sm mt-6 text-white/90">
  <span className="text-white" style={{ textShadow: '0 0 5px rgba(255,255,255,0.3)' }}>
    From $0.50 per query
  </span>
  <span className="text-white/70">•</span>
  <span className="text-white" style={{ textShadow: '0 0 5px rgba(255,255,255,0.3)' }}>
    No subscriptions
  </span>
  <span className="text-white/70">•</span>
  <span className="text-white" style={{ textShadow: '0 0 5px rgba(255,255,255,0.3)' }}>
    Results in ~30 seconds
  </span>
</div>
```

### CTA Button
```tsx
// REPLACE line 211-212
<span>Get Started Free</span>
```

### Trust Indicators
```tsx
// REPLACE lines 233-245
<div className="flex justify-center gap-8 text-sm text-white/80">
  <div className="flex items-center gap-2">
    <span className="text-green-400">✓</span>
    <span>OpenAI, Anthropic, Google</span>
  </div>
  <div className="flex items-center gap-2">
    <span className="text-green-400">✓</span>
    <span>No subscription required</span>
  </div>
  <div className="flex items-center gap-2">
    <span className="text-green-400">✓</span>
    <span>Most queries under $2</span>
  </div>
</div>
```

---

## ErrorFallback.tsx - Complete Component

```tsx
import React from 'react';
import { FallbackProps } from 'react-error-boundary';

const ErrorFallback: React.FC<FallbackProps> = ({
  error,
  resetErrorBoundary,
}) => {
  return (
    <div className="error-container max-w-lg mx-auto p-8 bg-white dark:bg-gray-800 rounded-lg shadow-lg text-center">
      <div className="text-6xl mb-4">😅</div>
      <h2 className="text-2xl font-bold mb-2 text-gray-800 dark:text-white">
        Oops! We hit a snag
      </h2>
      <p className="text-gray-600 dark:text-gray-300 mb-6">
        Don't worry—your work isn't lost. Let's try that again.
      </p>
      
      {process.env.NODE_ENV === 'development' && (
        <details className="text-left mb-6 text-sm">
          <summary className="cursor-pointer text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300">
            Technical details
          </summary>
          <pre className="mt-2 p-4 bg-gray-100 dark:bg-gray-900 rounded overflow-auto text-xs">
            {error.message}
          </pre>
        </details>
      )}
      
      <div className="flex gap-3 justify-center">
        <button 
          onClick={resetErrorBoundary}
          className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold transition-colors"
        >
          Try Again
        </button>
        <a 
          href="mailto:support@ultrai.com"
          className="px-6 py-2 border-2 border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 font-semibold transition-colors"
        >
          Contact Support
        </a>
      </div>
    </div>
  );
};

export default ErrorFallback;
```

---

## OfflineBanner.tsx Snippets

### Offline Messages
```tsx
// REPLACE lines 125-130
<span className="font-medium">
  {customMessage ||
    (!isOnline
      ? 'No internet connection. Reconnect to run new queries.'
      : !apiAvailable
        ? 'Can't reach our servers. We're working on it—please try again in a moment.'
        : 'Back online!')}
</span>
```

### Extended Message
```tsx
// REPLACE lines 176-178
<p>
  {!isOnline
    ? 'Your recent work is saved locally. We'll sync everything when you're back online.'
    : 'We're automatically retrying. Your queries are safe.'}
</p>
```

---

## ProcessingStep.tsx Snippet

### Processing Message
```tsx
// REPLACE lines 60-66
<div className="text-center max-w-md">
  <h3 className="text-lg font-medium text-white mb-2">
    Your AI Team is Working...
  </h3>
  <p className="text-gray-400 text-sm">
    Running your query through GPT-4, Claude, and Gemini. 
    Usually takes 20-30 seconds.
  </p>
</div>
```

---

## ResultsStep.tsx Snippets

### Results Header
```tsx
// REPLACE line 31
<h3 className="text-xl font-medium text-gray-800 dark:text-white">
  Your Results
</h3>
```

### Empty State
```tsx
// REPLACE lines 72-74
<div className="text-center py-8 text-gray-500">
  <p className="mb-4">No results yet. Run an analysis to get started!</p>
  <button 
    onClick={onStartNewAnalysis}
    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
  >
    Start Your First Analysis
  </button>
</div>
```

---

## ModelSelectionStep.tsx Snippet

### Instructions
```tsx
// REPLACE lines 40-44
<p className="text-cyan-100 mb-4">
  Pick which AI models to use. Each has different strengths. 
  Choose one as your "Ultra" model—it'll combine everyone's answers 
  into the final result.
</p>
```

---

## index.html Snippets

### Meta Description
```html
<!-- REPLACE lines 6-9 -->
<meta
  name="description"
  content="Get better AI answers by combining GPT-4, Claude, and Gemini. Pay per query, no subscriptions. Most queries under $2."
/>
```

### Page Title
```html
<!-- OPTIONAL: Make title more descriptive -->
<title>UltrAI - Smarter AI Answers from Multiple Models</title>
```

### Loading Message
```html
<!-- REPLACE line 87 -->
<p>Preparing your AI workspace...</p>
```

---

## Quick Copy-Only Changes (No Code)

These are pure text replacements with no logic changes:

### Button Labels
- ❌ "Enter UltrAI" → ✅ "Get Started Free"
- ❌ "Try again" → ✅ "Try Again" (capitalize)
- ❌ "Ultra Analysis Results" → ✅ "Your Results"

### Headings
- ❌ "AI Models Working Together" → ✅ "Your AI Team is Working..."
- ❌ "Intelligence Multiplication Platform" → ✅ "Smarter AI Answers, Better Value"

### Instructions
- ❌ "What do you want to create?" → ✅ "What are you working on today?"
- ❌ "Which AI models do you want to perform your query?" → ✅ "Which AI models should work on this?"

### Error Messages
- ❌ "Something went wrong" → ✅ "Oops! We hit a snag"
- ❌ "You are offline. Some features may be unavailable." → ✅ "No internet connection. Reconnect to run new queries."

---

## Testing Checklist

After implementing copy changes:

```bash
# 1. Visual check
make dev
# Visit http://localhost:8000

# 2. Check all wizard steps
# Click through entire flow

# 3. Trigger error state
# Disconnect network, try to submit

# 4. Check mobile view
# Resize browser to 375px width

# 5. Screen reader test (macOS)
# CMD+F5 to enable VoiceOver, navigate through

# 6. Check all copy for:
- [ ] Typos/grammar
- [ ] Consistent tone (friendly, helpful)
- [ ] No jargon ("orchestrate", "synthesize")
- [ ] Accurate pricing claims
- [ ] Mobile-friendly (no text overflow)
```

---

## Rollback Plan

If users react negatively to new copy:

1. **Keep original files:**
   ```bash
   cp wizard_steps.json wizard_steps_ORIGINAL.json
   ```

2. **Quick rollback:**
   ```bash
   git checkout wizard_steps.json
   git checkout src/components/wizard/IntroScreen.tsx
   # etc.
   ```

3. **A/B test approach:**
   - Implement changes on staging first
   - Monitor user feedback for 1 week
   - Roll out to production if positive

---

*Created: 2025-09-30*  
*Status: Ready for copy-paste implementation*
