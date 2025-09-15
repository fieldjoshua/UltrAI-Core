import React, { useState } from 'react';
import { Card } from './ui/card';
import { ChevronUp, ChevronDown } from 'lucide-react';

interface ReceiptItem {
  label: string;
  cost: number;
  color: string;
  section: string;
}

interface CollapsibleReceiptProps {
  items: ReceiptItem[];
  totalCost: number;
  isProcessing: boolean;
  children?: React.ReactNode;
  monoStack: string;
  colorHex: string;
  receiptColor: string;
}

export const CollapsibleReceipt: React.FC<CollapsibleReceiptProps> = ({
  items,
  totalCost,
  isProcessing,
  children,
  monoStack,
  colorHex,
  receiptColor,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 1024;

  // Group items by section
  const sections = items.reduce((acc, item) => {
    if (!acc[item.section]) {
      acc[item.section] = [];
    }
    acc[item.section].push(item);
    return acc;
  }, {} as Record<string, ReceiptItem[]>);

  return (
    <Card 
      className={`relative rounded-2xl transition-smooth ${isCollapsed ? 'receipt-collapsed' : ''}`}
      style={{ 
        fontFamily: monoStack, 
        background: 'rgba(0, 0, 0, 0.1)',
        backdropFilter: 'blur(40px)',
        WebkitBackdropFilter: 'blur(40px)',
        border: `2px solid ${receiptColor}`,
        minHeight: isCollapsed ? '80px' : '420px',
        width: '100%',
        boxShadow: `
          0 8px 32px rgba(0, 0, 0, 0.3),
          0 0 60px ${receiptColor}10,
          0 0 0 1px ${receiptColor}20,
          inset 0 0 60px rgba(255, 255, 255, 0.05)
        `,
        clipPath: isMobile ? 'none' : 'polygon(0 0, calc(100% - 20px) 0, 100% 20px, 100% 100%, 20px 100%, 0 calc(100% - 20px))'
      }}>
      
      {/* Mobile collapse toggle */}
      {isMobile && (
        <button
          onClick={() => setIsCollapsed(!isCollapsed)}
          className="w-full flex items-center justify-between p-4 text-white hover:bg-white/5 transition-colors"
          aria-expanded={!isCollapsed}
          aria-label={isCollapsed ? 'Expand receipt' : 'Collapse receipt'}
        >
          <div className="flex items-center gap-3">
            <span className="text-sm font-bold">RECEIPT</span>
            <span className="text-lg font-bold text-pink-400">${totalCost.toFixed(2)}</span>
          </div>
          {isCollapsed ? (
            <ChevronUp className="w-5 h-5" />
          ) : (
            <ChevronDown className="w-5 h-5" />
          )}
        </button>
      )}

      {/* Receipt content */}
      <div className={`${isMobile && isCollapsed ? 'hidden' : ''} ${isMobile ? 'px-4 pb-4' : 'p-6'}`}>
        {!isProcessing ? (
          <>
            <div className="text-center mb-2">
              <div className="text-[14px] font-extrabold tracking-[0.35em] text-white">ULTRAI</div>
              <div className="text-[10px] text-white/70">— ITEMIZED RECEIPT —</div>
            </div>
            
            <div className="space-y-2" style={{ 
              maxHeight: isMobile ? '250px' : '360px', 
              overflowY: 'auto', 
              paddingRight: 6 
            }}>
              {Object.entries(sections).map(([sectionTitle, sectionItems]) => (
                <div key={sectionTitle}>
                  <div className="uppercase text-[10px] tracking-wider mb-1 text-center text-white/80">
                    {sectionTitle}
                  </div>
                  {sectionItems.map((item, i) => (
                    <div 
                      key={i} 
                      className="text-[10px] leading-tight flex items-center text-white hover:text-white transition-colors duration-200 group cursor-pointer glass-text-fix"
                    >
                      <span 
                        className="flex-auto overflow-hidden text-ellipsis whitespace-nowrap group-hover:text-shadow-sm" 
                        title={item.label}
                      >
                        {item.label}
                      </span>
                      <span className="px-1 select-none opacity-50 group-hover:opacity-70 hidden sm:inline">
                        . . . . . . . . . . .
                      </span>
                      <span className="text-right w-14 group-hover:text-pink-400 transition-colors">
                        ${item.cost.toFixed(2)}
                      </span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
            
            <div 
              className="mt-3 font-bold text-pink-400 text-lg text-center transition-all duration-300 hover:scale-105" 
              style={{
                textShadow: 'var(--shadow-text-glow, 0 0 10px currentColor)'
              }}
            >
              Total: ${totalCost.toFixed(2)}
            </div>
            
            {children}
          </>
        ) : (
          <>
            <div className="text-center mb-2">
              <div className="text-[14px] font-extrabold tracking-[0.35em] text-white">ULTRAI</div>
              <div className="text-[10px] text-white/70">— PROCESSING —</div>
            </div>
            <div className="text-center mt-8">
              <div className="text-[12px] text-white/60">Ultra Synthesis™ in progress</div>
              <div className="text-[10px] text-white/40 mt-2">Check the status in the main panel</div>
            </div>
          </>
        )}
      </div>
    </Card>
  );
};

export default CollapsibleReceipt;