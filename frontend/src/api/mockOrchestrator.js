// Mock Orchestrator API for demo mode
// Provides realistic simulated responses for demonstrations

// Error simulation configuration
const ERROR_SCENARIOS = {
  NETWORK_TIMEOUT: 'network_timeout',
  NO_MODELS_AVAILABLE: 'no_models_available',
  AUTHENTICATION_FAILURE: 'authentication_failure',
  NONE: 'none'
};

// Global error simulation state
let currentErrorScenario = ERROR_SCENARIOS.NONE;
let errorProbability = 0; // 0-1 probability of random errors

// Error simulation control functions
export function setErrorScenario(scenario) {
  if (Object.values(ERROR_SCENARIOS).includes(scenario)) {
    currentErrorScenario = scenario;
    console.log(`Mock Orchestrator: Error scenario set to ${scenario}`);
  }
}

export function setRandomErrorProbability(probability) {
  errorProbability = Math.max(0, Math.min(1, probability));
  console.log(`Mock Orchestrator: Random error probability set to ${errorProbability}`);
}

export function clearErrorSimulation() {
  currentErrorScenario = ERROR_SCENARIOS.NONE;
  errorProbability = 0;
  console.log('Mock Orchestrator: Error simulation cleared');
}

// Helper to check if we should simulate an error
function shouldSimulateError() {
  if (currentErrorScenario !== ERROR_SCENARIOS.NONE) {
    return currentErrorScenario;
  }
  if (Math.random() < errorProbability) {
    // Randomly select an error scenario
    const scenarios = [
      ERROR_SCENARIOS.NETWORK_TIMEOUT,
      ERROR_SCENARIOS.NO_MODELS_AVAILABLE,
      ERROR_SCENARIOS.AUTHENTICATION_FAILURE
    ];
    return scenarios[Math.floor(Math.random() * scenarios.length)];
  }
  return null;
}

// Simulate network timeout
async function simulateNetworkTimeout() {
  // Wait for a realistic timeout period
  await new Promise(resolve => setTimeout(resolve, 30000)); // 30 second timeout
  throw new Error('Network timeout: Request took too long to complete');
}

// Simulate authentication failure
function simulateAuthenticationFailure() {
  const error = new Error('Authentication failed');
  error.status = 401;
  error.response = {
    status: 401,
    statusText: 'Unauthorized',
    json: async () => ({
      detail: 'Invalid or expired authentication token',
      error_code: 'AUTH_FAILED'
    })
  };
  throw error;
}

// Simulate no models available
function simulateNoModelsAvailable() {
  const error = new Error('No models available');
  error.status = 503;
  error.response = {
    status: 503,
    statusText: 'Service Unavailable',
    json: async () => ({
      detail: 'No AI models are currently available. All providers are experiencing issues.',
      error_code: 'NO_MODELS_AVAILABLE',
      available_models: []
    })
  };
  throw error;
}

const DEMO_MODELS = [
  { id: 'gpt-5', provider: 'openai', cost_per_1k_tokens: 0.006 },
  { id: 'claude-4.1', provider: 'anthropic', cost_per_1k_tokens: 0.004 },
  { id: 'gemini-2.5', provider: 'google', cost_per_1k_tokens: 0.0045 },
  // Additional demo models remain available
  { id: 'gpt-4o-mini', provider: 'openai', cost_per_1k_tokens: 0.00015 },
  { id: 'claude-3-haiku-20240307', provider: 'anthropic', cost_per_1k_tokens: 0.00025 },
  { id: 'gemini-1.5-flash', provider: 'google', cost_per_1k_tokens: 0.00035 },
  { id: 'llama-3.1-70b-versatile', provider: 'groq', cost_per_1k_tokens: 0.00059 },
  { id: 'mixtral-8x7b-32768', provider: 'groq', cost_per_1k_tokens: 0.00024 },
];

// Simulate different types of responses based on query patterns
const generateDemoResponse = (query, models) => {
  const lowerQuery = query.toLowerCase();
  
  // Detect query type and generate appropriate response
  if (lowerQuery.includes('angel investor') || lowerQuery.includes('top 10 angel')) {
    return generateAngelInvestorResponse(query, models);
  } else if (lowerQuery.includes('code') || lowerQuery.includes('program') || lowerQuery.includes('function')) {
    return generateCodeResponse(query, models);
  } else if (lowerQuery.includes('analyze') || lowerQuery.includes('compare')) {
    return generateAnalysisResponse(query, models);
  } else if (lowerQuery.includes('creative') || lowerQuery.includes('story') || lowerQuery.includes('write')) {
    return generateCreativeResponse(query, models);
  } else if (lowerQuery.includes('explain') || lowerQuery.includes('how') || lowerQuery.includes('what')) {
    return generateExplanationResponse(query, models);
  } else {
    return generateGeneralResponse(query, models);
  }
};

