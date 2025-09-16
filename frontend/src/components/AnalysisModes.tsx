interface AnalysisMode {
  label: string;
  icon: string;
  description: string;
}

interface Props {
  options: AnalysisMode[];
  selected: string[];
  onToggle: (label: string) => void;
}

export default function AnalysisModes({ options, selected, onToggle }: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
      {options.map(opt => (
        <div
          key={opt.label}
          className={`glass border-2 rounded-xl p-2 cursor-pointer transition-all animate-border-hum
            ${
              selected.includes(opt.label)
                ? 'shadow-neon-pink border-pink-400'
                : 'hover:shadow-neon-blue border-white/20'
            }`}
          onClick={() => onToggle(opt.label)}
        >
          <div className="flex items-start gap-2">
            <div className="text-base">{opt.icon}</div>
            <div>
              <h3 className="font-bold text-[11px] leading-tight">
                {opt.label}
              </h3>
              <p className="text-[10px] text-foreground/80 leading-snug">
                {opt.description}
              </p>
            </div>
          </div>
          <div className="mt-2 text-right">
            <input
              type="checkbox"
              checked={selected.includes(opt.label)}
              readOnly
              className="accent-pink-500 scale-90 cursor-pointer"
            />
          </div>
        </div>
      ))}
    </div>
  );
}
