import WelcomeView from './views/WelcomeView';
import DiskSpaceView from './views/DiskSpaceView';
import CleanupView from './views/CleanupView';
import SystemStatusView from './views/SystemStatusView';

type ViewType = 'welcome' | 'disk-space' | 'cleanup' | 'system-status';

interface DashboardContentProps {
  view: ViewType;
  isBotActive: boolean;
}

function DashboardContent({ view, isBotActive }: DashboardContentProps) {
  if (!isBotActive && view === 'welcome') {
    return <WelcomeView />;
  }

  switch (view) {
    case 'disk-space':
      return <DiskSpaceView />;
    case 'cleanup':
      return <CleanupView />;
    case 'system-status':
      return <SystemStatusView />;
    default:
      return <WelcomeView />;
  }
}

export default DashboardContent;
