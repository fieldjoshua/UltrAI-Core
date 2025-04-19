import React from 'react';
import { Button } from '../ui/button'; // Adjust path as needed
import { History, X, Trash2, Share2, FileText } from 'lucide-react';

// Assuming HistoryItem and ShareItem interfaces are defined/imported
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

interface ShareItem extends HistoryItem {
    shareId: string;
    shareUrl: string;
    createdAt: string;
}

interface HistoryPanelProps {
    showHistory: boolean;
    history: HistoryItem[];
    sharedItems: ShareItem[]; // Needed to show the 'Shared' badge
    onClose: () => void;
    onClearAll: () => void;
    onLoadItem: (item: HistoryItem) => void;
    onDeleteItem: (id: string) => void;
    onShareItem: (item: HistoryItem) => void;
}

const HistoryPanel: React.FC<HistoryPanelProps> = ({
    showHistory,
    history,
    sharedItems,
    onClose,
    onClearAll,
    onLoadItem,
    onDeleteItem,
    onShareItem,
}) => {
    if (!showHistory) return null;

    return (
        <div className="fixed inset-0 bg-black/80 z-50 flex items-center justify-center p-4">
            <div className="bg-gray-900 border-2 border-cyan-700 rounded-lg max-w-3xl w-full max-h-[90vh] flex flex-col">
                <div className="p-4 border-b border-cyan-800 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-cyan-400 flex items-center">
                        <History className="mr-2 h-5 w-5" />
                        Interaction History
                    </h2>
                    <div className="flex items-center">
                        {history.length > 0 && (
                            <Button
                                variant="outline"
                                size="sm"
                                onClick={onClearAll}
                                className="mr-2 text-red-400 border-red-800 hover:bg-red-900/30"
                            >
                                <Trash2 className="h-4 w-4 mr-1" />
                                Clear All
                            </Button>
                        )}
                        <Button
                            variant="ghost"
                            size="sm"
                            onClick={onClose}
                            className="text-gray-400"
                        >
                            <X className="h-5 w-5" />
                        </Button>
                    </div>
                </div>

                <div className="flex-1 overflow-y-auto p-4">
                    {history.length === 0 ? (
                        <div className="text-center py-8 text-gray-500">
                            <p>No saved interactions yet.</p>
                            <p className="text-sm mt-2">
                                Complete an analysis to save it here.
                            </p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {history.map((item) => (
                                <div
                                    key={item.id}
                                    className="border border-gray-800 rounded-lg p-3 bg-black/40 hover:bg-gray-900/60 transition-colors"
                                >
                                    <div className="flex justify-between items-start mb-2">
                                        <h3 className="font-medium text-cyan-300 truncate max-w-[70%]">
                                            {item.prompt.substring(0, 60)}
                                            {item.prompt.length > 60 ? '...' : ''}
                                        </h3>
                                        <div className="flex items-center">
                                            <span className="text-xs text-gray-500 mr-2">
                                                {new Date(item.timestamp).toLocaleString()}
                                            </span>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="h-7 w-7 p-0 text-blue-400 hover:text-blue-300 hover:bg-blue-950/30"
                                                onClick={() => onShareItem(item)}
                                                title="Share"
                                            >
                                                <Share2 className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="h-7 w-7 p-0 text-cyan-400 hover:text-cyan-300 hover:bg-cyan-950/30"
                                                onClick={() => onLoadItem(item)}
                                                title="Load"
                                            >
                                                <FileText className="h-4 w-4" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="h-7 w-7 p-0 text-red-400 hover:text-red-300 hover:bg-red-950/30"
                                                onClick={() => onDeleteItem(item.id)}
                                                title="Delete"
                                            >
                                                <Trash2 className="h-4 w-4" />
                                            </Button>
                                        </div>
                                    </div>

                                    <div className="text-sm text-gray-400 mb-2 truncate">
                                        {item.output.substring(0, 80)}
                                        {item.output.length > 80 ? '...' : ''}
                                    </div>

                                    <div className="flex flex-wrap items-center mt-2 text-xs">
                                        <span className="bg-cyan-900/40 text-cyan-300 px-2 py-1 rounded-full mr-2 mb-1">
                                            {(item.models || []).length} models
                                        </span>
                                        {item.usingDocuments && (
                                            <span className="bg-blue-900/40 text-blue-300 px-2 py-1 rounded-full mr-2 mb-1">
                                                {(item.documents || []).length} documents
                                            </span>
                                        )}
                                        {/* Show indicator if this item has been shared */}
                                        {sharedItems.some((shared) => shared.id === item.id) && (
                                            <span className="bg-purple-900/40 text-purple-300 px-2 py-1 rounded-full mr-2 mb-1 flex items-center">
                                                <Share2 className="h-3 w-3 mr-1" /> Shared
                                            </span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default HistoryPanel;