# AI Usage Guide for UltraAI Framework

This guide provides best practices for using AI coding assistants with the UltraAI Framework.

## Effective Prompting Strategies

When working with AI assistants on this project, use these strategies for optimal results:

1. **Start with documentation context**:
   ```
   I'm working on the UltraAI Framework. Before answering, please review the
   documentation structure in documentation/UNIFIED_README.md to understand
   the project approach and existing patterns.
   ```

2. **Reference specific documentation**:
   ```
   I need help with analysis patterns in UltraAI. The pattern documentation
   is in documentation/instructions/PATTERNS.md and the conceptual background
   is in documentation/logic/INTELLIGENCE_MULTIPLICATION.md.
   ```

3. **Check for existing implementations**:
   ```
   Before implementing this feature, can you check if something similar already
   exists by examining the documentation directory and core source files?
   ```

## Avoiding Common Issues

- **Duplicate Functionality**: Always ask the AI to check if a feature already exists
- **Inconsistent Patterns**: Reference existing patterns when asking for new implementations
- **Documentation Drift**: Request AI to update documentation alongside code changes
- **Isolated Changes**: Ensure AI understands the entire workflow before making changes

## Documentation-First Implementation

When implementing new features with AI assistance:

1. **Start with documentation**: Have the AI draft documentation before writing code
2. **Reference existing patterns**: Point AI to similar implementations
3. **Follow the implementation plan**: Share the relevant implementation plan document
4. **Update documentation**: Ensure AI updates relevant documentation files

Example prompt:
```
I want to implement a new analysis pattern called "Perspective Analysis".
First, help me create the documentation for this pattern following the
structure in documentation/instructions/PATTERNS.md. Then we'll implement
it based on the patterns in src/patterns/ultra_analysis_patterns.py.
```

## Code Review with AI

When using AI for code review:

1. **Share context**: Provide links to documentation and implementation plans
2. **Ask specific questions**: "Does this implementation follow the pattern in documentation/instructions/PATTERNS.md?"
3. **Check for consistency**: "Is this consistent with our existing patterns?"
4. **Verify documentation**: "Does the code match what we've documented?"

## Template Prompts

### Feature Implementation
```
I need to implement [FEATURE] for UltraAI. The relevant documentation is in
[DOCUMENTATION_PATH]. Similar features are implemented in [EXISTING_FEATURE_PATH].
Please help me:
1. Verify this doesn't duplicate existing functionality
2. Draft documentation updates first
3. Implement the feature following our existing patterns
4. Update any affected documentation
```

### Bug Fix
```
I'm fixing a bug in [COMPONENT] of UltraAI. The issue is [ISSUE_DESCRIPTION].
The component is documented in [DOCUMENTATION_PATH] and implemented in
[IMPLEMENTATION_PATH]. Please help me:
1. Understand the root cause based on our documentation and code
2. Develop a fix that's consistent with our patterns
3. Update documentation if needed
```

### Documentation Update
```
I need to update documentation for [FEATURE] in UltraAI. The current documentation
is in [DOCUMENTATION_PATH] and the implementation is in [IMPLEMENTATION_PATH].
Please help me ensure the documentation:
1. Accurately reflects the current implementation
2. Follows our documentation structure
3. Cross-references related documentation
4. Provides clear guidance for users
```

## Experiment Safely with AI

To safely experiment with AI-assisted development:

1. **Create experimental branches**: Use clearly marked branches for AI experimentation
2. **Document AI-generated code**: Add comments indicating AI-generated sections
3. **Review thoroughly**: Carefully review all AI-generated code before merging
4. **Test incrementally**: Test small changes rather than large AI-generated components

## AI-Assisted Troubleshooting

When troubleshooting with AI:

1. Share the relevant documentation first
2. Provide error messages and context
3. Ask AI to explain the issue in terms of our documented architecture
4. Request solutions that align with our existing patterns

Example:
```
I'm getting this error in our analysis pipeline: [ERROR].
The analysis pattern is documented in documentation/instructions/PATTERNS.md
and implemented in src/patterns/ultra_analysis_patterns.py.
The multi-stage process is described in documentation/logic/INTELLIGENCE_MULTIPLICATION.md.
Please help me troubleshoot this issue within our existing architecture.
```

## Maintaining Documentation with AI

When using AI to maintain documentation:

1. **Cross-reference check**: Ask AI to verify all cross-references are correct
2. **Consistency check**: Have AI verify terminology consistency
3. **Update multiple files**: Ensure AI updates all affected documentation files
4. **Format verification**: Confirm AI follows our documentation format

Remember that AI assistance works best when it builds upon our documentation-first approach, not as a replacement for it.
