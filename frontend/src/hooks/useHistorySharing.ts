import { useState, useEffect, useCallback } from 'react';

// Define types (consider moving to a shared types file)
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

export const useHistorySharing = () => {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [showHistory, setShowHistory] = useState<boolean>(false);
  const [sharedItems, setSharedItems] = useState<ShareItem[]>([]);
  const [showShareDialog, setShowShareDialog] = useState<boolean>(false);
  const [shareDialogItem, setShareDialogItem] = useState<HistoryItem | null>(
    null
  );
  const [shareUrl, setShareUrl] = useState<string>('');
  const [copySuccess, setCopySuccess] = useState<boolean>(false);

  // Load history from local storage on initial mount
  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem('ultraAiHistory');
      if (savedHistory) {
        setHistory(JSON.parse(savedHistory));
      }
    } catch (err) {
      console.error('Failed to load history:', err);
      localStorage.removeItem('ultraAiHistory');
    }
  }, []);

  // Load shared items from local storage on initial mount
  useEffect(() => {
    try {
      const savedSharedItems = localStorage.getItem('ultraAiSharedItems');
      if (savedSharedItems) {
        setSharedItems(JSON.parse(savedSharedItems));
      }
    } catch (err) {
      console.error('Failed to load shared items:', err);
      localStorage.removeItem('ultraAiSharedItems');
    }
  }, []);

  // Save history to local storage whenever it changes
  useEffect(() => {
    try {
      localStorage.setItem('ultraAiHistory', JSON.stringify(history));
    } catch (err) {
      console.error('Failed to save history:', err);
    }
  }, [history]);

  // Save shared items to local storage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('ultraAiSharedItems', JSON.stringify(sharedItems));
    } catch (err) {
      console.error('Failed to save shared items:', err);
    }
  }, [sharedItems]);

  // Generate a unique share ID
  const generateShareId = useCallback((): string => {
    return (
      Math.random().toString(36).substring(2, 15) +
      Math.random().toString(36).substring(2, 15)
    );
  }, []);

  // Save current interaction to history
  const saveToHistory = useCallback(
    (item: HistoryItem) => {
      if (!item.prompt || !item.output) return;

      const updatedHistory = [item, ...history].slice(0, 50); // Keep most recent 50
      setHistory(updatedHistory);

      try {
        localStorage.setItem('ultraAiHistory', JSON.stringify(updatedHistory));
      } catch (err) {
        console.error('Failed to save history:', err);
      }
    },
    [history]
  );

  // Function called by component when history item is loaded
  // Returns the item so component can update other states
  const loadFromHistory = useCallback((item: HistoryItem) => {
    setShareDialogItem(null);
    setShowHistory(false);
    return item;
  }, []);

  // Delete a history item
  const deleteHistoryItem = useCallback(
    (id: string) => {
      const updatedHistory = history.filter(item => item.id !== id);
      setHistory(updatedHistory);

      try {
        localStorage.setItem('ultraAiHistory', JSON.stringify(updatedHistory));
      } catch (err) {
        console.error('Failed to save updated history:', err);
      }
    },
    [history]
  );

  // Clear all history
  const clearHistory = useCallback(() => {
    setHistory([]);
    localStorage.removeItem('ultraAiHistory');
    setShowHistory(false);
  }, []);

  // Prepare and show the share dialog
  const shareHistoryItem = useCallback(
    (item: HistoryItem) => {
      setShareDialogItem(item);

      // Check if this item has already been shared
      const existingShare = sharedItems.find(shared => shared.id === item.id);

      if (existingShare) {
        setShareUrl(existingShare.shareUrl);
      } else {
        const shareId = generateShareId();
        const newShareUrl = `${window.location.origin}/share/${shareId}`;
        setShareUrl(newShareUrl);

        const sharedItem: ShareItem = {
          ...item,
          shareId,
          shareUrl: newShareUrl,
          createdAt: new Date().toISOString(),
        };

        const updatedSharedItems = [...sharedItems, sharedItem];
        setSharedItems(updatedSharedItems);

        try {
          localStorage.setItem(
            'ultraAiSharedItems',
            JSON.stringify(updatedSharedItems)
          );
        } catch (err) {
          console.error('Failed to save shared items:', err);
        }
      }

      setShowShareDialog(true);
    },
    [sharedItems, generateShareId]
  );

  // Copy share URL to clipboard
  const copyToClipboard = useCallback(() => {
    navigator.clipboard
      .writeText(shareUrl)
      .then(() => {
        setCopySuccess(true);
        setTimeout(() => setCopySuccess(false), 2000);
      })
      .catch(err => {
        console.error('Failed to copy:', err);
      });
  }, [shareUrl]);

  return {
    history,
    showHistory,
    setShowHistory,
    sharedItems,
    showShareDialog,
    setShowShareDialog,
    shareDialogItem,
    shareUrl,
    copySuccess,
    setCopySuccess,
    saveToHistory,
    loadFromHistory,
    deleteHistoryItem,
    clearHistory,
    shareHistoryItem,
    copyToClipboard,
  };
};
