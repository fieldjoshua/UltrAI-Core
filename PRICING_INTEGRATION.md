# Pricing Integration Guide

## Overview
This document describes how to integrate pricing, billing, and token usage tracking functionality into the Ultra AI orchestration system. The core application is designed to work without these features, allowing for flexible integration by domain experts.

## Current State
The application currently uses mock implementations for financial features:
- `TransactionService` returns mock balances and transaction history
- Token usage is tracked but not priced
- No budget enforcement is implemented

## Integration Points

### 1. Token Usage Tracking
The system already tracks token usage in multiple places:
- `app/services/llm_adapters.py` - Each adapter returns token counts
- `app/services/telemetry_service.py` - Records token usage metrics
- `app/routes/orchestrator_minimal.py` - Aggregates tokens in responses

**Integration needed:**
- Convert token counts to costs based on provider pricing
- Store usage history for billing

### 2. Cost Calculation Service
Create a service implementing the `PricingServiceInterface`:
```python
# app/services/interfaces/pricing_service_interface.py
class PricingServiceInterface(ABC):
    async def calculate_cost(self, tokens: Dict[str, int], model: str) -> float
    async def get_model_pricing(self, model: str) -> Dict[str, float]
    async def estimate_cost(self, prompt: str, model: str) -> float
```

### 3. Budget Management
Implement budget checking and enforcement:
```python
# app/services/interfaces/budget_service_interface.py
class BudgetServiceInterface(ABC):
    async def check_budget(self, user_id: str, estimated_cost: float) -> bool
    async def deduct_from_budget(self, user_id: str, amount: float) -> bool
    async def get_remaining_budget(self, user_id: str) -> float
```

### 4. Billing Integration
Connect to payment processors and billing systems:
```python
# app/services/interfaces/billing_service_interface.py
class BillingServiceInterface(ABC):
    async def create_invoice(self, user_id: str, amount: float) -> str
    async def process_payment(self, invoice_id: str, payment_method: str) -> bool
    async def get_billing_history(self, user_id: str) -> List[Invoice]
```

## Database Schema Requirements

### Tables Needed
1. **token_usage**
   - user_id (FK)
   - model
   - prompt_tokens
   - completion_tokens
   - cost
   - timestamp

2. **user_budgets**
   - user_id (FK)
   - monthly_limit
   - current_usage
   - reset_date

3. **pricing_models**
   - model_name
   - provider
   - prompt_token_price
   - completion_token_price
   - effective_date

4. **invoices**
   - invoice_id
   - user_id (FK)
   - amount
   - status
   - created_at
   - paid_at

## Configuration Flags
The following environment variables control pricing features:
- `ENABLE_PRICING` - Enable/disable cost calculation
- `ENABLE_BUDGET_ENFORCEMENT` - Enable/disable budget checks
- `ENABLE_BILLING` - Enable/disable billing integration
- `DEFAULT_MONTHLY_BUDGET` - Default budget for new users
- `PRICING_UPDATE_INTERVAL` - How often to refresh pricing data

## Implementation Steps

### Phase 1: Basic Cost Tracking
1. Implement `PricingService` with hardcoded prices
2. Add cost calculation to orchestration responses
3. Store token usage in database
4. Add cost display to UI

### Phase 2: Budget Management
1. Implement `BudgetService`
2. Add budget checks before orchestration
3. Create budget management UI
4. Add budget alerts and notifications

### Phase 3: Billing Integration
1. Choose payment processor (Stripe, PayPal, etc.)
2. Implement `BillingService`
3. Add payment methods UI
4. Create invoice generation
5. Implement subscription management

## Testing Strategy

### Unit Tests
- Mock pricing calculations
- Test budget enforcement logic
- Validate cost aggregation

### Integration Tests
- Test with real database
- Verify transaction atomicity
- Test payment processor webhooks

### Load Tests
- Verify performance with high-volume token tracking
- Test concurrent budget checks
- Validate billing under load

## Security Considerations

1. **PCI Compliance** - Never store credit card data
2. **Audit Trail** - Log all financial transactions
3. **Rate Limiting** - Prevent abuse of free tiers
4. **Encryption** - Encrypt sensitive billing data
5. **Access Control** - Restrict financial data access

## API Endpoints to Add

```python
# Pricing endpoints
GET  /api/pricing/models         # Get current model pricing
GET  /api/pricing/estimate       # Estimate cost for prompt

# Budget endpoints  
GET  /api/budget/status          # Get user's budget status
PUT  /api/budget/limit           # Update budget limit
GET  /api/budget/usage           # Get usage history

# Billing endpoints
GET  /api/billing/invoices       # Get invoice history
POST /api/billing/payment        # Process payment
GET  /api/billing/methods        # Get payment methods
```

## Frontend Integration

### Components Needed
1. **Cost Display** - Show estimated/actual costs
2. **Budget Meter** - Visual budget remaining
3. **Pricing Calculator** - Estimate costs before running
4. **Billing Dashboard** - Invoices and payment history
5. **Payment Form** - Add/update payment methods

## Monitoring and Alerts

### Metrics to Track
- Token usage by model/user
- Cost per request
- Budget utilization
- Payment success rate
- Pricing accuracy

### Alerts to Configure
- User approaching budget limit
- Payment failures
- Unusual usage patterns
- Pricing data staleness

## Migration Path

1. **Deploy with flags disabled** - No impact on existing users
2. **Enable cost calculation** - Show costs but don't enforce
3. **Gradual budget rollout** - Enable for new users first
4. **Full enforcement** - Enable for all users with grace period

## Support Documentation

### For Users
- How pricing works
- Understanding your bill
- Managing budgets
- Payment methods

### For Developers  
- Adding new payment processors
- Updating pricing models
- Debugging billing issues
- Financial reporting

## Contact for Implementation
If you're implementing the pricing system, please coordinate with the project maintainers to ensure compatibility and proper integration with the existing system architecture.