const generateCodeResponse = (query, models) => {
  return `Based on comprehensive analysis across ${models.length} specialized AI models, here's the optimal solution:

**Code Implementation:**
\`\`\`python
def optimize_performance(data):
    """
    Multi-model consensus implementation combining best practices
    from GPT-4, Claude, and specialized coding models.
    """
    # Pre-processing optimization (GPT-4 suggestion)
    processed_data = preprocess_efficiently(data)
    
    # Core algorithm (Claude's approach)
    results = apply_advanced_algorithm(processed_data)
    
    # Post-processing refinement (Gemini enhancement)
    return finalize_with_caching(results)
\`\`\`

**Key Insights from Model Synthesis:**
1. **Performance**: All models agreed on O(n log n) complexity as optimal
2. **Memory Usage**: Consensus on streaming approach for large datasets
3. **Error Handling**: Comprehensive exception handling pattern identified
4. **Testing**: Unit test coverage recommendations from multiple perspectives

**Best Practices Identified:**
- Use type hints for better code clarity (unanimous agreement)
- Implement logging for production debugging (87% model consensus)
- Consider async implementation for I/O operations (specialized model insight)

*This synthesis leverages the unique strengths of each model to deliver production-ready code.*`;
};

const generateAnalysisResponse = (query, models) => {
  return `Through advanced multi-model orchestration, I've synthesized insights from ${models.length} leading AI systems:

**Comparative Analysis Results:**

📊 **Quantitative Findings:**
- Model Agreement Score: 94.2%
- Confidence Level: High (8.7/10)
- Analysis Depth: Comprehensive (Level 5)

🔍 **Key Discoveries:**
1. **Primary Pattern**: All models identified similar core trends with nuanced variations
2. **Unique Insights**: 
   - GPT-4: Emphasized long-term strategic implications
   - Claude: Focused on ethical considerations and edge cases
   - Gemini: Highlighted technical implementation details

📈 **Synthesized Recommendations:**
1. **Immediate Actions**: Implement the consensus approach identified by 90% of models
2. **Risk Mitigation**: Address the edge cases surfaced by specialized analysis
3. **Future Planning**: Consider the strategic roadmap suggested by pattern synthesis

**Confidence Metrics:**
- Inter-model agreement: 94.2%
- Factual consistency: 97.8%
- Novel insights generated: 12

*This Ultra Synthesis™ combines diverse AI perspectives for unparalleled analytical depth.*`;
};

const generateCreativeResponse = (query, models) => {
  return `Leveraging creative synthesis across ${models.length} AI models, here's a uniquely crafted response:

**Creative Synthesis Output:**

✨ **Opening Concept** (Collaborative ideation):
"In a world where ideas dance between digital minds, your vision takes shape through the harmonious collaboration of artificial intelligences, each contributing their unique creative signature..."

🎨 **Multi-Model Creative Elements:**
- **Narrative Arc**: Classic three-act structure with modern twists
- **Character Depth**: Psychologically complex protagonists with relatable flaws
- **World Building**: Rich, immersive environment with consistent internal logic
- **Dialogue Style**: Natural, character-specific voices that advance the plot

🌟 **Unique Creative Insights:**
1. GPT-4 contributed sophisticated metaphorical frameworks
2. Claude added emotional depth and ethical complexity
3. Gemini provided technical accuracy and scientific plausibility

**Creative Metrics:**
- Originality Score: 8.9/10
- Emotional Resonance: High
- Narrative Coherence: Excellent

*This creative fusion represents the pinnacle of AI collaboration in artistic expression.*`;
};

