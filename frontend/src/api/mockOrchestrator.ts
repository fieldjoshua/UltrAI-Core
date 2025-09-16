// Mock Orchestrator API for demo mode
// Provides realistic simulated responses for demonstrations

import type {
  OrchestrationRequest,
  OrchestrationResponse,
  AvailableModelsResponse,
  ModelHealthResponse,
  OrchestratorStatusResponse,
} from './types';

// Error simulation configuration
const ERROR_SCENARIOS = {
  NETWORK_TIMEOUT: 'network_timeout',
  NO_MODELS_AVAILABLE: 'no_models_available',
  AUTHENTICATION_FAILURE: 'authentication_failure',
  NONE: 'none',
} as const;

type ErrorScenario = typeof ERROR_SCENARIOS[keyof typeof ERROR_SCENARIOS];

// Global error simulation state
let currentErrorScenario: ErrorScenario = ERROR_SCENARIOS.NONE;
let errorProbability = 0; // 0-1 probability of random errors

// Error simulation control functions
export function setErrorScenario(scenario: ErrorScenario): void {
  if (Object.values(ERROR_SCENARIOS).includes(scenario)) {
    currentErrorScenario = scenario;
    console.log(`Mock Orchestrator: Error scenario set to ${scenario}`);
  }
}

export function setRandomErrorProbability(probability: number): void {
  errorProbability = Math.max(0, Math.min(1, probability));
  console.log(
    `Mock Orchestrator: Random error probability set to ${errorProbability}`
  );
}

export function clearErrorSimulation(): void {
  currentErrorScenario = ERROR_SCENARIOS.NONE;
  errorProbability = 0;
  console.log('Mock Orchestrator: Error simulation cleared');
}

// Helper to check if we should simulate an error
function shouldSimulateError(): ErrorScenario | null {
  if (currentErrorScenario !== ERROR_SCENARIOS.NONE) {
    return currentErrorScenario;
  }
  if (Math.random() < errorProbability) {
    // Randomly select an error scenario
    const scenarios = [
      ERROR_SCENARIOS.NETWORK_TIMEOUT,
      ERROR_SCENARIOS.NO_MODELS_AVAILABLE,
      ERROR_SCENARIOS.AUTHENTICATION_FAILURE,
    ];
    return scenarios[Math.floor(Math.random() * scenarios.length)];
  }
  return null;
}

// Simulate network timeout
async function simulateNetworkTimeout(): Promise<never> {
  // Wait for a realistic timeout period
  await new Promise(resolve => setTimeout(resolve, 30000)); // 30 second timeout
  throw new Error('Network timeout: Request took too long to complete');
}

// Simulate authentication failure
function simulateAuthenticationFailure(): never {
  const error: any = new Error('Authentication failed');
  error.status = 401;
  error.response = {
    status: 401,
    statusText: 'Unauthorized',
    json: async () => ({
      detail: 'Invalid or expired authentication token',
      error_code: 'AUTH_FAILED',
    }),
  };
  throw error;
}

// Simulate no models available
function simulateNoModelsAvailable(): never {
  const error: any = new Error('No models available');
  error.status = 503;
  error.response = {
    status: 503,
    statusText: 'Service Unavailable',
    json: async () => ({
      detail:
        'No AI models are currently available. All providers are experiencing issues.',
      error_code: 'NO_MODELS_AVAILABLE',
      available_models: [],
    }),
  };
  throw error;
}

const DEMO_MODELS = [
  { id: 'gpt-5', provider: 'openai', cost_per_1k_tokens: 0.006 },
  { id: 'claude-4.1', provider: 'anthropic', cost_per_1k_tokens: 0.004 },
  { id: 'gemini-2.5', provider: 'google', cost_per_1k_tokens: 0.0045 },
  // Additional demo models remain available
  { id: 'gpt-4o-mini', provider: 'openai', cost_per_1k_tokens: 0.00015 },
  {
    id: 'claude-3-haiku-20240307',
    provider: 'anthropic',
    cost_per_1k_tokens: 0.00025,
  },
  { id: 'gemini-1.5-flash', provider: 'google', cost_per_1k_tokens: 0.00035 },
  {
    id: 'llama-3.1-70b-versatile',
    provider: 'groq',
    cost_per_1k_tokens: 0.00059,
  },
  { id: 'mixtral-8x7b-32768', provider: 'groq', cost_per_1k_tokens: 0.00024 },
];

