interface Option {
  label: string;
  icon?: string;
  description?: string;
  cost?: number;
}

interface Props {
  options: Option[];
  selected: string[];
  onToggle: (label: string) => void;
  multi?: boolean; // allow multiple (checkbox) vs single (radio)
}

export default function OptionCards({
  options,
  selected,
  onToggle,
  multi = true,
}: Props) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
      {options.map(opt => (
        <div
          key={opt.label}
          className={`glass border-2 rounded-xl p-2 cursor-pointer transition-all animate-border-hum
            ${
              selected.includes(opt.label)
                ? 'shadow-neon-mint border-mint-400'
                : 'hover:shadow-neon-blue border-white/20'
            }`}
          onClick={() => onToggle(opt.label)}
        >
          <div className="flex items-start gap-2">
            <div className="text-base">{opt.icon || '⬜'}</div>
            <div>
              <h3 className="font-bold text-[11px] leading-tight">
                {opt.label}
              </h3>
              {opt.description && (
                <p className="text-[10px] text-foreground/80 leading-snug">
                  {opt.description}
                </p>
              )}
              {opt.cost !== undefined && (
                <p className="text-[10px] text-pink-400 mt-1">
                  +${opt.cost.toFixed(2)}
                </p>
              )}
            </div>
          </div>
          <div className="mt-2 text-right">
            <input
              type={multi ? 'checkbox' : 'radio'}
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
