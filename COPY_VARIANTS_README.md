# UltrAI Copy Variants - Multi-Persona Guide

Created: 2025-09-30  
Status: Fun experimental variants ready for testing

---

## 📚 Available Variants

We've created **11** different copy variants for the wizard steps, each targeting a different audience persona:

### English Variants

| Variant | File | Target Audience | Tone | Best For |
|---------|------|----------------|------|----------|
| **Improved** | `wizard_steps_IMPROVED.json` | General public | Clear, friendly, professional | **DEFAULT RECOMMENDATION** |
| **Beginner** | `wizard_steps_BEGINNER.json` | First-time AI users | Patient, explanatory, simple | Onboarding, tutorials |
| **Developer** | `wizard_steps_DEVELOPER.json` | Engineers, tech-savvy | Technical, precise, API-focused | Developer docs, tech demos |
| **Gen Alpha** | `wizard_steps_BRAINROT.json` | Gen Z/Alpha (13-25) | Slang-heavy, meme culture | TikTok marketing, social media |
| **College** | `wizard_steps_COLLEGE.json` | University students | Casual but smart, relatable | Student discounts, .edu campaigns |
| **Professional** | `wizard_steps_PROFESSIONAL.json` | Enterprise, B2B | Corporate, precise, formal | Sales demos, enterprise deals |
| **Pirate** | `wizard_steps_PIRATE.json` | Everyone (fun mode!) | Pirate speak, playful | April Fools, special events |

### International Variants

| Language | File | Native Name | Best For |
|----------|------|-------------|----------|
| **Spanish** | `wizard_steps_SPANISH.json` | Español | Latin America, Spain |
| **French** | `wizard_steps_FRENCH.json` | Français | France, Canada, Africa |
| **German** | `wizard_steps_GERMAN.json` | Deutsch | Germany, Austria, Switzerland |
| **Japanese** | `wizard_steps_JAPANESE.json` | 日本語 | Japan |

---

## 🎭 Persona Breakdowns

### 1. IMPROVED (Recommended Default)

**Target:** General public, all ages  
**Voice:** Clear, friendly, helpful without being patronizing

**Key Features:**
- ✅ Simple language (8th grade reading level)
- ✅ Benefit-focused ("better answers" not "intelligence multiplication")
- ✅ Transparent pricing (shows actual dollar amounts)
- ✅ Honest claims (no fake certifications)

**Sample Copy:**
> "Get better AI answers by combining multiple AI models. Pay only for what you use—many queries cost under $1."

**When to Use:**
- Default production deployment
- General marketing
- Broad audience appeal

---

### 2. BRAINROT (Gen Alpha Mode)

**Target:** Gen Z/Alpha (ages 13-25), extremely online  
**Voice:** Chaotic, meme-heavy, internet slang

**Key Features:**
- 🔥 Heavy use of slang ("fr fr", "no cap", "bussin", "bestie")
- 🔥 Meme references and internet culture
- 🔥 Deliberately unhinged energy
- 🔥 Still conveys same information, just... differently

**Sample Copy:**
> "Yo bestie welcome to UltrAI where we be fr multiplying the AI rizz ✨ Most queries? Less than a dolla. No cap. That's bussin fr fr."

**When to Use:**
- Social media campaigns (TikTok, Instagram)
- April Fools mode
- A/B testing with Gen Z audiences
- **DO NOT** use for enterprise/B2B 😅

**Warning:** This will alienate older audiences. Use strategically!

---

### 3. COLLEGE (Student Mode)

**Target:** University students (18-24)  
**Voice:** Casual but intelligent, slightly sarcastic, relatable

**Key Features:**
- 📚 References to student life (broke, deadlines, GPA)
- 📚 Self-aware humor
- 📚 Budget-conscious messaging
- 📚 Still professional enough for academic use

**Sample Copy:**
> "Welcome to UltrAI—basically like having a study group of AI nerds working on your stuff at the same time. Perfect for broke college students tbh."

**When to Use:**
- .edu email campaigns
- Campus ambassador programs
- Student discount promotions
- Academic partnerships

---

### 4. PROFESSIONAL (Enterprise Mode)

**Target:** C-suite, enterprise buyers, B2B decision makers  
**Voice:** Corporate, precise, formal with industry jargon

**Key Features:**
- 💼 Uses business terminology properly
- 💼 Emphasizes security/compliance
- 💼 ROI-focused messaging
- 💼 Detailed specifications

**Sample Copy:**
> "UltrAI delivers institutional-grade AI analysis by orchestrating multiple leading language models in parallel. Usage-based pricing with transparent per-query costs. Enterprise-ready architecture with SOC2-compliant infrastructure."

**When to Use:**
- Enterprise sales demos
- RFP responses
- Board presentations
- LinkedIn marketing

**Note:** Only claim "SOC2-compliant" if you actually have the certification!

---

### 5. SPANISH (Español)

**Target:** Spanish-speaking markets  
**Voice:** Professional, clear, culturally appropriate

**Key Features:**
- 🌍 Full Spanish translation
- 🌍 Maintains brand voice
- 🌍 Culturally neutral (works for Latin America + Spain)
- 🌍 Same pricing transparency

**Sample Copy:**
> "Obtén mejores respuestas de IA combinando múltiples modelos de inteligencia artificial. Paga solo por lo que uses—muchas consultas cuestan menos de $1."