const generateExplanationResponse = (query, models) => {
  return `Synthesizing explanations from ${models.length} expert AI models for maximum clarity:

**Multi-Level Explanation:**

🎯 **Simple Overview** (Consensus explanation):
${query.slice(0, 50)}... can be understood as a fundamental concept that bridges multiple domains of knowledge.

📚 **Detailed Breakdown:**
1. **Core Concept**: All models agree on the fundamental principle
2. **Technical Details**: Specialized models provide domain-specific insights
3. **Practical Applications**: Real-world examples from diverse perspectives
4. **Common Misconceptions**: Clarifications based on model consensus

🔬 **Deep Dive Insights:**
- **Historical Context**: How this concept evolved over time
- **Current Understanding**: State-of-the-art knowledge synthesis
- **Future Implications**: Predictive insights from multiple models

**Understanding Metrics:**
- Clarity Score: 9.2/10
- Completeness: 96%
- Accuracy: Verified across models

*This explanation benefits from cross-model validation for maximum accuracy and clarity.*`;
};

const generateAngelInvestorResponse = (query, models) => {
  return `Here is a synthesized and fully fact-checked list of the **Top 10 Angel Investors** most likely to fund a powerful, democratizing multi-LLM AI portal—one designed for accessibility, pay-as-you-go pricing, and student-driven campus sales. This synthesis draws exclusively from the attached document but consolidates rankings, investor reasoning, and contacts for maximum clarity and accuracy, omitting any potentially misleading or unsubstantiated info.

## Top 10 Angel Investors for a Democratizing Multi-LLM AI Portal

### 1. Nat Friedman & Daniel Gross (C2 Investment Partners / AI Grant)
- **Contact:** Application at [aigrant.org], X: @natfriedman, @danielgross
- **Why Chosen:** The most prolific AI angel duo, leading both AI Grant and C2 Investments, directly responsible for many of the highest-profile AI democratization and multi-model platform investments (including Perplexity). Their approach is laser-focused on "AI for everyone" and strongly favors infrastructure + consumer AI with bottoms-up adoption—exact alignment with the product's pay-as-you-go, student-ambassador distribution model.[1]

### 2. Elad Gil
- **Contact:** Blog contact form at [eladgil.com], X: @eladgil
- **Why Chosen:** With a portfolio spanning Perplexity, Character.AI, Harvey, and Mistral, Elad Gil stands out for high-conviction support of infrastructure and product-led AI plays. He's known for democratizing access to advanced tech and favored for his strong intuition for scalable platforms, making him an ideal backer for multi-LLM businesses with practical distribution models.[1]

### 3. Naval Ravikant
- **Contact:** naval@angellist.com, AngelList syndicate, X: @naval
- **Why Chosen:** As AngelList's founder and a major advocate for democratized access, Naval is deeply aligned with missions that lower barriers to premium tools. He invests in campus P2P and network-effect businesses and his vision of "AI for everyone" precisely matches the portal's distribution and pricing mechanics.[1]

### 4. Sam Altman
- **Contact:** sam@openai.com, OpenAI Startup Fund
- **Why Chosen:** Prolific investor (160+ deals) and CEO of OpenAI, Sam Altman champions AI accessibility and signaling power. While there could be perception-of-competition risks, his demonstrated commitment to democratizing AI capabilities keeps him highly relevant for outreach.[1]

### 5. Reid Hoffman
- **Contact:** rhoffman@greylock.com
- **Why Chosen:** LinkedIn co-founder and Greylock partner, with direct board and investment experience in leading AI companies, Hoffman is regarded for his focus on network effects, distribution, and "AI for humanity" missions—strongly reinforcing the multi-LLM, student-distributed, and access-first thesis.[1]

### 6. Fabrice Grinda
- **Contact:** fabrice@fjlabs.com
- **Why Chosen:** As arguably the most prolific angel globally (1,000+ deals via FJ Labs), Fabrice has deep expertise in marketplace and distribution-centric models. Pay-as-you-go and campus-sales strategies align extremely well with his historical investment playbook and appetite for platforms that amplify under-served markets.[1]

### 7. Jason Calacanis
- **Contact:** jmc@launch.co, investmentteam@launch.co
- **Why Chosen:** Founder of LAUNCH and The Syndicate, Calacanis is hands-on in pre-seed/seed startups that emphasize accessibility and student/grassroots growth. Programs like Founder University and a track record with P2P, student-driven sales make him an ideal anchor investor for campus ambassador models.[1]

### 8. Gokul Rajaram
- **Contact:** gokulr@gmail.com
- **Why Chosen:** A "godfather" of product-led growth, Gokul is legendary for his expertise in go-to-market, distribution, and user onboarding (ex-Google, Square, DoorDash). As an angel, he loves clever sales loops and network effects—qualities foundational to the student-led P2P model described here.[1]

### 9. Scott Belsky
- **Contact:** via Adobe/Behance networks, scottbelsky.com
- **Why Chosen:** Adobe's Chief Product Officer and Behance founder, Belsky is renowned for investing in creative and democratization-centric technology. His credibility in community-building and accessibility, especially in student and creator circles, uniquely position him to recognize the high-potential of the proposed platform.[1]

### 10. Sahil Lavingia
- **Contact:** Apply at [shl.vc]
- **Why Chosen:** As Gumroad's founder and steward of a rolling fund for indie and creator-first startups, Lavingia is an expert in bottom-up pricing, PLG, and pay-as-you-go models that empower students and creators. His portfolio and thesis make him one of the strongest matches for P2P, accessibility-focused AI platforms.[1]

***

## Notable Alternatives (Just Outside Top 10)
- **Balaji Srinivasan:** Decentralized/P2P investment track, though less active currently.
- **Dharmesh Shah:** HubSpot, democratizing SaaS.
- **Andrej Karpathy:** AI signal investor, lighter as frequent check-writer.
- **Amjad Masad:** Replit, extreme alignment but sharply founder-operational.
- **Charlie Songhurst:** AI infra investor with good thesis, less visible in current rounds.[1]

***

## Key Considerations for Outreach
- The first 5 listed are highest-priority based on mission fit and accessibility patterns.
- Each contact method represents a legitimate, public-facing channel—no private or misleading contact tips are included.
- This list deliberately removes any outdated, disputed, or unsubstantiated names and prioritizes those with both precedent and clear thesis alignment.[1]

***

**This selection, blending the consensus and highest-signal points from your inputs, provides the most up-to-date, accurate, and impactful target list for outreach to angels who understand and back democratizing, multi-LLM, student-driven AI ventures.**`;
};

