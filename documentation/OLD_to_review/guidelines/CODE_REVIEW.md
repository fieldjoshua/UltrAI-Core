# Mandatory Code Review Process

This document outlines the code review requirements for the UltraAI project. All changes to the codebase must go through this process without exception.

## Code Review Requirements

### Prerequisites for Submitting Code for Review

Before submitting code for review, ensure:

1. You have read all relevant documentation in the `documentation/` directory
2. You have checked that your changes align with existing patterns and conventions
3. You have run linters and formatting tools on your code
4. You have tested your changes locally
5. You have updated relevant documentation

### Required Approvals

All changes require at least one approval from an authorized reviewer before merging:

- Changes to frontend components require approval from a UI team member
- Changes to backend APIs require approval from a backend team member
- Changes to core patterns require approval from a core team member
- Changes to documentation require approval from a documentation team member

Critical files require multiple approvals as specified in the `CODEOWNERS` file.

## Reviewer Guidelines

As a reviewer, you must verify:

### 1. Documentation Compliance

- Confirm that the changes align with project documentation
- Verify that all new features match patterns in the documentation
- Ensure that documentation is updated if necessary

### 2. Duplication Check

- Check for duplicate code and implementations
- Verify that no duplicate functions, components, or files exist
- Ensure hooks are properly reused rather than reimplemented

### 3. Code Quality Standards

- Ensure code adheres to project style guidelines
- Verify proper typing in TypeScript files
- Check for common issues like duplicate identifiers
- Review for potential bugs and edge cases

### 4. Project Structure

- Ensure new files follow the project structure
- Verify that code is organized according to project conventions
- Check that imports use correct paths

## Specific Issue Prevention

### Preventing Duplicate Functions

- Always check if a function exists in a hook before implementing it in a component
- Use grep to search for existing implementations before creating new ones
- Follow the "single source of truth" principle for all functionality

### Preventing Duplicate Components

- Before creating a new component, check if it already exists
- Use composition with existing components when possible
- Document component purposes clearly

### Preventing Duplicate Files

- Never create multiple files with the same name in different directories
- Follow the established project structure for new files
- Remove redundant files when found

## Review Process Flow

1. **Self-Review**: Developer reviews their own code against the checklist
2. **Submission**: Developer creates a pull request with detailed description
3. **Initial Review**: Reviewer checks the code against guidelines
4. **Feedback**: Reviewer provides comments and change requests if needed
5. **Iteration**: Developer makes requested changes
6. **Approval**: Reviewer approves the changes once satisfied
7. **Merge**: Changes are merged only after required approvals

## Enforcing Review Requirements

The review process is enforced through:

1. Branch protection rules in the repository
2. CODEOWNERS file defining required reviewers
3. CI/CD checks that must pass before merging
4. Pre-commit hooks to catch issues early

## Questions and Exceptions

For questions about the review process or to request exceptions in urgent cases, contact the project lead or open an issue for discussion.

## Review Checklist Template

```markdown
## Code Review Checklist

### Documentation
- [ ] Changes align with project documentation
- [ ] Documentation is updated if needed
- [ ] New features match existing patterns

### Duplication
- [ ] No duplicate functions or methods
- [ ] No duplicate components
- [ ] No duplicate files with similar purpose

### Code Quality
- [ ] Code follows style guidelines
- [ ] Proper typing is used
- [ ] No obvious bugs or edge cases
- [ ] Tests are included where appropriate

### Structure
- [ ] Files are in the correct directories
- [ ] Code organization follows project conventions
- [ ] Imports use correct paths

### Comments
<!-- Add any specific comments or concerns here -->
```
