import React from 'react';

export interface ReceiptItem {
  label: string;
  amount: number;
}

export interface ReceiptProps {
  items: ReceiptItem[];
  total: number;
}

const Receipt: React.FC<ReceiptProps> = ({ items, total }) => {
  return (
    <section aria-label="Receipt" className="rounded-md border bg-background p-4 space-y-4">
      <h3 className="font-semibold text-lg">Receipt</h3>
      <ul className="space-y-2 text-sm">
        {items.map((it, i) => (
          <li key={`${it.label}-${i}`} className="flex justify-between">
            <span className="text-muted-foreground">{it.label}</span>
            <span className="font-mono">${it.amount.toFixed(2)}</span>
          </li>
        ))}
      </ul>
      <div className="flex justify-between pt-2 border-t">
        <span className="font-medium">Total</span>
        <span className="font-bold">${total.toFixed(2)}</span>
      </div>
    </section>
  );
};

export default Receipt;


