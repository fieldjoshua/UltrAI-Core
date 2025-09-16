import { memo } from 'react';

interface DemoQueryTemplatesProps {
  onSelectQuery: (query: string) => void;
  currentQuery: string;
}

const DEMO_QUERIES = [
  {
    category: 'Business Analysis',
    icon: '📊',
    queries: [
      'Analyze the market opportunity for AI-powered educational tools targeting K-12 schools',
      'Create a comprehensive business plan for a sustainable fashion marketplace',
      'Evaluate the competitive landscape for electric vehicle charging networks',
    ],
  },
  {
    category: 'Technical',
    icon: '🔧',
    queries: [
      'Design a scalable microservices architecture for a real-time collaboration platform',
      'Compare different approaches to implementing real-time data synchronization',
      'Create a technical roadmap for migrating from monolith to microservices',
    ],
  },
  {
    category: 'Creative',
    icon: '🎨',
    queries: [
      'Write a compelling pitch deck narrative for an AI mental health startup',
      'Create a brand strategy for a Gen-Z focused financial app',
      'Develop a content marketing strategy for a B2B SaaS platform',
    ],
  },
  {
    category: 'Research',
    icon: '🔬',
    queries: [
      'Analyze the ethical implications of AGI development',
      'Research the future of quantum computing in cryptography',
      'Investigate the impact of remote work on urban development',
    ],
  },
];

const DemoQueryTemplates = memo(function DemoQueryTemplates({
  onSelectQuery,
  currentQuery,
}: DemoQueryTemplatesProps) {
  return (
    <div className="space-y-4">
      <div className="text-xs text-white/60 text-center mb-4">
        Try one of these example queries:
      </div>

      <div className="grid grid-cols-2 gap-4">
        {DEMO_QUERIES.map((category, idx) => (
          <div key={idx} className="space-y-2">
            <div className="flex items-center gap-2 text-sm font-semibold text-white/80">
              <span>{category.icon}</span>
              <span>{category.category}</span>
            </div>

            <div className="space-y-1">
              {category.queries.map((query, qIdx) => (
                <button
                  key={qIdx}
                  onClick={() => onSelectQuery(query)}
                  className={`w-full text-left p-2 rounded-lg text-xs transition-all duration-200 ${
                    currentQuery === query
                      ? 'bg-gradient-to-r from-pink-500/20 to-purple-500/20 border border-pink-500/30 text-white'
                      : 'bg-white/5 hover:bg-white/10 border border-white/10 text-white/70 hover:text-white'
                  }`}
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="text-center mt-6">
        <div className="text-[10px] text-white/50">
          Or type your own query above
        </div>
      </div>
    </div>
  );
});

export default DemoQueryTemplates;
