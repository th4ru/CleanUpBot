import { Power, PowerOff, HardDrive, Trash2, Activity } from 'lucide-react';

type ViewType = 'welcome' | 'disk-space' | 'cleanup' | 'system-status';

interface SidebarProps {
  isBotActive: boolean;
  currentView: ViewType;
  onStartBot: () => void;
  onStopBot: () => void;
  onViewChange: (view: ViewType) => void;
}

function Sidebar({ isBotActive, currentView, onStartBot, onStopBot, onViewChange }: SidebarProps) {
  return (
    <aside className="w-64 bg-gray-950 border-r border-gray-800 flex flex-col">
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
            <Activity className="w-6 h-6 text-white" />
          </div>
          <div>
            <h2 className="font-bold text-lg text-white">Remote Bot</h2>
            <p className="text-xs text-gray-400">Admin Panel</p>
          </div>
        </div>
      </div>

      <nav className="flex-1 p-4 space-y-2">
        <button
          onClick={onStartBot}
          disabled={isBotActive}
          className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all ${
            isBotActive
              ? 'bg-green-500/20 text-green-400 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-500 text-white shadow-lg hover:shadow-green-500/20'
          }`}
        >
          <Power className="w-5 h-5" />
          <span>{isBotActive ? 'Bot Active' : 'Start Bot'}</span>
        </button>

        {isBotActive && (
          <div className="pt-2 space-y-2 animate-fadeIn">
            <button
              onClick={() => onViewChange('disk-space')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all ${
                currentView === 'disk-space'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white'
              }`}
            >
              <HardDrive className="w-5 h-5" />
              <span>Disk Space</span>
            </button>

            <button
              onClick={() => onViewChange('cleanup')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all ${
                currentView === 'cleanup'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white'
              }`}
            >
              <Trash2 className="w-5 h-5" />
              <span>Cleanup</span>
            </button>

            <button
              onClick={() => onViewChange('system-status')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-all ${
                currentView === 'system-status'
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-gray-800 hover:bg-gray-700 text-gray-300 hover:text-white'
              }`}
            >
              <Activity className="w-5 h-5" />
              <span>System Status</span>
            </button>
          </div>
        )}

        {isBotActive && (
          <div className="pt-4">
            <button
              onClick={onStopBot}
              className="w-full flex items-center gap-3 px-4 py-3 rounded-lg font-medium bg-red-600 hover:bg-red-500 text-white transition-all shadow-lg hover:shadow-red-500/20"
            >
              <PowerOff className="w-5 h-5" />
              <span>Stop Bot</span>
            </button>
          </div>
        )}
      </nav>

      <div className="p-4 border-t border-gray-800">
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <div className={`w-2 h-2 rounded-full ${isBotActive ? 'bg-green-500' : 'bg-gray-600'}`} />
          <span>{isBotActive ? 'System Online' : 'System Offline'}</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
