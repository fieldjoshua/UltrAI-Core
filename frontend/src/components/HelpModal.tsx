import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from './ui/dialog';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';

interface HelpModalProps {
  shortcuts: Array<{
    key: string;
    ctrlKey?: boolean;
    shiftKey?: boolean;
    altKey?: boolean;
    description: string;
  }>;
}

export const HelpModal: React.FC<HelpModalProps> = ({ shortcuts }) => {
  const formatShortcut = (shortcut: HelpModalProps['shortcuts'][0]) => {
    const parts = [];
    if (shortcut.ctrlKey) parts.push('Ctrl');
    if (shortcut.shiftKey) parts.push('Shift');
    if (shortcut.altKey) parts.push('Alt');
    parts.push(shortcut.key.toUpperCase());
    return parts.join(' + ');
  };

  return (
    <Dialog>
      <DialogTrigger asChild>
        <Button variant="ghost" size="sm">
          Help
        </Button>
      </DialogTrigger>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Help & Keyboard Shortcuts</DialogTitle>
        </DialogHeader>
        <Tabs defaultValue="shortcuts">
          <TabsList>
            <TabsTrigger value="shortcuts">Keyboard Shortcuts</TabsTrigger>
            <TabsTrigger value="features">Features</TabsTrigger>
            <TabsTrigger value="tips">Tips & Tricks</TabsTrigger>
          </TabsList>
          <TabsContent value="shortcuts" className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              {shortcuts.map((shortcut, index) => (
                <div key={index} className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">
                    {shortcut.description}
                  </span>
                  <kbd className="px-2 py-1 bg-gray-100 rounded text-sm">
                    {formatShortcut(shortcut)}
                  </kbd>
                </div>
              ))}
            </div>
          </TabsContent>
          <TabsContent value="features" className="space-y-4">
            <div className="prose max-w-none">
              <h3>Key Features</h3>
              <ul>
                <li>
                  <strong>Multi-Model Analysis:</strong> Compare responses from
                  different LLMs
                </li>
                <li>
                  <strong>Analysis Patterns:</strong> Choose from various
                  analysis approaches
                </li>
                <li>
                  <strong>Export Options:</strong> Save results in JSON, CSV, or
                  Markdown
                </li>
                <li>
                  <strong>History Management:</strong> Access and manage past
                  analyses
                </li>
              </ul>
            </div>
          </TabsContent>
          <TabsContent value="tips" className="space-y-4">
            <div className="prose max-w-none">
              <h3>Tips for Better Analysis</h3>
              <ul>
                <li>Use specific prompts for more accurate results</li>
                <li>
                  Compare responses from multiple models for better insights
                </li>
                <li>Export results for future reference</li>
                <li>Use keyboard shortcuts for faster navigation</li>
                <li>Check the history for similar past analyses</li>
              </ul>
            </div>
          </TabsContent>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
};
