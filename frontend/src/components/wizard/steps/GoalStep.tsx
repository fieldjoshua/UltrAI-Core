import React from 'react';
import { Checkbox } from '../../ui/Checkbox';

export interface Goal {
  id: string;
  label: string;
  description: string;
  category: 'analysis' | 'research' | 'creative' | 'business';
}

export const AVAILABLE_GOALS: Goal[] = [
  {
    id: 'comprehensive-analysis',
    label: 'Comprehensive Analysis',
    description: 'Deep dive into complex topics with detailed insights',
    category: 'analysis'
  },
  {
    id: 'quick-overview',
    label: 'Quick Overview',
    description: 'Rapid assessment and key takeaways',
    category: 'analysis'
  },
  {
    id: 'research-synthesis',
    label: 'Research Synthesis',
    description: 'Combine multiple sources into coherent insights',
    category: 'research'
  },
  {
    id: 'trend-analysis',
    label: 'Trend Analysis',
    description: 'Identify patterns and future directions',
    category: 'research'
  },
  {
    id: 'creative-brainstorming',
    label: 'Creative Brainstorming',
    description: 'Generate innovative ideas and solutions',
    category: 'creative'
  },
  {
    id: 'content-generation',
    label: 'Content Generation',
    description: 'Create high-quality written content',
    category: 'creative'
  },
  {
    id: 'strategic-planning',
    label: 'Strategic Planning',
    description: 'Develop actionable strategies and recommendations',
    category: 'business'
  },
  {
    id: 'competitive-analysis',
    label: 'Competitive Analysis',
    description: 'Evaluate market position and opportunities',
    category: 'business'
  }
];

interface GoalStepProps {
  selectedGoals: string[];
  onGoalToggle: (goalId: string) => void;
}

export function GoalStep({ selectedGoals, onGoalToggle }: GoalStepProps) {
  const categories = ['analysis', 'research', 'creative', 'business'] as const;

  return (
    <div className="space-y-6">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">What are your goals?</h2>
        <p className="text-gray-300">
          Select one or more objectives for your AI analysis session
        </p>
      </div>

      <div className="space-y-8">
        {categories.map(category => {
          const categoryGoals = AVAILABLE_GOALS.filter(goal => goal.category === category);
          if (categoryGoals.length === 0) return null;

          return (
            <div key={category} className="space-y-4">
              <h3 className="text-lg font-semibold text-cyan-400 capitalize">
                {category.replace('-', ' ')}
              </h3>
              <div className="grid gap-4 md:grid-cols-2">
                {categoryGoals.map(goal => (
                  <div
                    key={goal.id}
                    className={`p-4 rounded-lg border transition-all cursor-pointer ${
                      selectedGoals.includes(goal.id)
                        ? 'border-cyan-400 bg-cyan-400/10'
                        : 'border-gray-600 bg-gray-800/50 hover:border-gray-500'
                    }`}
                    onClick={() => onGoalToggle(goal.id)}
                  >
                    <div className="flex items-start space-x-3">
                      <Checkbox
                        checked={selectedGoals.includes(goal.id)}
                        onChange={() => onGoalToggle(goal.id)}
                        className="mt-1"
                      />
                      <div className="flex-1">
                        <label className="text-white font-medium cursor-pointer">
                          {goal.label}
                        </label>
                        <p className="text-sm text-gray-400 mt-1">
                          {goal.description}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {selectedGoals.length > 0 && (
        <div className="bg-gray-800/50 p-4 rounded-lg border border-gray-600">
          <p className="text-sm text-gray-300">
            Selected {selectedGoals.length} goal{selectedGoals.length !== 1 ? 's' : ''}
          </p>
        </div>
      )}
    </div>
  );
}