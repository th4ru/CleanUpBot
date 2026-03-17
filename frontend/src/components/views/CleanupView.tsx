import { useState, useEffect } from 'react';
import { Trash2, Play, CheckCircle, Clock, XCircle, Loader } from 'lucide-react';

interface CleanupLog {
  id: string;
  timestamp: string;
  pcName: string;
  action: string;
  spaceFreed: string;
  status: 'success' | 'running' | 'failed';
}

interface BackendSystemPC {
  id: number;
  pcName: string;
}

interface BackendCleanupOp {
  id: number;
  systemId: number;
  cleanupType: string;
  status: string;
  startedAt: string;
  completedAt?: string;
}

const getBackendUrl = () =>  'http://localhost:5000/api';

async function fetchCleanupHistory(): Promise<CleanupLog[]> {
  try {
    // Fetch cleanup operations
    const response = await fetch(`${getBackendUrl()}/cleanup?limit=50`);
    const data = await response.json();
    
    if (!data.success || !data.data) {
      return [];
    }
    
    const operations: BackendCleanupOp[] = data.data;
    
    // Fetch systems to get names
    const systemsResponse = await fetch(`${getBackendUrl()}/systems`);
    const systemsData = await systemsResponse.json();
    const systemsMap = new Map(
      (systemsData.data || []).map((sys: BackendSystemPC) => [sys.id, sys.pcName])
    );
    
    return operations.map((op) => ({
      id: op.id.toString(),
      timestamp: new Date(op.startedAt).toLocaleString('en-US', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }),
      pcName: systemsMap.get(op.systemId) || `System ${op.systemId}`,
      action: `${op.cleanupType} cleanup ${op.status}`,
      spaceFreed: '...',
      status: op.status as 'success' | 'running' | 'failed',
    }));
  } catch (error) {
    console.error('Error fetching cleanup history:', error);
    return [];
  }
}

async function fetchAvailableSystems(): Promise<BackendSystemPC[]> {
  try {
    const response = await fetch(`${getBackendUrl()}/systems`);
    const data = await response.json();
    return data.success ? data.data : [];
  } catch (error) {
    console.error('Error fetching systems:', error);
    return [];
  }
}

