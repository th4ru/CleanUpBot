import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import DashboardContent from './components/DashboardContent';

type ViewType = 'welcome' | 'disk-space' | 'cleanup' | 'system-status';

function App() {
  const [isBotActive, setIsBotActive] = useState(false);
  const [currentView, setCurrentView] = useState<ViewType>('welcome');

  const handleStartBot = () => {
    setIsBotActive(true);
    setCurrentView('welcome');
  };

  const handleStopBot = () => {
    setIsBotActive(false);
    setCurrentView('welcome');
  };

  const handleViewChange = (view: ViewType) => {
    setCurrentView(view);
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100">
      <Sidebar
        isBotActive={isBotActive}
        currentView={currentView}
        onStartBot={handleStartBot}
        onStopBot={handleStopBot}
        onViewChange={handleViewChange}
      />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6">
          <DashboardContent view={currentView} isBotActive={isBotActive} />
        </main>
      </div>
    </div>
  );
}

export default App;