const generateGeneralResponse = (query, models) => {
  // Extract key terms from query for more relevant response
  const queryTerms = query.toLowerCase().split(' ').filter(word => word.length > 3);
  const topic = queryTerms.length > 0 ? queryTerms.join(' ') : 'your inquiry';
  
  return `# Ultra Synthesis™ Analysis Report

## Query Analysis
**Original Query:** "${query}"
**Processing Time:** ${(12.5 + Math.random() * 5).toFixed(2)} seconds
**Models Engaged:** ${models.length} specialized AI systems

---

## 🧠 Intelligence Multiplication Results

### Stage 1: Initial Model Responses (Parallel Processing)
${models.map((model, i) => `
**${model}** (${(1.2 + Math.random()).toFixed(2)}s):
- Primary insight: Identified ${3 + i} key factors related to ${topic}
- Confidence: ${(85 + Math.random() * 10).toFixed(1)}%
- Unique perspective: ${
  model.includes('gpt') ? 'Comprehensive analysis with strong general knowledge' :
  model.includes('claude') ? 'Nuanced understanding with ethical considerations' :
  model.includes('gemini') ? 'Technical depth with multimodal insights' :
  'Specialized domain expertise with efficient processing'
}`).join('\n')}

### Stage 2: Meta-Analysis (Cross-Model Synthesis)
🔄 **Pattern Recognition Results:**
- **Consensus Areas** (${(88 + Math.random() * 10).toFixed(1)}% agreement):
  • All models identified similar core themes around ${topic}
  • Shared understanding of fundamental principles
  • Consistent factual accuracy across responses

- **Divergence Points** (Valuable unique insights):
  • GPT models emphasized broader context and implications
  • Claude models highlighted potential edge cases and ethical dimensions
  • Gemini models provided technical implementation details
  • Open-source models offered alternative perspectives

### Stage 3: Ultra Synthesis™ (Intelligence Multiplication)

📈 **Synthesized Insights:**

1. **Core Finding** (Supported by ${models.length}/${models.length} models):
   Based on comprehensive analysis, ${topic} involves multiple interconnected factors that require careful consideration. The synthesis reveals both immediate practical applications and long-term strategic implications.

2. **Multi-Dimensional Analysis:**
   - **Technical Perspective**: Implementation requires attention to scalability, efficiency, and maintainability
   - **Strategic Perspective**: Long-term value creation through systematic approach
   - **Risk Perspective**: ${Math.floor(Math.random() * 3) + 2} potential challenges identified with mitigation strategies
   - **Opportunity Perspective**: ${Math.floor(Math.random() * 4) + 3} growth vectors discovered through cross-model insights

3. **Actionable Recommendations** (Priority-ranked):
   🥇 **Immediate Actions** (0-30 days):
   - Implement the consensus approach validated by all ${models.length} models
   - Begin with pilot testing in controlled environment
   - Establish measurement frameworks for success metrics
   
   🥈 **Short-term Initiatives** (1-3 months):
   - Scale successful patterns identified in synthesis
   - Address edge cases surfaced by specialized analysis
   - Optimize based on initial performance data
   
   🥉 **Strategic Roadmap** (3-12 months):
   - Leverage compound benefits from integrated approach
   - Expand into adjacent opportunities identified
   - Build sustainable competitive advantages

## 📊 Quality Assurance Metrics

| Metric | Score | Benchmark |
|--------|-------|-----------|
| Inter-Model Agreement | ${(92 + Math.random() * 6).toFixed(1)}% | >85% ✅ |
| Factual Consistency | ${(95 + Math.random() * 4).toFixed(1)}% | >90% ✅ |
| Novel Insights Generated | ${Math.floor(8 + Math.random() * 7)} | >5 ✅ |
| Confidence Level | ${(88 + Math.random() * 10).toFixed(1)}% | >80% ✅ |
| Comprehensiveness | ${(93 + Math.random() * 6).toFixed(1)}% | >85% ✅ |

## 🚀 Value Delivered

Through Ultra Synthesis™, you've received:
- **${models.length}x perspective multiplication** vs single model response
- **${(35 + Math.random() * 25).toFixed(0)}% more insights** through cross-model synthesis
- **${(92 + Math.random() * 7).toFixed(0)}% confidence level** through consensus validation
- **Unique discoveries** that no single model would have identified

---

*This Ultra Synthesis™ report represents the cutting edge of AI orchestration, where multiple intelligences collaborate to deliver insights beyond the capability of any single model. Each response is unique, contextual, and optimized for maximum value delivery.*

**Report ID:** US-${Date.now().toString(36).toUpperCase()}-${Math.random().toString(36).substring(2, 6).toUpperCase()}`;
};

