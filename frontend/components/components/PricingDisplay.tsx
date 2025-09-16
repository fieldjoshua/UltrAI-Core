'use client';

import React from 'react';
import { useState, useEffect } from 'react';
import { Feather, DollarSign, Award } from 'lucide-react';
import { motion } from 'framer-motion';

// Define component styling
const styles = {
  container: 'flex items-center gap-2',
  featherIcon: (isPremium: boolean) =>
    `w-5 h-5 ${isPremium ? 'text-amber-400' : 'text-gray-400'}`,
  priceBadge: 'flex items-center',
  priceText: 'text-lg font-medium text-cyan-300',
  premiumBadge: 'flex items-center ml-1',
  premiumText: 'text-xs text-amber-300',
  detailsText: 'text-xs text-gray-400 mt-1',
};

type ModelPricing = {
  input: number;
  output: number;
  context: number;
};

type PricingDisplayProps = {
  selectedModels: string[];
  estimatedInputTokens?: number;
  estimatedOutputTokens?: number;
  promptText?: string; // Actual prompt text to analyze complexity
  attachments?: File[]; // Any attached documents
  analysisType?: string; // The selected analysis pattern
  showDetails?: boolean;
  className?: string;
  addonCost?: number; // New prop for addon costs
};

// Analysis patterns with complexity multipliers
const ANALYSIS_COMPLEXITY: Record<string, number> = {
  confidence: 1.0, // Base complexity
  critique: 1.25, // More complex, requires cross-model analysis
  gut: 0.9, // Simple gut check, less intensive
  fact_check: 1.35, // Very intensive fact verification
  perspective: 1.2, // Multiple viewpoints analysis
  scenario: 1.5, // Most complex - exploring future scenarios
};

const MODEL_PRICING: Record<string, ModelPricing> = {
  // OpenAI models
  'gpt-4-8k': { input: 0.03, output: 0.06, context: 8000 },
  'gpt-4-32k': { input: 0.06, output: 0.12, context: 32000 },
  'gpt-4.5-128k': { input: 0.075, output: 0.15, context: 128000 },
  'gpt-4-turbo': { input: 0.01, output: 0.03, context: 128000 },
  'gpt-4o': { input: 0.005, output: 0.015, context: 128000 },
  'gpt-4o-mini': { input: 0.00015, output: 0.0006, context: 128000 },
  'gpt-3.5-4k': { input: 0.0015, output: 0.002, context: 4000 },
  'gpt-3.5-16k': { input: 0.0005, output: 0.0015, context: 16000 },

  // Claude models
  'claude-instant': { input: 0.0008, output: 0.0024, context: 9000 },
  'claude-2-100k': { input: 0.008, output: 0.024, context: 100000 },
  'claude-2.1': { input: 0.008, output: 0.024, context: 100000 },
  'claude-3.5-sonnet': { input: 0.003, output: 0.015, context: 128000 },
  'claude-3-opus': { input: 0.015, output: 0.075, context: 128000 },

  // Google models
  'gemini-1.0-pro': { input: 0.0005, output: 0.0015, context: 128000 },
  'gemini-1.5-pro': { input: 0.0035, output: 0.0105, context: 128000 },
  'gemini-2.0-flash': { input: 0.0001, output: 0.0004, context: 1000000 },

  // Anthropic models via Bedrock
  'anthropic-claude-3-haiku': {
    input: 0.00025,
    output: 0.00125,
    context: 128000,
  },
  'anthropic-claude-3-sonnet': { input: 0.003, output: 0.015, context: 128000 },
  'anthropic-claude-3-opus': { input: 0.015, output: 0.075, context: 200000 },

  // Cohere models
  'cohere-command-r': { input: 0.0005, output: 0.0015, context: 128000 },
  'cohere-command-r-plus': { input: 0.003, output: 0.015, context: 128000 },

  // AI21 models
  'ai21-jamba-1.5-mini': { input: 0.0002, output: 0.0004, context: 4000 },
  'ai21-jamba-1.5-large': { input: 0.002, output: 0.008, context: 8000 },

  // Mistral models
  'mistral-large': { input: 0.0008, output: 0.0024, context: 32000 },
  'mistral-small': { input: 0.0002, output: 0.0006, context: 32000 },
  'mistral-medium': { input: 0.0006, output: 0.0018, context: 32000 },

  // Open source models
  'llama-2-13b': { input: 0.00075, output: 0.001, context: 4096 },
  'llama-2-70b': { input: 0.00195, output: 0.00256, context: 4096 },
  'llama-3-8b': { input: 0.0005, output: 0.0008, context: 8192 },
  'llama-3-70b': { input: 0.00175, output: 0.00225, context: 8192 },

  // Map to our UI options
  chatgpt: { input: 0.01, output: 0.03, context: 128000 }, // GPT-4 Turbo
  claude: { input: 0.003, output: 0.015, context: 128000 }, // Claude 3.5 Sonnet
  gemini: { input: 0.0035, output: 0.0105, context: 128000 }, // Gemini 1.5 Pro
  llama: { input: 0.0001, output: 0.0004, context: 128000 }, // Lowest tier

  // Special Ultra combinations (for multi-model scenarios)
  'ultra-basic': { input: 0.001, output: 0.003, context: 128000 }, // Economy tier
  'ultra-standard': { input: 0.007, output: 0.021, context: 128000 }, // Standard tier
  'ultra-premium': { input: 0.02, output: 0.06, context: 128000 }, // Premium tier
};

