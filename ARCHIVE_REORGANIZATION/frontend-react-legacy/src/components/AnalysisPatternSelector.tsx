import React from 'react';
import { Card } from './ui/card';
import { RadioGroup, RadioGroupItem } from './ui/radio-group';
import { Label } from './ui/label';

interface AnalysisPattern {
  id: string;
  name: string;
  description: string;
}

interface AnalysisPatternSelectorProps {
  patterns: AnalysisPattern[];
  selectedPattern: string;
  onPatternChange: (patternId: string) => void;
  disabled?: boolean;
}

export const AnalysisPatternSelector: React.FC<
  AnalysisPatternSelectorProps
> = ({ patterns, selectedPattern, onPatternChange, disabled = false }) => {
  return (
    <Card className="w-full p-4">
      <h3 className="text-lg font-semibold mb-4">Select Analysis Pattern</h3>
      <RadioGroup
        value={selectedPattern}
        onValueChange={onPatternChange}
        disabled={disabled}
        className="space-y-4"
      >
        {patterns.map(pattern => (
          <div key={pattern.id} className="flex items-start space-x-3">
            <RadioGroupItem value={pattern.id} id={pattern.id} />
            <div className="space-y-1">
              <Label htmlFor={pattern.id} className="font-medium">
                {pattern.name}
              </Label>
              <p className="text-sm text-gray-500">{pattern.description}</p>
            </div>
          </div>
        ))}
      </RadioGroup>
    </Card>
  );
};