// Simulate different types of responses based on query patterns
const generateDemoResponse = (query: string, models: string[]): string => {
  const lowerQuery = query.toLowerCase();

  // Detect query type and generate appropriate response
  if (
    lowerQuery.includes('angel investor') ||
    lowerQuery.includes('top 10 angel')
  ) {
    return generateAngelInvestorResponse(query, models);
  } else if (
    lowerQuery.includes('code') ||
    lowerQuery.includes('program') ||
    lowerQuery.includes('function')
  ) {
    return generateCodeResponse(query, models);
  } else if (lowerQuery.includes('analyze') || lowerQuery.includes('compare')) {
    return generateAnalysisResponse(query, models);
  } else if (
    lowerQuery.includes('creative') ||
    lowerQuery.includes('story') ||
    lowerQuery.includes('write')
  ) {
    return generateCreativeResponse(query, models);
  } else if (
    lowerQuery.includes('explain') ||
    lowerQuery.includes('how') ||
    lowerQuery.includes('what')
  ) {
    return generateExplanationResponse(query, models);
  } else {
    return generateGeneralResponse(query, models);
  }
};

const generateCodeResponse = (query: string, models: string[]): string => {
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

const generateAnalysisResponse = (query: string, models: string[]): string => {
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

const generateCreativeResponse = (query: string, models: string[]): string => {
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

const generateExplanationResponse = (query: string, models: string[]): string => {
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

const generateAngelInvestorResponse = (query: string, models: string[]): string => {
  // Return the actual Claude response from the CSV file
  return `Based on my research, here are the Top 10 Angel Investors most likely to fund your AI portal with democratizing features and campus-based P2P marketing:

1. **Nat Friedman**
   Contact: n***@gmail.com (available via RocketReach)
   Reasoning: Co-founded AI Grant and has the largest AI angel portfolio with 138 investments. Former GitHub CEO with deep developer community understanding. Actively invested in AI infrastructure and democratization through AI Grant program. Perfect fit for developer-focused AI tools.

2. **Sam Altman**
   Contact: sam@openai.com or through OpenAI Startup Fund
   Reasoning: OpenAI CEO with 168+ angel investments focused on AI accessibility. Believes in democratizing AI through affordable access models. Previously led Y Combinator and has extensive student/campus network connections. Ideal for scalable AI democratization plays.

3. **Reid Hoffman**
   Contact: rhoffman@greylock.com
   Reasoning: LinkedIn founder and Greylock partner with 37+ AI investments. Champions AI democratization and wrote extensively about "AI benefiting humanity." Strong track record with network effect businesses and educational platforms. Excellent fit for AI platform with viral campus distribution.

4. **Naval Ravikant**
   Contact: naval@angellist.com or through AngelList Syndicate
   Reasoning: AngelList founder who literally built the infrastructure for democratizing startup investing. 131 investments with focus on platforms that increase accessibility. Strong belief in technology democratization and reducing barriers to entry. Perfect alignment with accessibility mission.

5. **Jason Calacanis**
   Contact: jmc@launch.co
   Reasoning: LAUNCH founder who invests in 100+ startups annually with focus on education and accessibility. Runs Founder University and Angel University programs targeting students. Deep campus connections and pay-as-you-go business model expertise. Ideal for campus-based P2P marketing model.

6. **Elad Gil**
   Contact: Available through blog.eladgil.com contact form
   Reasoning: Solo VC with 296 investments including early AI companies like Perplexity, Character.AI, Harvey. Focus on AI infrastructure and tools that democratize access to advanced capabilities. Strong track record with B2B AI platforms serving diverse user bases. Perfect for AI infrastructure democratization.

7. **Fabrice Grinda**
   Contact: fabrice@fjlabs.com or fabrice@grinda.org
   Reasoning: FJ Labs founder with 1000+ investments focused on marketplaces that democratize access. Strong thesis on platforms connecting underserved users to premium services. Extensive experience with pay-as-you-go and accessibility models. Excellent fit for democratizing premium AI access.

8. **Dharmesh Shah**
   Contact: dharmesh@hubspot.com
   Reasoning: HubSpot co-founder and CTO with $140M+ invested in AI startups. Created ChatSpot AI and focuses on making technology accessible to non-technical users. Strong believer in freemium and bottom-up SaaS adoption. Ideal for AI tools with campus-first go-to-market.

9. **Alexandr Wang**
   Contact: alex@scale.com
   Reasoning: Scale AI founder (age 27) who understands student/young founder dynamics. Built $7.3B company democratizing AI data labeling. Active angel investor in AI infrastructure and tools. Perfect for understanding campus distribution and young user adoption patterns.

10. **Lachy Groom**
   Contact: hello@lachy.com
   Reasoning: Former Stripe exec turned prolific angel with 200+ investments. Focus on developer tools and API-first businesses with usage-based pricing. Strong track record with bottom-up SaaS and PLG models. Ideal match for pay-as-you-go AI platform with student ambassadors.

**Key Insights:**
- Warm introductions dramatically increase response rates (10-50x higher than cold outreach)
- Use university alumni networks and LinkedIn to find mutual connections
- Lead with traction metrics: student ambassadors signed up, campuses covered, early usage data
- Emphasize the network effects of your P2P campus distribution model
- Highlight pay-as-you-go accessibility vs expensive enterprise AI subscriptions

**Pro tip:** Start with investors who have portfolios in both AI/ML and education/campus markets. They'll immediately understand your distribution advantage.`;
};

const generateGeneralResponse = (query: string, models: string[]): string => {
  // Extract key terms from query for more relevant response
  const queryTerms = query
    .toLowerCase()
    .split(' ')
    .filter(word => word.length > 3);
  const topic = queryTerms.length > 0 ? queryTerms.join(' ') : 'your inquiry';

  return `# Ultra Synthesis™ Analysis Report

## Query Analysis
**Original Query:** "${query}"
**Processing Time:** ${(12.5 + Math.random() * 5).toFixed(2)} seconds
**Models Engaged:** ${models.length} specialized AI systems

---

## 🧠 Intelligence Multiplication Results

### Stage 1: Initial Model Responses (Parallel Processing)
${models
  .map(
    (model, i) => `
**${model}** (${(1.2 + Math.random()).toFixed(2)}s):
- Primary insight: Identified ${3 + i} key factors related to ${topic}
- Confidence: ${(85 + Math.random() * 10).toFixed(1)}%
- Unique perspective: ${
      model.includes('gpt')
        ? 'Comprehensive analysis with strong general knowledge'
        : model.includes('claude')
          ? 'Nuanced understanding with ethical considerations'
          : model.includes('gemini')
            ? 'Technical depth with multimodal insights'
            : 'Specialized domain expertise with efficient processing'
    }`
  )
  .join('\n')}

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
export async function processWithFeatherOrchestration(
  request: OrchestrationRequest
): Promise<OrchestrationResponse> {
  const orchestrationStartTime = Date.now();
  const { prompt, models = null, pattern = 'comparative' } = request;
  
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

  // If a demo dataset is available, return it directly to reflect manual UltrAI search
  try {
    const demoRes = await fetch('/demo/ultrai_demo.json', {
      cache: 'no-store',
    });
    if (demoRes.ok) {
      const demo = await demoRes.json();
      return {
        status: 'success',
        ultra_response: demo.ultra_response,
        models_used: demo.models_used || [
          'gpt-4o',
          'claude-3-5-sonnet-20241022',
          'gemini-1.5-pro',
        ],
        processing_time: 2.5,
        pattern_used: pattern,
        initial_responses: {},
        meta_analysis: {
          content: 'Loaded curated demo dataset',
          patterns: ['curated'],
          confidence: 0.99,
        },
        ultra_synthesis: {
          content: demo.ultra_response,
          confidence: 0.99,
          synthesis_method: 'curated_demo',
        },
      };
    }
  } catch (e) {
    // Fallback to generated mock if demo file missing
  }

  // Stage 1: Initialize providers & health check (2-5s)
  await new Promise(resolve =>
    setTimeout(resolve, 2000 + Math.random() * 3000)
  );

  // Use provided models or select defaults
  let selectedModels = models || [
    'gpt-4o',
    'claude-3-5-sonnet-20241022',
    'gemini-1.5-pro',
  ];

  // Ensure at least 2 models for Ultra Synthesis
  if (selectedModels.length < 2) {
    console.warn(
      'Less than 2 models selected, adding defaults for Ultra Synthesis'
    );
    selectedModels = ['gpt-4o', 'claude-3-5-sonnet-20241022'];
  }

  // Stage 2: Query dispatch (0.3-0.8s)
  await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 500));

  // Stage 3: Model generation in parallel (8-15s for slowest)
  const initialResponses: Record<string, any> = {};

  // Simulate parallel processing - all models work simultaneously
  const modelPromises = selectedModels.map(async model => {
    // Each model has different response times
    const modelDelay = model.includes('gpt-5')
      ? 8000 + Math.random() * 7000 // GPT-5: 8-15s
      : model.includes('claude-4.1')
        ? 6000 + Math.random() * 6000 // Claude: 6-12s
        : model.includes('gemini')
          ? 6000 + Math.random() * 4000 // Gemini: 6-10s
          : 5000 + Math.random() * 5000; // Others: 5-10s

    await new Promise(resolve => setTimeout(resolve, modelDelay));

    initialResponses[model] = {
      content: `[${model}] Initial analysis of: "${prompt.slice(0, 50)}..."`,
      processingTime: modelDelay / 1000,
      confidence: 0.85 + Math.random() * 0.15,
    };
  });

  // Wait for all models to complete (parallel execution)
  await Promise.all(modelPromises);

  // Stage 4: Cross-check & fan-out (2-5s)
  await new Promise(resolve =>
    setTimeout(resolve, 2000 + Math.random() * 3000)
  );

  // Stage 5: Critique & revision loop (5-20s total for 1-2 passes)
  const revisionPasses = Math.random() < 0.7 ? 1 : 2; // 70% chance of 1 pass, 30% chance of 2
  for (let pass = 0; pass < revisionPasses; pass++) {
    await new Promise(resolve =>
      setTimeout(resolve, 5000 + Math.random() * 5000)
    );
  }

  // Stage 6: Meta-draft assembly (2-4s)
  await new Promise(resolve =>
    setTimeout(resolve, 2000 + Math.random() * 2000)
  );

  // Stage 7: Meta-analysis & synthesis (6-12s)
  await new Promise(resolve =>
    setTimeout(resolve, 6000 + Math.random() * 6000)
  );
  const metaAnalysis = {
    content: `Meta-analysis identified ${Object.keys(initialResponses).length} key patterns across models with 92% consensus rate.`,
    patterns: ['consensus', 'divergence', 'synthesis'],
    confidence: 0.91,
  };

  // Stage 8: Final formatting & delivery (4-8s)
  await new Promise(resolve =>
    setTimeout(resolve, 4000 + Math.random() * 4000)
  );
  const ultraResponse = generateDemoResponse(prompt, selectedModels);

  // Add network/rate-limit jitter (1-3s)
  await new Promise(resolve =>
    setTimeout(resolve, 1000 + Math.random() * 2000)
  );

  return {
    status: 'success',
    ultra_response: ultraResponse,
    models_used: selectedModels,
    processing_time: (Date.now() - orchestrationStartTime) / 1000, // Actual elapsed time
    pattern_used: pattern,
    initial_responses: initialResponses,
    meta_analysis: metaAnalysis,
    ultra_synthesis: {
      content: ultraResponse,
      confidence: 0.94,
      synthesis_method: 'advanced_orchestration',
    },
  };
}

export async function getAvailableModels(): Promise<AvailableModelsResponse> {
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
        } as any;
      case ERROR_SCENARIOS.AUTHENTICATION_FAILURE:
        simulateAuthenticationFailure();
        break;
    }
  }

  // Simulate network delay (slower)
  await new Promise(resolve => setTimeout(resolve, 1000));

  return {
    models: DEMO_MODELS.map(m => m.id),
  } as any;
}

export async function getModelHealth(): Promise<ModelHealthResponse> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 500));

  return {
    models: DEMO_MODELS.reduce((acc: any, model) => {
      acc[model.id] = {
        status: 'healthy',
        latency_ms: 200 + Math.random() * 300,
        success_rate: 0.95 + Math.random() * 0.05,
        last_check: new Date().toISOString(),
      };
      return acc;
    }, {}),
    overall_health: 'healthy',
    healthy_models: DEMO_MODELS.length,
    total_models: DEMO_MODELS.length,
  };
}

export async function getOrchestratorStatus(): Promise<OrchestratorStatusResponse> {
  // Simulate network delay
  await new Promise(resolve => setTimeout(resolve, 300));

  return {
    status: 'operational',
    version: '1.0.0',
    uptime_seconds: 86400,
    total_requests: 1234,
    success_rate: 0.98,
    average_latency_ms: 450,
    active_models: DEMO_MODELS.length,
    queue_size: 0,
    last_error: null,
  };
}

export async function checkModelStatus(modelId: string): Promise<{ 
  available: boolean; 
  status: string; 
  error?: string;
  lastChecked?: string;
}> {
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
          error: 'No models are currently available',
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
    status: unavailableModels.includes(modelId)
      ? 'temporarily_unavailable'
      : 'ready',
    lastChecked: new Date().toISOString(),
  };
}

// Export error scenarios for testing
export { ERROR_SCENARIOS };

// Utility function for testing error scenarios
export function simulateError(scenario: string, duration?: number): void {
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
  } else if (Object.values(ERROR_SCENARIOS).includes(scenario as ErrorScenario)) {
    setErrorScenario(scenario as ErrorScenario);
    console.log(`Mock Orchestrator: Simulating ${scenario} errors`);

    if (duration) {
      setTimeout(() => {
        clearErrorSimulation();
        console.log(
          `Mock Orchestrator: ${scenario} simulation ended after timeout`
        );
      }, duration);
    }
  } else {
    console.error(`Mock Orchestrator: Unknown error scenario "${scenario}"`);
  }
}

// Window-level access for browser console testing
if (typeof window !== 'undefined') {
  (window as any).mockOrchestratorErrors = {
    simulateError,
    clearErrorSimulation,
    setErrorScenario,
    setRandomErrorProbability,
    scenarios: ERROR_SCENARIOS,
  };
}