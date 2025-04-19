/**
 * @file ${fileName}
 * @documentation This analysis pattern MUST follow documentation/instructions/PATTERNS.md
 * @documentation This pattern MUST be defined in documentation/logic/INTELLIGENCE_MULTIPLICATION.md
 * @requires-review Changes to analysis patterns require review by the core team
 *
 * IMPORTANT: Before implementing any analysis pattern:
 * 1. Ensure the pattern is documented in PATTERNS.md
 * 2. Verify the pattern doesn't duplicate an existing one
 * 3. Follow the standard pattern structure as per documentation
 */

import React from 'react';

// Pattern interface should match documented structure
interface ${patternName}Props {
  prompt: string;
  models: string[];
  primaryModel: string;
  options?: Record<string, any>;
}

/**
 * ${patternName} - Analysis pattern implementation
 *
 * @documentation This pattern is defined in documentation/instructions/PATTERNS.md
 */
const ${patternName}: React.FC<${patternName}Props> = ({
  prompt,
  models,
  primaryModel,
  options = {}
}) => {
  // Pattern implementation should follow documented structure
  return (
    <div className="analysis-pattern">
      <h2>{pattern_name}</h2>
      <div className="pattern-description">
        {/* Pattern description from documentation */}
      </div>

      {/* Pattern implementation */}
    </div>
  );
};

export default ${patternName};
