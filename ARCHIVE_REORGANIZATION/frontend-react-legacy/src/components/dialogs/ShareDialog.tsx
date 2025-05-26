import React from 'react';
import { Button } from '../ui/button'; // Adjust path as needed
import { Share2, X, Link, Copy, Check } from 'lucide-react';

// Assuming HistoryItem interface is defined/imported
interface HistoryItem {
  id: string;
  prompt: string;
  output: string;
  models: string[];
  ultraModel: string;
  timestamp: string;
  usingDocuments?: boolean;
  documents?: { id: string; name: string }[];
}

interface ShareDialogProps {
  showShareDialog: boolean;
  shareDialogItem: HistoryItem | null;
  shareUrl: string;
  copySuccess: boolean;
  onClose: () => void;
  onCopyToClipboard: () => void;
}

const ShareDialog: React.FC<ShareDialogProps> = ({
  showShareDialog,
  shareDialogItem,
  shareUrl,
  copySuccess,
  onClose,
  onCopyToClipboard,
}) => {
  if (!showShareDialog || !shareDialogItem) return null;

  return (
    <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
      <div className="bg-gray-900 border-2 border-cyan-700 rounded-lg max-w-md w-full p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold text-cyan-400 flex items-center">
            <Share2 className="mr-2 h-5 w-5" />
            Share Analysis
          </h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="text-gray-400"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="space-y-4">
          <p className="text-gray-300">
            Share this analysis with others using the link below:
          </p>

          <div className="flex items-center">
            <div className="bg-black/60 border border-gray-700 rounded-lg p-3 flex-1 overflow-hidden">
              <p className="text-cyan-300 truncate">{shareUrl}</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              className={`ml-2 ${
                copySuccess
                  ? 'text-green-400 border-green-700'
                  : 'text-cyan-400 border-cyan-700'
              }`}
              onClick={onCopyToClipboard}
              title={copySuccess ? 'Copied!' : 'Copy link'} // Dynamic title
            >
              {copySuccess ? (
                <Check className="h-4 w-4" />
              ) : (
                <Copy className="h-4 w-4" />
              )}
            </Button>
          </div>

          <div className="pt-2">
            <p className="text-sm text-gray-400">
              Anyone with this link can view this analysis without needing an
              account.
            </p>
          </div>

          <div className="bg-gray-800/60 border border-gray-700 rounded-lg p-3 mt-4">
            <div className="flex items-center mb-2">
              <Link className="text-cyan-400 mr-2 h-4 w-4" />
              <h3 className="text-cyan-300 font-medium">Shared Analysis</h3>
            </div>
            <p className="text-gray-400 text-sm mb-1 truncate">
              <span className="text-gray-500">Prompt: </span>
              {shareDialogItem.prompt.substring(0, 100)}
              {shareDialogItem.prompt.length > 100 ? '...' : ''}
            </p>
            <p className="text-gray-400 text-xs">
              <span className="text-gray-500">Using models: </span>
              {shareDialogItem.models.map(model => model).join(', ')}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ShareDialog;
