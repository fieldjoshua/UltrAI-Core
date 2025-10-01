import { renderHook, act } from '@testing-library/react';
import { useReceipt, ReceiptItem } from '../../hooks/useReceipt';

const mockItem1: ReceiptItem = {
  id: 'item-1',
  label: 'Deep analysis',
  cost: 0.08,
  category: 'goal',
};

const mockItem2: ReceiptItem = {
  id: 'item-2',
  label: 'UltrAI Multiplier',
  cost: 0.10,
  category: 'analysis',
};

const mockItem3: ReceiptItem = {
  id: 'item-3',
  label: 'Premium Models',
  cost: 0.50,
  category: 'model',
};

describe('useReceipt', () => {
  it('initializes with empty items', () => {
    const { result } = renderHook(() => useReceipt());
    
    expect(result.current.items).toEqual([]);
    expect(result.current.total).toBe(0);
    expect(result.current.count).toBe(0);
  });

  it('adds items to receipt', () => {
    const { result } = renderHook(() => useReceipt());
    
    act(() => {
      result.current.addItem(mockItem1);
    });
    
    expect(result.current.items).toHaveLength(1);
    expect(result.current.items[0]).toEqual(mockItem1);
    expect(result.current.count).toBe(1);
  });

  it('calculates total correctly', () => {
    const { result } = renderHook(() => useReceipt());
    
    act(() => {
      result.current.addItem(mockItem1);
      result.current.addItem(mockItem2);
    });
    
    expect(result.current.total).toBeCloseTo(0.18, 2);
  });

  it('removes items from receipt', () => {
    const { result } = renderHook(() => useReceipt());
    
    act(() => {
      result.current.addItem(mockItem1);
      result.current.addItem(mockItem2);
    });
    
    act(() => {
      result.current.removeItem('item-1');
    });
    
    expect(result.current.items).toHaveLength(1);
    expect(result.current.items[0].id).toBe('item-2');
    expect(result.current.total).toBeCloseTo(0.10, 2);
  });

  it('toggles items (add if not exists, remove if exists)', () => {
    const { result } = renderHook(() => useReceipt());
    
    // Add via toggle
    act(() => {
      result.current.toggleItem(mockItem1);
    });
    expect(result.current.items).toHaveLength(1);
    
    // Remove via toggle
    act(() => {
      result.current.toggleItem(mockItem1);
    });
    expect(result.current.items).toHaveLength(0);
  });

  it('replaces item with same ID when adding', () => {
    const { result } = renderHook(() => useReceipt());
    
    act(() => {
      result.current.addItem(mockItem1);
    });
    
    const updatedItem = { ...mockItem1, cost: 0.15 };
    
    act(() => {
      result.current.addItem(updatedItem);
    });
    
    expect(result.current.items).toHaveLength(1);
    expect(result.current.items[0].cost).toBe(0.15);
  });

  it('clears all items', () => {
    const { result } = renderHook(() => useReceipt());
    
    act(() => {
      result.current.addItem(mockItem1);
      result.current.addItem(mockItem2);
      result.current.addItem(mockItem3);
    });
    
    act(() => {
      result.current.clear();
    });
    
    expect(result.current.items).toHaveLength(0);
    expect(result.current.total).toBe(0);
  });

  it('groups items by category', () => {
    const { result } = renderHook(() => useReceipt());
    
    act(() => {
      result.current.addItem(mockItem1);
      result.current.addItem(mockItem2);
      result.current.addItem(mockItem3);
    });
    
    expect(result.current.itemsByCategory.goal).toHaveLength(1);
    expect(result.current.itemsByCategory.analysis).toHaveLength(1);
    expect(result.current.itemsByCategory.model).toHaveLength(1);
    expect(result.current.itemsByCategory.addon).toHaveLength(0);
  });

  it('handles multiple items of same category', () => {
    const { result } = renderHook(() => useReceipt());
    
    const addon1: ReceiptItem = {
      id: 'addon-1',
      label: 'Citations',
      cost: 0.05,
      category: 'addon',
    };
    
    const addon2: ReceiptItem = {
      id: 'addon-2',
      label: 'Summary',
      cost: 0.03,
      category: 'addon',
    };
    
    act(() => {
      result.current.addItem(addon1);
      result.current.addItem(addon2);
    });
    
    expect(result.current.itemsByCategory.addon).toHaveLength(2);
    expect(result.current.total).toBeCloseTo(0.08, 2);
  });
});