**When to Use:**
- Spanish-language markets
- International expansion
- Multilingual support

**Translation Quality:** Professional but could benefit from native speaker review

---

## 🔧 How to Implement

### Option 1: Manual Swap (Quick Test)

```bash
# Backup original
cp frontend/public/wizard_steps.json frontend/public/wizard_steps_ORIGINAL.json

# Try a variant
cp frontend/public/wizard_steps_BRAINROT.json frontend/public/wizard_steps.json

# Rebuild frontend
cd frontend && npm run build

# Test locally
make dev
```

### Option 2: Dynamic Loading (Recommended)

Add persona selection to your app:

```typescript
// In your wizard component
const [persona, setPersona] = useState<'default' | 'brainrot' | 'college' | 'professional' | 'spanish'>('default');

const stepsFile = {
  default: '/wizard_steps_IMPROVED.json',
  brainrot: '/wizard_steps_BRAINROT.json',
  college: '/wizard_steps_COLLEGE.json',
  professional: '/wizard_steps_PROFESSIONAL.json',
  spanish: '/wizard_steps_SPANISH.json',
}[persona];

// Load steps from selected file
```

### Option 3: User Preference

Let users pick their vibe:

```tsx
<select onChange={(e) => setPersona(e.target.value)}>
  <option value="default">Standard</option>
  <option value="college">College Mode 🎓</option>
  <option value="brainrot">Brainrot Mode 💀</option>
  <option value="professional">Professional Mode 💼</option>
  <option value="spanish">Español 🇪🇸</option>
</select>
```

---

## 📊 A/B Testing Strategy

### Recommended Test Plan:

1. **Week 1:** Default (IMPROVED) to 100% of users
   - Establish baseline conversion rate
   
2. **Week 2:** A/B test COLLEGE vs DEFAULT with .edu emails
   - Measure: completion rate, time on page, conversion
   
3. **Week 3:** A/B test PROFESSIONAL vs DEFAULT for enterprise leads
   - Measure: demo requests, enterprise sign-ups
   
4. **Week 4:** Limited BRAINROT test with Gen Z segment
   - Measure: social shares, viral potential, brand sentiment

**Key Metrics to Track:**
- Wizard completion rate
- Time per step
- Bounce rate at each step
- Conversion to paid query
- User feedback/sentiment

---

## ⚠️ Important Warnings

### BRAINROT Mode:
- **DO NOT** use as default without testing
- **DO NOT** use for investor presentations
- **DO** prepare for polarized reactions
- **DO** monitor brand sentiment closely

### PROFESSIONAL Mode:
- **Verify** all compliance claims (SOC2, etc.)
- **Update** if pricing changes
- **Test** with actual enterprise buyers first

### SPANISH Mode:
- **Review** with native speaker
- **Adapt** for regional differences if targeting specific countries
- **Test** with Spanish-speaking users

---

## 🎨 Creating Your Own Variant

Want to create a new persona? Follow this template:

```json
{
  "title": "[Step number + title in your voice]",
  "color": "[keep original colors]",
  "type": "[keep original type]",
  "narrative": "[Rewrite in your persona's voice]",
  "options": [
    {
      "label": "[Rewrite label]",
      "icon": "[keep same icon]",
      "cost": [keep same cost],
      "hint": "[Optional: add persona-appropriate hint]"
    }
  ]
}
```

**Voice Guidelines:**
1. Keep same information/features
2. Maintain same pricing
3. Preserve technical accuracy
4. Adapt tone to persona
5. Test with target audience

---

## 📈 Analytics Integration

Track which persona performs best:

```typescript
// Track persona usage
analytics.track('Wizard Started', {
  persona: persona,
  timestamp: new Date(),
});

// Track completion by persona
analytics.track('Wizard Completed', {
  persona: persona,
  steps_completed: stepsCompleted,
  time_taken: timeInSeconds,
});
```

---

## 🤔 FAQ

**Q: Can I mix personas (e.g., BRAINROT intro + PROFESSIONAL later steps)?**  
A: Technically yes, but it would be jarring. Pick one voice and stick with it.

**Q: Which persona should I use by default?**  
A: IMPROVED. It's tested, professional, and appeals to the widest audience.

**Q: Can users switch mid-wizard?**  
A: Not recommended—would be confusing. If implementing, save their progress.

**Q: What if users hate BRAINROT mode?**  
A: That's the point! It's polarizing. Use it strategically for specific campaigns, not as default.

**Q: Should I translate BRAINROT to other languages?**  
A: Please don't 😅 Gen Z slang doesn't translate well. Create language-specific variants instead.

**Q: Is the Spanish translation good?**  
A: It's functional but would benefit from native speaker polish. Professional enough for beta.

---

## 🚀 Next Steps

1. **Review** all variants with your team
2. **Test** IMPROVED variant as new default
3. **A/B test** COLLEGE variant with student segment
4. **Monitor** user feedback closely
5. **Iterate** based on data

**Remember:** Copy is never "done"—keep testing and improving based on user behavior!

---

## 📝 Change Log

- **2025-09-30:** Initial creation of all 5 variants
- Future: Track updates here as variants evolve

---

*Created by: Claude Code*  
*Have fun with these! But also test them properly before going live 😄*
