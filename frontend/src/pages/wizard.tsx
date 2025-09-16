import CyberWizard from '@components/wizard/CyberWizard';
import { PageErrorBoundary } from '@components/PageErrorBoundary';

export default function WizardPage() {
  return (
    <PageErrorBoundary pageName="Wizard">
      <CyberWizard />
    </PageErrorBoundary>
  );
}
