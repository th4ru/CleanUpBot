import { HardDrive, AlertTriangle, Loader } from 'lucide-react';
import { useState, useEffect } from 'react';

interface DiskData {
  id: string;
  pcName: string;
  totalSpace: string;
  usedSpace: string;
  freeSpace: string;
  usagePercent: number;
  status: 'healthy' | 'warning' | 'critical';
}

interface SystemPC {
  id: number;
  pcName: string;
}

interface BackendDiskInfo {
  filesystem: string;
  total: string;
  used: string;
  available: string;
  usage_percent: number;
  mount_point: string;
}

const getBackendUrl = () => 'http://localhost:5000/api';

const getStatusFromPercent = (percent: number): 'healthy' | 'warning' | 'critical' => {
  if (percent >= 90) return 'critical';
  if (percent >= 75) return 'warning';
  return 'healthy';
};

async function fetchSystemsAndDiskData(): Promise<DiskData[]> {
  try {
    const systemsResponse = await fetch(`${getBackendUrl()}/systems`);
    const systemsData = await systemsResponse.json();
    
    if (!systemsData.success || !systemsData.data) {
      return [];
    }
    
    const systems: SystemPC[] = systemsData.data;
    const diskDataPromises = systems.map(async (system) => {
      try {
        const diskResponse = await fetch(`${getBackendUrl()}/systems/${system.id}/disk-space`);
        const diskResult = await diskResponse.json();
        
        if (diskResult.success && diskResult.data && diskResult.data.length > 0) {
          const mainDisk: BackendDiskInfo = diskResult.data[0];
          return {
            id: system.id.toString(),
            pcName: system.pcName,
            totalSpace: mainDisk.total,
            usedSpace: mainDisk.used,
            freeSpace: mainDisk.available,
            usagePercent: mainDisk.usage_percent,
            status: getStatusFromPercent(mainDisk.usage_percent),
          };
        }
      } catch (error) {
        console.error(`Error fetching disk data for ${system.pcName}:`, error);
      }
      return null;
    });
    
    const results = await Promise.all(diskDataPromises);
    return results.filter((item): item is DiskData => item !== null);
  } catch (error) {
    console.error('Error fetching systems and disk data:', error);
    return [];
  }
}

function DiskSpaceView() {
  const [diskData, setDiskData] = useState<DiskData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadDiskData();
  }, []);

  const loadDiskData = async () => {
    setLoading(true);
    setError(null);
    const data = await fetchSystemsAndDiskData();
    if (data.length === 0) {
      setError('No systems found or failed to fetch disk data');
    }
    setDiskData(data);
    setLoading(false);
  };

  const handleRefresh = async () => {
    await loadDiskData();
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'warning':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'critical':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const getProgressColor = (percent: number) => {
    if (percent >= 90) return 'bg-red-500';
    if (percent >= 75) return 'bg-yellow-500';
    return 'bg-green-500';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <HardDrive className="w-7 h-7 text-blue-500" />
            Disk Space Overview
          </h2>
          <p className="text-gray-400 mt-1">Monitor disk usage across all connected systems</p>
        </div>
        <button 
          onClick={handleRefresh}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {loading ? (
            <>
              <Loader className="w-4 h-4 animate-spin" />
              Loading...
            </>
          ) : (
            'Refresh Data'
          )}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Systems</p>
              <p className="text-3xl font-bold text-white mt-1">{diskData.length}</p>
            </div>
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <HardDrive className="w-6 h-6 text-blue-400" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Warning Level</p>
              <p className="text-3xl font-bold text-yellow-400 mt-1">{diskData.filter(d => d.status === 'warning').length}</p>
            </div>
            <div className="w-12 h-12 bg-yellow-500/20 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-yellow-400" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Critical Level</p>
              <p className="text-3xl font-bold text-red-400 mt-1">{diskData.filter(d => d.status === 'critical').length}</p>
            </div>
            <div className="w-12 h-12 bg-red-500/20 rounded-lg flex items-center justify-center">
              <AlertTriangle className="w-6 h-6 text-red-400" />
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
          <p className="text-gray-400">Loading disk space data...</p>
        </div>
      ) : diskData.length === 0 ? (
        <div className="bg-gray-800/50 rounded-xl border border-gray-700 p-12 flex flex-col items-center justify-center gap-4">
          <HardDrive className="w-8 h-8 text-gray-500" />
          <p className="text-gray-400">No systems available</p>
        </div>
      ) : (
        <div className="bg-gray-800/50 rounded-xl border border-gray-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-900/50">
                <tr>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    PC Name
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Total Space
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Used Space
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Free Space
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Usage
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {diskData.map((disk: DiskData) => (
                  <tr key={disk.id} className="hover:bg-gray-900/30 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 bg-blue-500/20 rounded flex items-center justify-center">
                          <HardDrive className="w-4 h-4 text-blue-400" />
                        </div>
                        <span className="text-white font-medium">{disk.pcName}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-300">{disk.totalSpace}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-300">{disk.usedSpace}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-gray-300">{disk.freeSpace}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center gap-3">
                        <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                          <div
                            className={`h-full ${getProgressColor(disk.usagePercent)} transition-all`}
                            style={{ width: `${disk.usagePercent}%` }}
                          />
                        </div>
                        <span className="text-white font-medium w-12 text-right">{disk.usagePercent}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                          disk.status
                        )}`}
                      >
                        {disk.status.charAt(0).toUpperCase() + disk.status.slice(1)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

export default DiskSpaceView;