function CleanupView() {
  const [systems, setSystems] = useState<BackendSystemPC[]>([]);
  const [logs, setLogs] = useState<CleanupLog[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);
  const [selectedSystemIds, setSelectedSystemIds] = useState<number[]>([]);
  const [cleanupType, setCleanupType] = useState<'cache' | 'temp' | 'logs' | 'all'>('all');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    const [systemsData, logsData] = await Promise.all([
      fetchAvailableSystems(),
      fetchCleanupHistory(),
    ]);
    setSystems(systemsData);
    setLogs(logsData);
    if (systemsData.length > 0) {
      setSelectedSystemIds([systemsData[0].id]);
    }
    setLoading(false);
  };

  const handleStartCleanup = async () => {
    if (selectedSystemIds.length === 0) {
      alert('Please select at least one system');
      return;
    }

    setIsRunning(true);
    
    try {
      const response = await fetch(`${getBackendUrl()}/cleanup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          pcIds: selectedSystemIds,
          cleanupType: cleanupType,
        }),
      });

      const result = await response.json();
      
      if (result.success && result.data) {
        // Add new operations to logs
        const newLogs = result.data.map((op: BackendCleanupOp) => {
          const systemName = systems.find(s => s.id === op.systemId)?.pcName || `System ${op.systemId}`;
          return {
            id: op.id.toString(),
            timestamp: new Date(op.startedAt).toLocaleString('en-US', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit',
              second: '2-digit',
            }),
            pcName: systemName,
            action: `Running ${op.cleanupType} cleanup...`,
            spaceFreed: '...',
            status: 'running' as const,
          };
        });

        setLogs([...newLogs, ...logs]);

        // Poll for updates
        const pollInterval = setInterval(async () => {
          const updatedLogs = await fetchCleanupHistory();
          setLogs(updatedLogs);
          
          // Check if any operations are still running
          const hasRunning = updatedLogs.some(log => log.status === 'running');
          if (!hasRunning) {
            clearInterval(pollInterval);
            setIsRunning(false);
          }
        }, 2000);
      }
    } catch (error) {
      console.error('Error starting cleanup:', error);
      setIsRunning(false);
      alert('Failed to start cleanup operation');
    }
  };

  const toggleSystemSelection = (systemId: number) => {
    setSelectedSystemIds(prev =>
      prev.includes(systemId)
        ? prev.filter(id => id !== systemId)
        : [...prev, systemId]
    );
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-400" />;
      case 'running':
        return <Clock className="w-5 h-5 text-blue-400 animate-spin" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-400" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'text-green-400';
      case 'running':
        return 'text-blue-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white flex items-center gap-3">
            <Trash2 className="w-7 h-7 text-blue-500" />
            System Cleanup
          </h2>
          <p className="text-gray-400 mt-1">Remove junk files and free up disk space</p>
        </div>
        <div className="flex gap-3">
          <select
            value={cleanupType}
            onChange={(e) => setCleanupType(e.target.value as any)}
            disabled={isRunning}
            className="px-3 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 disabled:opacity-50"
          >
            <option value="all">Full Cleanup</option>
          </select>
          <button
            onClick={handleStartCleanup}
            disabled={isRunning || selectedSystemIds.length === 0}
            className={`px-6 py-3 rounded-lg font-medium flex items-center gap-2 transition-all ${
              isRunning || selectedSystemIds.length === 0
                ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                : 'bg-green-600 hover:bg-green-500 text-white shadow-lg hover:shadow-green-500/20'
            }`}
          >
            {isRunning ? (
              <>
                <Clock className="w-5 h-5 animate-spin" />
                Running...
              </>
            ) : (
              <>
                <Play className="w-5 h-5" />
                Start Cleanup
              </>
            )}
          </button>
        </div>
      </div>

      {!loading && systems.length > 0 && (
        <div className="bg-gray-800/50 rounded-xl p-4 border border-gray-700">
          <p className="text-gray-400 text-sm mb-3">Select systems to clean:</p>
          <div className="flex flex-wrap gap-2">
            {systems.map((system) => (
              <label key={system.id} className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedSystemIds.includes(system.id)}
                  onChange={() => toggleSystemSelection(system.id)}
                  className="w-4 h-4"
                />
                <span className="text-white text-sm">{system.pcName}</span>
              </label>
            ))}
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Total Operations</p>
              <p className="text-2xl font-bold text-white mt-1">{logs.length}</p>
            </div>
            <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-blue-400" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Successful</p>
              <p className="text-2xl font-bold text-green-400 mt-1">{logs.filter(l => l.status === 'success').length}</p>
            </div>
            <div className="w-10 h-10 bg-green-500/20 rounded-lg flex items-center justify-center">
              <CheckCircle className="w-5 h-5 text-green-400" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Running</p>
              <p className="text-2xl font-bold text-blue-400 mt-1">{logs.filter(l => l.status === 'running').length}</p>
            </div>
            <div className="w-10 h-10 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <Loader className="w-5 h-5 text-blue-400 animate-spin" />
            </div>
          </div>
        </div>

        <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-400 text-sm">Failed</p>
              <p className="text-2xl font-bold text-red-400 mt-1">{logs.filter(l => l.status === 'failed').length}</p>
            </div>
            <div className="w-10 h-10 bg-red-500/20 rounded-lg flex items-center justify-center">
              <XCircle className="w-5 h-5 text-red-400" />
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800/50 rounded-xl border border-gray-700">
        <div className="px-6 py-4 border-b border-gray-700">
          <h3 className="text-lg font-semibold text-white">Cleanup Activity Log</h3>
        </div>
        <div className="p-6">
          <div className="space-y-3">
            {logs.map((log) => (
              <div
                key={log.id}
                className="bg-gray-900/50 rounded-lg p-4 border border-gray-700 hover:border-gray-600 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    {getStatusIcon(log.status)}
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-1">
                        <span className="text-white font-medium">{log.pcName}</span>
                        <span className="text-gray-500 text-sm">{log.timestamp}</span>
                      </div>
                      <p className={`text-sm ${getStatusColor(log.status)}`}>{log.action}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <span className="text-green-400 font-semibold">{log.spaceFreed}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <p className="text-blue-300 text-sm">
          Cleanup operations will remove temporary files, cache data, and old logs from all connected systems.
          Critical system files are protected and will not be affected.
        </p>
      </div>
    </div>
  );
}

export default CleanupView;