// Default values for calculations
const DEFAULT_INPUT_TOKENS = 800;
const DEFAULT_OUTPUT_TOKENS = 1200;
const TOKEN_RATIO_PER_CHAR = 0.25; // Approx. chars per token
const ATTACHMENT_TOKEN_PER_KB = 2.5; // Estimated tokens per KB of attachment

export const PricingDisplay = ({
  selectedModels,
  estimatedInputTokens,
  estimatedOutputTokens,
  promptText = '',
  attachments = [],
  analysisType = 'confidence',
  showDetails = false,
  className = '',
  addonCost = 0, // Default to 0 if not provided
}: PricingDisplayProps) => {
  const [totalCost, setTotalCost] = useState<number>(0);
  const [isPremium, setIsPremium] = useState<boolean>(false);
  const [effectiveInputTokens, setEffectiveInputTokens] =
    useState<number>(DEFAULT_INPUT_TOKENS);
  const [effectiveOutputTokens, setEffectiveOutputTokens] = useState<number>(
    DEFAULT_OUTPUT_TOKENS
  );

  // Calculate token estimates based on prompt and attachments
  useEffect(() => {
    // Start with default or provided values
    let inputTokens = estimatedInputTokens || DEFAULT_INPUT_TOKENS;
    let outputTokens = estimatedOutputTokens || DEFAULT_OUTPUT_TOKENS;

    // Adjust based on prompt length if provided
    if (promptText) {
      const promptLength = promptText.length;
      inputTokens = Math.max(
        inputTokens,
        Math.ceil(promptLength * TOKEN_RATIO_PER_CHAR)
      );

      // Longer prompts generally produce longer responses
      const promptComplexityFactor = Math.min(
        2.0,
        1.0 + (promptLength / 1000) * 0.25
      );
      outputTokens = Math.ceil(outputTokens * promptComplexityFactor);
    }

    // Add tokens for each attachment
    if (attachments && attachments.length > 0) {
      let totalAttachmentSizeKB = 0;

      for (const file of attachments) {
        totalAttachmentSizeKB += file.size / 1024; // Convert bytes to KB
      }

      // Calculate approximate tokens for attachments and add to input tokens
      const attachmentTokens = Math.ceil(
        totalAttachmentSizeKB * ATTACHMENT_TOKEN_PER_KB
      );
      inputTokens += attachmentTokens;

      // Attachments also increase output token count as LLMs need to process and reference them
      outputTokens += Math.ceil(attachmentTokens * 0.3); // 30% of attachment tokens impact output
    }

    // Apply complexity multiplier based on analysis type
    const complexityMultiplier = ANALYSIS_COMPLEXITY[analysisType] || 1.0;
    outputTokens = Math.ceil(outputTokens * complexityMultiplier);

    // Set the calculated values
    setEffectiveInputTokens(inputTokens);
    setEffectiveOutputTokens(outputTokens);
  }, [
    promptText,
    attachments,
    analysisType,
    estimatedInputTokens,
    estimatedOutputTokens,
  ]);

  // Calculate total cost based on all factors
  useEffect(() => {
    // Calculate total cost based on selected models and estimated tokens
    let cost = 0;
    let hasPremiumModel = false;

    // Calculate model-specific costs
    selectedModels.forEach(modelId => {
      const pricing = MODEL_PRICING[modelId];
      if (!pricing) return;

      const inputCost = (effectiveInputTokens / 1000) * pricing.input;
      const outputCost = (effectiveOutputTokens / 1000) * pricing.output;
      cost += inputCost + outputCost;

      // Check if this is a premium model (over certain threshold)
      if (pricing.input > 0.01 || pricing.output > 0.03) {
        hasPremiumModel = true;
      }
    });

    // Apply analysis complexity as a final multiplier if using premium models
    if (hasPremiumModel && analysisType) {
      const complexityMultiplier = ANALYSIS_COMPLEXITY[analysisType] || 1.0;
      cost *= complexityMultiplier;
    }

    // Add addon costs
    cost += addonCost;

    setTotalCost(cost);
    setIsPremium(hasPremiumModel || addonCost > 0.1); // Premium if using premium models or expensive addons
  }, [
    selectedModels,
    effectiveInputTokens,
    effectiveOutputTokens,
    analysisType,
    addonCost,
  ]);

  // Format the cost with appropriate precision
  const formattedCost =
    totalCost < 0.01 ? totalCost.toFixed(5) : totalCost.toFixed(2);

  // Calculate tokens summary text
  const getTokensSummary = () => {
    const baseText = `Based on ~${effectiveInputTokens} input + ~${effectiveOutputTokens} output tokens`;

    const factors = [];
    if (promptText && promptText.length > 100)
      factors.push('prompt complexity');
    if (attachments && attachments.length > 0)
      factors.push(`${attachments.length} attachment(s)`);
    if (analysisType && analysisType !== 'confidence')
      factors.push(`${analysisType} analysis`);
    if (addonCost > 0) factors.push('add-ons');

    return factors.length > 0
      ? `${baseText} • Includes: ${factors.join(', ')}`
      : baseText;
  };

  return (
    <div className={`${styles.container} ${className}`}>
      <motion.div
        initial={{ rotate: -10, opacity: 0 }}
        animate={{ rotate: isPremium ? [0, 5, 0] : 0, opacity: 1 }}
        transition={{ duration: 0.5, type: 'spring' }}
        className="relative"
      >
        <Feather
          className={styles.featherIcon(isPremium)}
          strokeWidth={isPremium ? 2.5 : 1.5}
        />
        {isPremium && (
          <motion.div
            className="absolute -top-1 -right-1 w-2 h-2 bg-amber-300 rounded-full"
            animate={{ scale: [1, 1.5, 1] }}
            transition={{ repeat: Infinity, duration: 2 }}
          />
        )}
      </motion.div>

      <div className={styles.priceBadge}>
        <DollarSign className="w-4 h-4 text-cyan-400" />
        <span className={styles.priceText}>{formattedCost}</span>
      </div>

      {isPremium && (
        <div className={styles.premiumBadge}>
          <Award className="w-4 h-4 text-amber-400 mr-1" />
          <span className={styles.premiumText}>Premium</span>
        </div>
      )}

      {showDetails && (
        <div className={styles.detailsText}>{getTokensSummary()}</div>
      )}
    </div>
  );
};
