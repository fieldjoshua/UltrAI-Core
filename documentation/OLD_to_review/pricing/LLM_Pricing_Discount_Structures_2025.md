
# LLM Token Pricing and Discount Structures (2025)

## Commercial LLM APIs with Direct Token Purchasing

| Model (Provider) | Token Purchase Options | Discount Structures | How Discounts are Triggered | Context Window |
|------------------|------------------------|---------------------|-----------------------------|----------------|
| GPT-4 (OpenAI) | Usage-based API billing | Custom enterprise discounts only | Enterprise contracts | 8K-128K tokens |
| GPT-3.5 Turbo (OpenAI) | Usage-based API billing | None publicly available | Enterprise negotiation | 4K-16K tokens |
| OpenAI o1 (OpenAI) | Pay per token (batch/cache discounts) | 50% off Batch/Cache mode | Automatic (batch/cache usage) | 200K tokens |
| Claude 3 Opus (Anthropic) | Pay-per-token API billing | Enterprise custom discounts | Large enterprise usage contracts | 100K tokens |
| Claude 3 Sonnet (Anthropic) | Pay-per-token API billing | Enterprise discounts | Custom agreements | 100K tokens |
| Claude Instant (Haiku, Anthropic) | Pay-per-token API billing | Lowest price, minimal discount | Bundling possible for enterprise | 100K tokens |
| Command R+ (Cohere) | Usage-based API billing | Custom enterprise plans | High-volume negotiation | 128K tokens |
| Command R (Cohere) | Pay-per-use API | Enterprise custom pricing | Negotiation only | 16K-128K tokens |
| Command (Cohere) | Pay-per-use API | Legacy model, no discounts | Negotiation only | 4K tokens |
| Jurassic-2 Ultra (AI21 Labs) | Pay-per-token API | Enterprise discounts | Custom enterprise contracts | 8K tokens |

## Open-Source LLMs via Hosted Inference Providers

| Model (Provider) | Token Purchase Options | Discount Structures | How Discounts are Triggered | Context Window |
|------------------|------------------------|---------------------|-----------------------------|----------------|
| LLaMA 2 70B (Meta via HF, Azure) | Credit-based inference | No automatic discounts | Long-term commitments | 4096 tokens |
| Falcon 180B (TII via AWS, HF) | Pay-per-token | Batch discounts on AWS | Automatic for batch jobs | 2048 tokens |
| Mistral 7B (Mistral AI via HF, AWS) | Compute time billing | No discounts (low cost) | N/A | 8192 tokens |
| BLOOM 176B (BigScience via HF) | Compute-based billing | No discounts (research-focused) | N/A | 2048 tokens |
| Dolly 2.0 (Databricks via HF) | Pay-per-use | No discounts | Straight usage billing | 2048 tokens |

## Top 10 Pay-as-You-Go LLMs

1. OpenAI API (GPT-4/GPT-3.5) - Pay monthly per token, no upfront token purchase.
2. Anthropic Claude - Monthly invoicing per million tokens.
3. Azure OpenAI - Billed monthly via Azure credits, no token packs.
4. Google Vertex AI - Usage-based billing, volume discounts via cloud spend.
5. AWS Bedrock - Monthly pay-as-you-go, discounts via Batch API and commitments.
6. Cohere API - Pay-per-token monthly, free tier available.
7. AI21 Labs API - Pay-per-token monthly, enterprise discounts available.
8. IBM watsonx.ai - Monthly RU-based billing, discounts via plan upgrades.
9. Hugging Face Inference API - Monthly compute-based billing, free credits included.
10. Together AI Cloud API - Monthly credit-based pay-as-you-go billing.

## Token Pricing Systems Overview

- **Token Definition:** Unit of measure for API usage (text chunks).
- **Input vs Output Pricing:** Output generally more costly.
- **Context Window:** Larger context increases costs.
- **Billing Mechanics:** Monthly postpaid billing typical; discounts via efficient usage (e.g. batch processing).

## Future Trends (Next 12–24 months)

- Expect significant price reductions due to competition.
- Pricing shift from per-token to flat-fee/task-based models.
- Transparent enterprise volume pricing expected.
- Efficiency gains from model improvements (e.g., MoE) likely to reduce prices further.

