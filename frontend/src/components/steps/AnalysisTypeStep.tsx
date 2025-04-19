import React from 'react';
import { LucideProps } from 'lucide-react'; // Import LucideProps type

// Assuming analysisTypes structure is defined elsewhere or passed
// Re-defining here for component context
interface AnalysisTypeOption {
    id: string;
    name: string;
    description: string;
    icon: React.ComponentType<LucideProps>; // Use LucideProps type
}

interface AnalysisTypeStepProps {
    analysisTypes: AnalysisTypeOption[];
    selectedAnalysisType: string;
    onAnalysisTypeChange: (id: string) => void;
}

const AnalysisTypeStep: React.FC<AnalysisTypeStepProps> = ({
    analysisTypes,
    selectedAnalysisType,
    onAnalysisTypeChange,
}) => {
    return (
        <div className="space-y-6 fadeIn">
            <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-2">
                    Select Analysis Method
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Choose how Ultra should approach your query.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {analysisTypes.map((type) => {
                        const isSelected = selectedAnalysisType === type.id;
                        const Icon = type.icon;

                        return (
                            <div
                                key={type.id}
                                className={`
                                    border rounded-lg p-4 cursor-pointer transition-all
                                    ${isSelected
                                        ? 'border-purple-500 bg-purple-50 dark:bg-purple-900/20'
                                        : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                                    }
                                `}
                                onClick={() => onAnalysisTypeChange(type.id)}
                            >
                                <div className="flex flex-col items-center text-center">
                                    <div
                                        className={`p-3 rounded-full mb-3 ${isSelected
                                            ? 'bg-purple-100 dark:bg-purple-900/30'
                                            : 'bg-gray-100 dark:bg-gray-800'
                                            }`}
                                    >
                                        <Icon
                                            className={`h-6 w-6 ${isSelected
                                                ? 'text-purple-600'
                                                : 'text-gray-500 dark:text-gray-400'
                                                }`}
                                        />
                                    </div>
                                    <h4 className="font-medium text-gray-800 dark:text-gray-200 mb-1">
                                        {type.name}
                                    </h4>
                                    <p className="text-xs text-gray-600 dark:text-gray-400">
                                        {type.description}
                                    </p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>
            {/* Navigation buttons handled by parent */}
        </div>
    );
};

export default AnalysisTypeStep;