// Mock API implementation
export async function processWithFeatherOrchestration({
  prompt,
  models = null,
  pattern = 'comparative',
  ultraModel = null,
  outputFormat = 'plain'
}) {
  // Check for error simulation
  const errorScenario = shouldSimulateError();
  if (errorScenario) {
    switch (errorScenario) {
      case ERROR_SCENARIOS.NETWORK_TIMEOUT:
        await simulateNetworkTimeout();
        break;
      case ERROR_SCENARIOS.NO_MODELS_AVAILABLE:
        simulateNoModelsAvailable();
        break;
      case ERROR_SCENARIOS.AUTHENTICATION_FAILURE:
        simulateAuthenticationFailure();
        break;
    }
  }
  
  // Simulate network delay for initial processing (10x slower)
  await new Promise(resolve => setTimeout(resolve, 20000 + Math.random() * 5000));
  
  // Use provided models or select defaults (top models)
  let selectedModels = models || ['gpt-5', 'claude-4.1', 'gemini-2.5'];
  
  // Ensure at least 2 models for Ultra Synthesis
  if (selectedModels.length < 2) {
    console.warn('Less than 2 models selected, adding defaults for Ultra Synthesis');
    selectedModels = ['gpt-4o', 'claude-3-5-sonnet-20241022'];
  }
  
  // Generate initial responses
  const initialResponses = {};
  for (const model of selectedModels) {
    // Simulate per-model delay (10x slower)
    await new Promise(resolve => setTimeout(resolve, 15000 + Math.random() * 5000));
    initialResponses[model] = {
      content: `[${model}] Initial analysis of: "${prompt.slice(0, 50)}..."`,
      processingTime: 7.5 + Math.random() * 2,
      confidence: 0.85 + Math.random() * 0.15
    };
  }
  
  // Generate meta analysis (10x slower)
  await new Promise(resolve => setTimeout(resolve, 20000 + Math.random() * 8000));
  const metaAnalysis = {
    content: `Meta-analysis identified ${Object.keys(initialResponses).length} key patterns across models with 92% consensus rate.`,
    patterns: ['consensus', 'divergence', 'synthesis'],
    confidence: 0.91
  };
  
  // Generate ultra synthesis (10x slower)
  await new Promise(resolve => setTimeout(resolve, 30000 + Math.random() * 10000));
  const ultraResponse = generateDemoResponse(prompt, selectedModels);
  
  return {
    status: 'success',
    ultra_response: ultraResponse,
    models_used: selectedModels,
    processing_time: 300 + Math.random() * 120,
    pattern_used: pattern,
    initial_responses: initialResponses,
    meta_analysis: metaAnalysis,
    ultra_synthesis: {
      content: ultraResponse,
      confidence: 0.94,
      synthesis_method: 'advanced_orchestration'
    }
  };
}

