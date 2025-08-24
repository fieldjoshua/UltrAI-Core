import React from 'react';
import type { ReceiptItem } from './GuidedChat';

export interface ReceiptPanelProps {
  items: ReceiptItem[];
  costCents: number;
  onLaunch?: () => void;
}

const ReceiptPanel: React.FC<ReceiptPanelProps> = ({ items, costCents, onLaunch }) => {
  const dollars = (costCents / 100).toFixed(2);
  return (
    <div className="rounded-md border bg-background p-4 space-y-4">
      <h3 className="font-semibold text-lg">Receipt</h3>
      <ul className="space-y-2 text-sm">
        {items.map((it) => (
          <li key={it.key} className="flex justify-between">
            <span className="text-muted-foreground">{it.key}</span>
            <span className="font-medium">{it.value || '-'}</span>
          </li>
        ))}
      </ul>
      <div className="flex justify-between pt-2 border-t">
        <span className="font-medium">Estimated Cost</span>
        <span>${dollars}</span>
      </div>
      <button className="w-full px-4 py-2 rounded bg-primary text-primary-foreground" onClick={onLaunch}>
        Initialize Query
      </button>
    </div>
  );
};

export default ReceiptPanel;


