# Content Inventory

This document catalogs all existing documentation in the OLD_to_review directory to facilitate the migration process.

## Top-Level Documents

| File | Size | Last Modified | Key Topics | Categorization | Priority | Disposition |
|------|------|---------------|------------|----------------|----------|-------------|
| GUIDELINES.md | 9.0KB | [Date] | Documentation standards | Guidelines | High | Consolidate into Controlling_GUIDELINES.md |
| README.md | 7.3KB | [Date] | Project overview | Overview | High | Consolidate into Controlling_README.md |
| DOCUMENTATION_INDEX.md | 4.5KB | [Date] | Documentation structure | Index | Medium | Consolidate into PLANS_INDEX.md |
| PROJECT_OVERVIEW.md | 9.4KB | [Date] | Project details | Overview | High | Consolidate into Controlling_README.md |
| CORE_README.md | 2.1KB | [Date] | Core functionality | Overview | High | Consolidate into Controlling_README.md |
| AI_USAGE_GUIDE.md | 5.1KB | [Date] | AI integration | Guide | Medium | Move to AI_INTEGRATION_PLAN |
| DOCUMENTATION_GUIDE.md | 7.4KB | [Date] | Documentation standards | Guidelines | High | Consolidate into Controlling_GUIDELINES.md |
| PATTERN_ALIGNMENT.md | 8.0KB | [Date] | Analysis patterns | Technical | Medium | Move to INTELLIGENCE_MULTIPLICATION_PLAN |
| CONTENT_ORGANIZATION.md | 3.7KB | [Date] | Content structure | Guidelines | High | Consolidate into Controlling_GUIDELINES.md |
| DOCUMENTATION_STATUS.md | 3.7KB | [Date] | Progress tracking | Status | Low | Reference in PLANS_INDEX.md |
| CONSOLIDATION_PROGRESS.md | 3.3KB | [Date] | Migration progress | Status | Low | Reference in PLANS_INDEX.md |
| DOCUMENTATION_PRIORITIES.md | 5.9KB | [Date] | Priority settings | Planning | Medium | Reference in PLANS_INDEX.md |
| DOCUMENTATION_AUDIT.md | 3.7KB | [Date] | Content audit | Audit | Low | Archive |
| DOCUMENTATION_CONSOLIDATION.md | 4.4KB | [Date] | Consolidation plans | Planning | Medium | Superseded by current plan |
| README2.md | 10KB | [Date] | Additional overview | Overview | Medium | Consolidate into Controlling_README.md |

## Directories

| Directory | Contents | Priority | Disposition |
|-----------|----------|----------|-------------|
| api/ | API documentation | High | Move to API_DEVELOPMENT_PLAN |
| backend/ | Backend implementation | High | Move to BACKEND_INTEGRATION_PLAN |
| guidelines/ | Project standards | High | Consolidate into Controlling_GUIDELINES.md |
| implementation/ | Implementation details | Medium | Distribute to relevant plans |
| implementation_plans/ | Project plans | Medium | Replace with new plan structure |
| instructions/ | How-to guides | Medium | Distribute to relevant plans |
| logic/ | Core concepts | High | Move to INTELLIGENCE_MULTIPLICATION_PLAN |
| workflow/ | Process documentation | Medium | Distribute to relevant plans |
| templates/ | Document templates | High | Move to Templates/ directory |
| Standards/ | Project standards | High | Consolidate into Controlling_GUIDELINES.md |
| archive/ | Archived content | Low | Keep in OLD_to_review/archive |
| pricing/ | Pricing information | Medium | Move to PRICING_IMPLEMENTATION_PLAN |
| cloud/ | Cloud deployment | Medium | Move to CLOUD_INTEGRATION_PLAN |

## Content Relationships

### Key Dependencies

1. **Core Documentation Chain**:
   - README.md → PROJECT_OVERVIEW.md → CORE_README.md
   - These documents build on each other and should be consolidated together

2. **Guidelines Chain**:
   - GUIDELINES.md → DOCUMENTATION_GUIDE.md → CONTENT_ORGANIZATION.md
   - These establish the documentation rules and should be consolidated together

3. **Implementation References**:
   - api/ documentation references backend/ implementation
   - implementation/ details reference logic/ concepts
   - These connections must be maintained in the new structure

### Overlapping Content

1. **Documentation Standards Overlap**:
   - GUIDELINES.md, DOCUMENTATION_GUIDE.md and Standards/ contain overlapping rules
   - Need to reconcile and create a single set of standards

2. **Project Overview Overlap**:
   - README.md, PROJECT_OVERVIEW.md, and CORE_README.md contain redundant information
   - Need to create a unified project overview without duplication

## Next Steps

1. Begin detailed review of highest priority documents:
   - GUIDELINES.md, README.md, PROJECT_OVERVIEW.md
   - Create detailed outlines of content to be migrated

2. Establish Templates directory with required templates:
   - Migrate existing templates from OLD_to_review/templates/
   - Update according to new guidelines

3. Create first core plan directories based on content categorization:
   - API_DEVELOPMENT_PLAN
   - BACKEND_INTEGRATION_PLAN
   - INTELLIGENCE_MULTIPLICATION_PLAN
