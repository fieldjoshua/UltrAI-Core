import React, { useState } from 'react';
import { Card } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Clipboard, Download, ChevronDown, ChevronUp, Code, FileText, ExternalLink } from 'lucide-react';
import { Button } from '../ui/button';

export interface AnalysisResult {
  modelId: string;
  modelName: string;
  content: string;
  timestamp: string;
  processingTimeMs: number;
  sections?: {
    id: string;
    title: string;
    content: string;
  }[];
  metadata?: Record<string, any>;
}

export interface ResultsDisplayProps {
  results: AnalysisResult[];
  isLoading: boolean;
  error?: Error;
  comparisonMode?: boolean;
}

export const ResultsDisplay: React.FC<ResultsDisplayProps> = ({
  results,
  isLoading,
  error,
  comparisonMode = false
}) => {
  const [activeTab, setActiveTab] = useState<string>(
    results.length > 0 ? results[0].modelId : 'comparison'
  );
  const [expandedSections, setExpandedSections] = useState<string[]>([]);
  const [viewMode, setViewMode] = useState<'standard' | 'compact' | 'detailed'>('standard');
  
  const toggleSection = (sectionId: string) => {
    if (expandedSections.includes(sectionId)) {
      setExpandedSections(expandedSections.filter(id => id !== sectionId));
    } else {
      setExpandedSections([...expandedSections, sectionId]);
    }
  };
  
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Could add a toast notification here
  };
  
  const downloadAsFile = (content: string, filename: string, format: 'txt' | 'md' = 'txt') => {
    const element = document.createElement('a');
    const file = new Blob([content], {type: 'text/plain'});
    element.href = URL.createObjectURL(file);
    element.download = `${filename}.${format}`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };
  
  const formatModelName = (modelId: string, modelName?: string): string => {
    if (modelName) return modelName;
    
    // If no model name is provided, format the ID
    const modelMap: Record<string, string> = {
      'gpt4o': 'GPT-4o',
      'gpt4': 'GPT-4',
      'claude-3-opus': 'Claude 3 Opus',
      'claude-3-sonnet': 'Claude 3 Sonnet',
      'gemini-pro': 'Gemini Pro',
      'llama3': 'Llama 3',
    };
    
    return modelMap[modelId] || modelId;
  };
  
  const renderContent = (content: string) => {
    // Simple regex to detect code blocks and add syntax highlighting
    const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
    const parts = [];
    let lastIndex = 0;
    let match;
    
    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        parts.push(
          <p key={`text-${lastIndex}`} className="whitespace-pre-wrap mb-4">
            {content.slice(lastIndex, match.index)}
          </p>
        );
      }
      
      // Add code block with syntax highlighting
      const language = match[1] || 'plaintext';
      const code = match[2];
      parts.push(
        <div key={`code-${match.index}`} className="relative mb-4">
          <div className="absolute right-2 top-2 flex space-x-1">
            <button 
              onClick={() => copyToClipboard(code)}
              className="p-1 rounded bg-gray-800 text-gray-200 hover:bg-gray-700"
              aria-label="Copy code"
            >
              <Clipboard size={14} />
            </button>
          </div>
          <div className="bg-gray-900 text-gray-100 p-3 rounded-md overflow-x-auto">
            <div className="text-xs text-gray-400 pb-2">{language}</div>
            <pre className="font-mono text-sm">
              <code>{code}</code>
            </pre>
          </div>
        </div>
      );
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text after the last code block
    if (lastIndex < content.length) {
      parts.push(
        <p key={`text-${lastIndex}`} className="whitespace-pre-wrap">
          {content.slice(lastIndex)}
        </p>
      );
    }
    
    return <div className="text-gray-800">{parts}</div>;
  };
  
  if (isLoading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-gray-200 rounded w-1/4 mb-4"></div>
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    );
  }
  
  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md text-red-700">
        Error displaying results: {error.message}
      </div>
    );
  }
  
  if (results.length === 0) {
    return (
      <div className="text-center p-8 bg-gray-50 border border-gray-200 rounded-md">
        <div className="text-gray-500">No results to display</div>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Analysis Results</h2>
        <div className="flex items-center space-x-2">
          <select
            value={viewMode}
            onChange={(e) => setViewMode(e.target.value as any)}
            className="text-sm border border-gray-300 rounded-md px-2 py-1"
          >
            <option value="standard">Standard View</option>
            <option value="compact">Compact View</option>
            <option value="detailed">Detailed View</option>
          </select>
          <Button
            variant="outline"
            size="sm"
            onClick={() => downloadAsFile(
              results.map(r => `# ${formatModelName(r.modelId, r.modelName)}\n\n${r.content}`).join('\n\n---\n\n'),
              'ultra-analysis-results',
              'md'
            )}
          >
            <Download size={16} className="mr-1" />
            Export
          </Button>
        </div>
      </div>
      
      <Tabs defaultValue={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="w-full flex overflow-x-auto mb-2">
          {results.map(result => (
            <TabsTrigger 
              key={result.modelId} 
              value={result.modelId}
              className="flex-1 min-w-max"
            >
              {formatModelName(result.modelId, result.modelName)}
            </TabsTrigger>
          ))}
          {results.length > 1 && (
            <TabsTrigger value="comparison" className="flex-1 min-w-max">
              Side-by-Side
            </TabsTrigger>
          )}
        </TabsList>
        
        {/* Individual model tabs */}
        {results.map(result => (
          <TabsContent key={result.modelId} value={result.modelId} className="mt-4">
            <Card className="p-4">
              <div className="flex justify-between items-center mb-4">
                <div>
                  <h3 className="text-lg font-medium">
                    {formatModelName(result.modelId, result.modelName)}
                  </h3>
                  <div className="text-sm text-gray-500">
                    {new Date(result.timestamp).toLocaleString()} • 
                    {(result.processingTimeMs / 1000).toFixed(2)}s processing time
                  </div>
                </div>
                <div className="flex space-x-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(result.content)}
                  >
                    <Clipboard size={16} className="mr-1" />
                    Copy
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => downloadAsFile(
                      result.content,
                      `${result.modelId}-analysis`,
                      'txt'
                    )}
                  >
                    <FileText size={16} className="mr-1" />
                    Save
                  </Button>
                </div>
              </div>
              
              {/* Sectioned content */}
              {result.sections && result.sections.length > 0 ? (
                <div className="space-y-4">
                  {result.sections.map((section) => {
                    const isExpanded = expandedSections.includes(section.id);
                    
                    return (
                      <div key={section.id} className="border rounded-md overflow-hidden">
                        <div 
                          className="bg-gray-100 px-4 py-2 flex justify-between items-center cursor-pointer"
                          onClick={() => toggleSection(section.id)}
                        >
                          <h4 className="font-medium">{section.title}</h4>
                          {isExpanded ? <ChevronUp size={18} /> : <ChevronDown size={18} />}
                        </div>
                        {isExpanded && (
                          <div className="p-4">
                            {renderContent(section.content)}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="prose max-w-none">
                  {renderContent(result.content)}
                </div>
              )}
              
              {/* Show metadata if in detailed view */}
              {viewMode === 'detailed' && result.metadata && (
                <div className="mt-6 pt-4 border-t">
                  <h4 className="text-sm font-medium text-gray-700 mb-2">Metadata</h4>
                  <pre className="text-xs bg-gray-50 p-3 rounded overflow-auto">
                    {JSON.stringify(result.metadata, null, 2)}
                  </pre>
                </div>
              )}
            </Card>
          </TabsContent>
        ))}
        
        {/* Comparison tab */}
        {results.length > 1 && (
          <TabsContent value="comparison" className="mt-4">
            <div className={`grid ${viewMode === 'compact' ? 'grid-cols-1' : 'grid-cols-1 lg:grid-cols-2'} gap-4`}>
              {results.map(result => (
                <Card key={result.modelId} className="p-4 h-full overflow-hidden">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="text-lg font-medium">
                      {formatModelName(result.modelId, result.modelName)}
                    </h3>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => copyToClipboard(result.content)}
                    >
                      <Clipboard size={16} />
                    </Button>
                  </div>
                  <div className={`prose max-w-none ${viewMode === 'compact' ? 'max-h-64 overflow-y-auto' : ''}`}>
                    {renderContent(result.content)}
                  </div>
                </Card>
              ))}
            </div>
          </TabsContent>
        )}
      </Tabs>
    </div>
  );
};

export default ResultsDisplay;