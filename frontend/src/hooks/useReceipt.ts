import { useState, useCallback, useMemo } from 'react';

export interface ReceiptItem {
  id: string;
  label: string;
  cost: number;
  category: 'goal' | 'analysis' | 'model' | 'addon';
}

export function useReceipt() {
  const [items, setItems] = useState<ReceiptItem[]>([]);

  const addItem = useCallback((item: ReceiptItem) => {
    setItems(prev => {
      // Remove existing item with same ID if exists
      const filtered = prev.filter(i => i.id !== item.id);
      return [...filtered, item];
    });
  }, []);

  const removeItem = useCallback((id: string) => {
    setItems(prev => prev.filter(i => i.id !== id));
  }, []);

  const toggleItem = useCallback((item: ReceiptItem) => {
    setItems(prev => {
      const exists = prev.find(i => i.id === item.id);
      if (exists) {
        return prev.filter(i => i.id !== item.id);
      }
      return [...prev, item];
    });
  }, []);

  const clear = useCallback(() => {
    setItems([]);
  }, []);

  const total = useMemo(() => 
    items.reduce((sum, item) => sum + item.cost, 0),
    [items]
  );

  const itemsByCategory = useMemo(() => {
    const categories: Record<string, ReceiptItem[]> = {
      goal: [],
      analysis: [],
      model: [],
      addon: [],
    };
    items.forEach(item => {
      categories[item.category].push(item);
    });
    return categories;
  }, [items]);

  const count = items.length;

  return {
    items,
    addItem,
    removeItem,
    toggleItem,
    clear,
    total,
    itemsByCategory,
    count,
  };
}
