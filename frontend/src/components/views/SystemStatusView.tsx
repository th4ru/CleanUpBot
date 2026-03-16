import { Activity, Monitor, Cpu, MemoryStick, Loader } from 'lucide-react';
import { useState, useEffect } from 'react';

interface SystemInfo {
  id: string;
  pcName: string;
  status: 'online' | 'offline';
  uptime: string;
  cpu: number;
  memory: number;
  lastSeen: string;
  ipAddress: string;
}

interface BackendSystemPC {
  id: number;
  pcName: string;
  ipAddress: string;
  status: string;
  lastSeen: string;
}

interface BackendSystemStatus {
  status: string;
  uptime?: string;
  cpuUsage?: number;
  memoryInfo?: {
    used?: string;
  };
}

const getBackendUrl = () => process.env.VITE_API_URL || 'http://localhost:5000/api';

async function fetchSystemsWithStatus(): Promise<SystemInfo[]> {
  try {
    const response = await fetch(`${getBackendUrl()}/systems`);
    const data = await response.json();
    
    if (!data.success || !data.data) {
      return [];
    }
    
    const systems: BackendSystemPC[] = data.data;
    const systemsWithStatus = await Promise.all(
      systems.map(async (system) => {
        try {
          const statusResponse = await fetch(`${getBackendUrl()}/systems/${system.id}/status`);
          const statusData = await statusResponse.json();
          
          if (statusData.success && statusData.data) {
            const status = statusData.data;
            return {
              id: system.id.toString(),
              pcName: system.pcName,
              ipAddress: system.ipAddress,
              status: status.status as 'online' | 'offline',
              uptime: status.uptime || 'Unknown',
              cpu: Math.round(status.cpuUsage || 0),
              memory: 50, // Default fallback
              lastSeen: system.lastSeen.includes('T') ? 'Active now' : system.lastSeen,
            };
          }
        } catch (error) {
          console.error(`Error fetching status for ${system.pcName}:`, error);
        }
        
        return {
          id: system.id.toString(),
          pcName: system.pcName,
          ipAddress: system.ipAddress,
          status: (system.status as 'online' | 'offline') || 'offline',
          uptime: 'Unknown',
          cpu: 0,
          memory: 0,
          lastSeen: 'Unknown',
        };
      })
    );
    
    return systemsWithStatus.filter((s) => s !== null) as SystemInfo[];
  } catch (error) {
    console.error('Error fetching systems:', error);
    return [];
  }
}

function SystemStatusView() {
  const [systems, setSystems] = useState<SystemInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadSystems();
  }, []);

  const loadSystems = async () => {
    setLoading(true);
    setError(null);
    const data = await fetchSystemsWithStatus();
    if (data.length === 0) {
      setError('No systems found or failed to fetch system data');
    }
    setSystems(data);
    setLoading(false);
  };

  const onlineCount = systems.filter((system) => system.status === 'online').length;
  const offlineCount = systems.filter((system) => system.status === 'offline').length;

  const getResourceColor = (value: number) => {
    if (value >= 80) return 'text-red-400';
    if (value >= 60) return 'text-yellow-400';
    return 'text-green-400';
  };

  const getResourceBg = (value: number) => {
    if (value >= 80) return 'bg-red-500';
    if (value >= 60) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <Activity className="w-7 h-7 text-blue-500" />
            System Status Monitor
          </h2>
          <p className="text-gray-400 mt-1">Real-time status of all connected systems</p>
        </div>
        <button 
          onClick={loadSystems}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Loading...
            </>
          ) : (
            'Refresh Status'
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Systems</p>
              <p className="text-3xl font-bold text-white mt-1">{systems.length}</p>
            </div>
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <Monitor className="w-6 h-6 text-blue-400" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Online</p>
              <p className="text-3xl font-bold text-green-400 mt-1">{onlineCount}</p>
            </div>
            <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center">
              <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Offline</p>
              <p className="text-3xl font-bold text-red-400 mt-1">{offlineCount}</p>
            </div>
            <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
              <div className="w-3 h-3 bg-red-500 rounded-full" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Uptime Avg</p>
              <p className="text-xl font-bold text-white mt-1">5d 10h</p>
            </div>
            <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center">
              <Activity className="w-6 h-6 text-purple-400" />
            </div>
          </div>
        </div>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-4 text-red-400">
          {error}
        </div>
      )}

      {loading ? (
        <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-12 flex flex-col items-center justify-center gap-4">
          <Loader className="w-8 h-8 text-blue-400 animate-spin" />
          <p className="text-gray-400">Loading system data...</p>
        </div>
      ) : systems.length === 0 ? (
        <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-12 flex flex-col items-center justify-center gap-4">
          <Monitor className="w-8 h-8 text-gray-500" />
          <p className="text-gray-400">No systems available</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {systems.map((system) => (
          <div
            key={system.id}
            className={`bg-gray-800/50 rounded-xl p-6 border transition-all ${
              system.status === 'online'
                ? 'border-green-500/30 hover:border-green-500/50'
                : 'border-gray-700 opacity-75'
            }`}
          >
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div
                  className={`w-12 h-12 rounded-lg flex items-center justify-center ${
                    system.status === 'online' ? 'bg-green-500/20' : 'bg-gray-700'
                  }`}
                >
                  <Monitor
                    className={`w-6 h-6 ${system.status === 'online' ? 'text-green-400' : 'text-gray-500'}`}
                  />
                </div>
                <div>
                  <h3 className="text-white font-semibold text-lg">{system.pcName}</h3>
                  <p className="text-gray-400 text-sm">{system.ipAddress}</p>
                </div>
              </div>
              <div className="flex flex-col items-end gap-1">
                <span
                  className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-xs font-medium ${
                    system.status === 'online'
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                      : 'bg-red-500/20 text-red-400 border border-red-500/30'
                  }`}
                >
                  <div
                    className={`w-2 h-2 rounded-full ${
                      system.status === 'online' ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                    }`}
                  />
                  {system.status.toUpperCase()}
                </span>
                <span className="text-gray-500 text-xs">{system.lastSeen}</span>
              </div>
            </div>

            <div className="space-y-3">
              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-400 flex items-center gap-2">
                    <Cpu className="w-4 h-4" />
                    CPU Usage
                  </span>
                  <span className={`font-semibold ${getResourceColor(system.cpu)}`}>{system.cpu}%</span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getResourceBg(system.cpu)} transition-all`}
                    style={{ width: `${system.cpu}%` }}
                  />
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between text-sm mb-1">
                  <span className="text-gray-400 flex items-center gap-2">
                    <MemoryStick className="w-4 h-4" />
                    Memory Usage
                  </span>
                  <span className={`font-semibold ${getResourceColor(system.memory)}`}>{system.memory}%</span>
                </div>
                <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${getResourceBg(system.memory)} transition-all`}
                    style={{ width: `${system.memory}%` }}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between pt-2 border-t border-gray-700">
                <span className="text-gray-400 text-sm">System Uptime</span>
                <span className="text-white font-medium">{system.uptime}</span>
              </div>
            </div>
          </div>
        ))}
        </div>
      )}
    </div>
  );
}

export default SystemStatusView;
