import React from 'react';
import { LucideProps } from 'lucide-react'; // Import LucideProps type

// Define interfaces for options structure (assuming they are passed in)
interface AlaCarteOption {
    id: string;
    name: string;
    description: string;
    icon: React.ComponentType<LucideProps>;
}

interface FormatOption {
    id: string;
    name: string;
    description: string;
    icon: React.ComponentType<LucideProps>;
}

interface OptionsStepProps {
    alaCarteOptions: AlaCarteOption[];
    formatOptions: FormatOption[];
    selectedAlaCarteOptions: string[];
    selectedOutputFormat: string;
    onAlaCarteOptionToggle: (id: string) => void;
    onOutputFormatChange: (id: string) => void;
}

const OptionsStep: React.FC<OptionsStepProps> = ({
    alaCarteOptions,
    formatOptions,
    selectedAlaCarteOptions,
    selectedOutputFormat,
    onAlaCarteOptionToggle,
    onOutputFormatChange,
}) => {
    return (
        <div className="space-y-6 fadeIn">
            <div className="mb-6">
                <h3 className="text-lg font-medium text-gray-800 dark:text-white mb-2">
                    Additional Options
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                    Select any additional features you want to enable (optional).
                </p>

                {/* A La Carte Options */}
                <div className="mb-8">
                    <h4 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">
                        A La Carte Options
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                        {alaCarteOptions.map((option) => {
                            const isSelected = selectedAlaCarteOptions.includes(option.id);
                            const Icon = option.icon;

                            return (
                                <div
                                    key={option.id}
                                    className={`
                                        border rounded-lg p-3 cursor-pointer transition-all
                                        ${isSelected
                                            ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                                            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                                        }
                                    `}
                                    onClick={() => onAlaCarteOptionToggle(option.id)}
                                >
                                    <div className="flex items-center">
                                        <div
                                            className={`p-2 rounded-full mr-3 ${isSelected
                                                ? 'bg-blue-100 dark:bg-blue-900/30'
                                                : 'bg-gray-100 dark:bg-gray-800'
                                                }`}
                                        >
                                            <Icon
                                                className={`h-4 w-4 ${isSelected
                                                    ? 'text-blue-600'
                                                    : 'text-gray-500 dark:text-gray-400'
                                                    }`}
                                            />
                                        </div>
                                        <div>
                                            <h5 className="font-medium text-sm text-gray-800 dark:text-gray-200">
                                                {option.name}
                                            </h5>
                                            <p className="text-xs text-gray-600 dark:text-gray-400">
                                                {option.description}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Output Format Options */}
                <div>
                    <h4 className="text-md font-medium text-gray-700 dark:text-gray-300 mb-3">
                        Output Format
                    </h4>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                        {formatOptions.map((format) => {
                            const isSelected = selectedOutputFormat === format.id;
                            const Icon = format.icon;

                            return (
                                <div
                                    key={format.id}
                                    className={`
                                        border rounded-lg p-3 cursor-pointer transition-all text-center
                                        ${isSelected
                                            ? 'border-green-500 bg-green-50 dark:bg-green-900/20'
                                            : 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600'
                                        }
                                    `}
                                    onClick={() => onOutputFormatChange(format.id)}
                                >
                                    <div className="flex flex-col items-center">
                                        <div
                                            className={`p-2 rounded-full mb-2 ${isSelected
                                                ? 'bg-green-100 dark:bg-green-900/30'
                                                : 'bg-gray-100 dark:bg-gray-800'
                                                }`}
                                        >
                                            <Icon
                                                className={`h-4 w-4 ${isSelected
                                                    ? 'text-green-600'
                                                    : 'text-gray-500 dark:text-gray-400'
                                                    }`}
                                            />
                                        </div>
                                        <h5 className="font-medium text-sm text-gray-800 dark:text-gray-200">
                                            {format.name}
                                        </h5>
                                        <p className="text-xs text-gray-600 dark:text-gray-400">
                                            {format.description}
                                        </p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            </div>
            {/* Navigation buttons handled by parent */}
        </div>
    );
};

export default OptionsStep;