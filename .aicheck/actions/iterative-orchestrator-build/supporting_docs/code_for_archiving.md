# Code for Archiving

This document identifies specific files and code that should be archived during the Iterative Orchestrator Build process. Archiving means moving these files to an ARCHIVE directory rather than deleting them, to preserve functionality while cleaning up the codebase.

## Files to Archive

| File Path                                                                 | Destination Path                                          | Reason for Archiving                                                                                                                          |
| ------------------------------------------------------------------------- | --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| `/Users/joshuafield/Documents/Ultra/src/core/ultra_hyper.py`              | `ARCHIVE/legacy/ultra_hyper.py`                           | Original orchestrator implementation that will be replaced by the new BaseOrchestrator. Contains direct API calls rather than using adapters. |
| `/Users/joshuafield/Documents/Ultra/src/legacy/ultra_hyper.py`            | `ARCHIVE/legacy/ultra_hyper_duplicate.py`                 | Duplicate of the original implementation, kept only for backward compatibility.                                                               |
| `/Users/joshuafield/Documents/Ultra/src/orchestrator.py`                  | `ARCHIVE/legacy/orchestrator.py`                          | Simpler orchestrator implementation that lacks many features and has inconsistent interface with other components.                            |
| `/Users/joshuafield/Documents/Ultra/src/models/enhanced_orchestrator.py`  | `ARCHIVE/duplicates/src_models/enhanced_orchestrator.py`  | Duplicate implementation of EnhancedOrchestrator. The version in `backend/models/` seems to be the primary one used by API routes.            |
| `/Users/joshuafield/Documents/Ultra/backend/mock_llm_service.py`          | `ARCHIVE/duplicates/backend_mock_llm_service.py`          | One of several mock service implementations. Will be replaced by a unified mock adapter in the new structure.                                 |
| `/Users/joshuafield/Documents/Ultra/backend/services/mock_llm_service.py` | `ARCHIVE/duplicates/backend_services_mock_llm_service.py` | Duplicate mock service implementation. Will be consolidated into a single mock adapter.                                                       |

## Files to Keep with Modifications

| File Path                                                                    | Modifications Needed                                              | Reason for Keeping                                                                                                  |
| ---------------------------------------------------------------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------- |
| `/Users/joshuafield/Documents/Ultra/simple_analyzer.py`                      | Keep temporarily and gradually replace with `src/cli/analyzer.py` | Provides a simplified interface that users may have scripts referencing. The new CLI should be backward compatible. |
| `/Users/joshuafield/Documents/Ultra/backend/models/enhanced_orchestrator.py` | Refactor to use new orchestrator                                  | Currently used by the API routes through PromptService. Can be updated to proxy to the new implementation.          |
| `/Users/joshuafield/Documents/Ultra/backend/services/prompt_service.py`      | Refactor to use new orchestrator                                  | Service layer used by API routes. Should be updated to use the new orchestration service.                           |
| `/Users/joshuafield/Documents/Ultra/backend/services/llm_config_service.py`  | Refactor to use new configuration                                 | Used for model registration and configuration. Should be updated to work with the new system.                       |
| `/Users/joshuafield/Documents/Ultra/src/models/llm_adapter.py`               | Split into multiple adapter files                                 | Core adapter logic that is well-designed. Should be reorganized into the new structure with minimal changes.        |
| `/Users/joshuafield/Documents/Ultra/backend/routes/analyze_routes.py`        | Refactor to use new services                                      | API routes should be preserved but updated to use the new orchestration service.                                    |

## Code Patterns to Archive

Beyond specific files, certain code patterns should be deprecated and replaced:

1. **Direct API Calls:**

   - Pattern: Making direct API calls to LLM providers instead of using adapters
   - Example: `TriLLMOrchestrator.call_chatgpt()`, `TriLLMOrchestrator.call_gemini()`, `TriLLMOrchestrator.call_llama()`
   - Replacement: Use LLM adapters for all provider interactions

2. **Singleton Pattern for Services:**

   - Pattern: Creating global singleton instances of services
   - Example: `llm_config_service = LLMConfigService()`
   - Replacement: Use dependency injection for services

3. **Environment Variable Access in Multiple Places:**

   - Pattern: Accessing environment variables directly in many files
   - Example: `os.environ.get("OPENAI_API_KEY", "")` appearing in multiple files
   - Replacement: Centralize environment variable access in configuration service

4. **Multiple Mock Implementations:**

   - Pattern: Different approaches to mock mode across the system
   - Example: Various `MOCK_RESPONSES` dictionaries and mock handling logic
   - Replacement: Unified mock adapter with consistent interface

5. **Inconsistent Error Handling:**
   - Pattern: Different error handling approaches in different components
   - Example: Mix of try/except, retry decorators, and async error handling
   - Replacement: Consistent error handling strategy

## Directory Structure Changes

The following directories should be created for the new implementation:

```
src/orchestration/
src/adapters/
src/services/
src/cli/
ARCHIVE/legacy/
ARCHIVE/duplicates/
```

## Archive Process

1. Create the ARCHIVE directory structure
2. Move identified files to their archive locations
3. Update imports in remaining files
4. Create stub files in original locations that import from new locations if needed for backward compatibility
5. Document the archived components in a README file for future reference

## Migration Timeline

The archiving process should be coordinated with the implementation of new components:

1. **Phase 1 (Days 1-2):**

   - Create new directory structure
   - Implement core components
   - Keep all existing files in place

2. **Phase 2 (Days 3-4):**

   - Begin archiving files that have been fully replaced
   - Create compatibility layers for API routes

3. **Phase 3 (Days 5-7):**
   - Complete archiving process
   - Finalize all reference updates
   - Add documentation about archived components
