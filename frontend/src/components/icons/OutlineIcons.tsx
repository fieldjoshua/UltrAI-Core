import {
  Microscope,
  PenTool,
  FileText,
  Code2,
  TrendingUp,
  Palette,
  BookOpen,
  LineChart,
  Sparkles,
  Rocket,
  Upload,
  Target,
  Shield,
  Swords,
  GitBranch,
  DollarSign,
  Zap,
  Coins,
  Check,
  Brain,
  Share2,
  Edit3,
  FileCheck,
  BarChart,
  FlaskConical,
  FileType,
  Copy,
  Download,
  Settings,
  Globe,
  Image,
  Users,
  RotateCw,
  Mail,
  Layers,
  Type,
  Bot,
  Clock,
  Crosshair,
  Stars,
  RefreshCw,
  LucideIcon,
} from 'lucide-react';

interface IconProps {
  className?: string;
  size?: number;
}

// Goal icons mapping
export const goalIcons: Record<string, LucideIcon> = {
  Research: Microscope,
  'Writing/Editing': PenTool,
  'Document Analysis': FileText,
  'Code Creation': Code2,
  'Business Strategy': TrendingUp,
  'Creative Projects': Palette,
  'Learning & Education': BookOpen,
  'Data Analysis': LineChart,
  Other: Sparkles,
};

// Analysis type icons
export const analysisIcons: Record<string, LucideIcon> = {
  'UltrAI Intelligence Multiplier': Rocket,
  'Fact-check & Confidence': Shield,
  "Devil's Advocate": Swords,
  'Convergence/Divergence': GitBranch,
};

// Model selection icons
export const modelIcons: Record<string, LucideIcon> = {
  Premium: Target,
  Speed: Zap,
  Budget: Coins,
  Cost: DollarSign,
};

// Add-on icons
export const addonIcons: Record<string, LucideIcon> = {
  'Export as PDF/Word': FileType,
  'Priority Processing': Zap,
  'Advanced Formatting': Type,
  'Source Citations': BookOpen,
  'Multi-Language': Globe,
  'Visual Diagrams': BarChart,
  'Email Summary': Mail,
  'Version History': RotateCw,
  'Team Collaboration': Users,
};

// Processing status icons
export const statusIcons: Record<string, LucideIcon> = {
  boot: Rocket,
  submit: Upload,
  initial: Brain,
  distribute: Share2,
  revise: Edit3,
  meta_submit: FileCheck,
  meta_analyze: FlaskConical,
  write: FileType,
  'Models Used': Bot,
  'Processing Time': Clock,
  Pattern: Crosshair,
  Enhanced: Stars,
};

// UI action icons
export const actionIcons: Record<string, LucideIcon> = {
  copy: Copy,
  download: Download,
  settings: Settings,
  check: Check,
  Results: FileText,
  Restart: RefreshCw,
};

// Helper component to render icons
export const OutlineIcon: React.FC<{
  name: string;
  category?: 'goal' | 'analysis' | 'model' | 'addon' | 'status' | 'action';
  className?: string;
  size?: number;
}> = ({ name, category = 'goal', className = '', size = 20 }) => {
  let Icon: LucideIcon | undefined;

  switch (category) {
    case 'goal':
      Icon = goalIcons[name];
      break;
    case 'analysis':
      Icon = analysisIcons[name];
      break;
    case 'model':
      Icon = modelIcons[name];
      break;
    case 'addon':
      Icon = addonIcons[name];
      break;
    case 'status':
      Icon = statusIcons[name];
      break;
    case 'action':
      Icon = actionIcons[name];
      break;
  }

  if (!Icon) {
    return <Sparkles className={className} size={size} />;
  }

  return <Icon className={className} size={size} />;
};