export async function getAvailableModels() {
  // Check for error simulation
  const errorScenario = shouldSimulateError();
  if (errorScenario) {
    switch (errorScenario) {
      case ERROR_SCENARIOS.NETWORK_TIMEOUT:
        await simulateNetworkTimeout();
        break;
      case ERROR_SCENARIOS.NO_MODELS_AVAILABLE:
        // For getAvailableModels, return empty list instead of throwing
        return {
          models: [],
          totalCount: 0,
          providers: {
            openai: [],
            anthropic: [],
            google: [],
            groq: [],
          },
          modelInfos: {},
          error: 'No models available'
        };
      case ERROR_SCENARIOS.AUTHENTICATION_FAILURE:
        simulateAuthenticationFailure();
        break;
    }
  }
  
  // Simulate network delay (slower)
  await new Promise(resolve => setTimeout(resolve, 1000));
  
  return {
    models: DEMO_MODELS.map(m => m.id),
    totalCount: DEMO_MODELS.length,
    providers: {
      openai: DEMO_MODELS.filter(m => m.provider === 'openai').map(m => m.id),
      anthropic: DEMO_MODELS.filter(m => m.provider === 'anthropic').map(m => m.id),
      google: DEMO_MODELS.filter(m => m.provider === 'google').map(m => m.id),
      groq: DEMO_MODELS.filter(m => m.provider === 'groq').map(m => m.id),
    },
    modelInfos: DEMO_MODELS.reduce((acc, m) => {
      acc[m.id] = { provider: m.provider, cost_per_1k_tokens: m.cost_per_1k_tokens };
      return acc;
    }, {})
  };
}

export async function checkModelStatus(modelId) {
  // Check for error simulation
  const errorScenario = shouldSimulateError();
  if (errorScenario) {
    switch (errorScenario) {
      case ERROR_SCENARIOS.NETWORK_TIMEOUT:
        await simulateNetworkTimeout();
        break;
      case ERROR_SCENARIOS.NO_MODELS_AVAILABLE:
        return {
          available: false,
          status: 'all_models_unavailable',
          lastChecked: new Date().toISOString(),
          error: 'No models are currently available'
        };
      case ERROR_SCENARIOS.AUTHENTICATION_FAILURE:
        simulateAuthenticationFailure();
        break;
    }
  }
  
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 200));
  
  // Simulate some models being temporarily unavailable
  const unavailableModels = Math.random() > 0.8 ? ['mixtral-8x7b-32768'] : [];
  
  return {
    available: !unavailableModels.includes(modelId),
    status: unavailableModels.includes(modelId) ? 'temporarily_unavailable' : 'ready',
    lastChecked: new Date().toISOString()
  };
}

// Export error scenarios for testing
export { ERROR_SCENARIOS };

// Utility function for testing error scenarios
export function simulateError(scenario, duration = null) {
  if (scenario === 'random') {
    // Enable random errors with 30% probability
    setRandomErrorProbability(0.3);
    console.log('Mock Orchestrator: Random errors enabled (30% probability)');
    
    if (duration) {
      setTimeout(() => {
        clearErrorSimulation();
        console.log('Mock Orchestrator: Random errors disabled after timeout');
      }, duration);
    }
  } else if (Object.values(ERROR_SCENARIOS).includes(scenario)) {
    setErrorScenario(scenario);
    console.log(`Mock Orchestrator: Simulating ${scenario} errors`);
    
    if (duration) {
      setTimeout(() => {
        clearErrorSimulation();
        console.log(`Mock Orchestrator: ${scenario} simulation ended after timeout`);
      }, duration);
    }
  } else {
    console.error(`Mock Orchestrator: Unknown error scenario "${scenario}"`);
  }
}

// Window-level access for browser console testing
if (typeof window !== 'undefined') {
  window.mockOrchestratorErrors = {
    simulateError,
    clearErrorSimulation,
    setErrorScenario,
    setRandomErrorProbability,
    scenarios: ERROR_SCENARIOS
  };
}