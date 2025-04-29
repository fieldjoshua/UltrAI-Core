# Cursor Prompt Examples for UltraAI Project

This file contains ready-to-use prompt examples for working with the UltraAI project in Cursor.

## Initial Context Prompt

```
You're helping me work on the UltraAI project which follows a strict documentation-first approach.
Before suggesting any implementations, please review:
1. documentation/CORE_README.md for project structure
2. documentation/guidelines/DOCUMENTATION_FIRST.md for our approach
3. documentation/guidelines/CONTRIBUTING.md for code organization
4. documentation/instructions/PATTERNS.md for analysis patterns

The most important rule is to avoid duplicating existing functionality. Always check
for existing implementations before creating new ones.
```

## Creating Components

```
I need to create a new component for [purpose]. Before doing so:
1. Check if a similar component already exists in the components directory
2. Review documentation/guidelines/CONTRIBUTING.md for component structure
3. Use hooks from the hooks directory instead of reimplementing state logic
4. Follow the component template from cursor-templates/component.tsx
```

## Creating Hooks

```
I need a custom hook for [purpose]. Before creating it:
1. Check if a similar hook already exists in the hooks directory
2. Review documentation/guidelines/CONTRIBUTING.md for hook structure
3. Follow the hook template from cursor-templates/hook.ts
4. Ensure the hook name starts with "use" and follows React conventions
```

## Working with Analysis Patterns

```
I need to work with the [pattern] analysis pattern. Before doing anything:
1. Verify this pattern exists in documentation/instructions/PATTERNS.md
2. Read documentation/logic/INTELLIGENCE_MULTIPLICATION.md to understand pattern purpose
3. Follow the analysis pattern template if creating a new implementation
4. Ensure any code references the documentation
```

## Fixing Bugs

```
I need to fix a bug in [file/component]. Before making changes:
1. Help me understand if this is a deviation from documentation
2. Check if the issue is from duplicated functionality
3. Ensure our fix aligns with the documentation-first approach
4. Add appropriate documentation references in comments
```

## Code Review

```
Please review this [file/component] for compliance with our documentation-first approach:
1. Check if it follows patterns in documentation/guidelines/CONTRIBUTING.md
2. Verify it doesn't duplicate existing functionality
3. Ensure it references appropriate documentation
4. Check for proper use of hooks and components
```

## Automated Checks Fixes

```
Our documentation compliance check failed with this error: [error message].
Help me fix this by:
1. Understanding what documentation I'm violating
2. Identifying changes needed for compliance
3. Adding proper documentation references
4. Ensuring no duplicate functionality
```

## Feature Implementation

```
I need to implement a feature for [purpose]. Please:
1. First search for existing similar functionality
2. Review documentation/CORE_README.md and other relevant docs
3. Suggest an implementation that follows our documentation patterns
4. Add appropriate JSDoc and documentation references
```

## Documentation Improvement

```
I need to improve documentation for [component/feature]. Please:
1. Review the existing code to understand its purpose
2. Check existing documentation for inconsistencies
3. Suggest improvements that maintain our documentation-first approach
4. Ensure cross-references to other documentation
```

## Codebase Exploration

```
I'm trying to understand how [feature] works in our codebase. Please:
1. Help me identify relevant files and components
2. Check documentation that describes this feature
3. Explain the implementation in relation to our documentation
4. Identify any potential documentation gaps
```
