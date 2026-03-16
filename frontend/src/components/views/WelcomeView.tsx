import { Terminal, Shield, Zap } from 'lucide-react';

function WelcomeView() {
  return (
    <div className="h-full flex items-center justify-center">
      <div className="text-center max-w-2xl">
        <div className="w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg shadow-blue-500/20">
          <Terminal className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-3xl font-bold text-white mb-4">Remote Cleanup Bot</h2>
        <p className="text-gray-400 text-lg mb-8">
          System Administration & Network Management Tool
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-12">
          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <div className="w-12 h-12 bg-blue-500/20 rounded-lg flex items-center justify-center mb-4">
              <Shield className="w-6 h-6 text-blue-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">Secure Management</h3>
            <p className="text-gray-400 text-sm">
              Remotely manage multiple Linux PCs in your lab environment
            </p>
          </div>

          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <div className="w-12 h-12 bg-green-500/20 rounded-lg flex items-center justify-center mb-4">
              <Zap className="w-6 h-6 text-green-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">Quick Actions</h3>
            <p className="text-gray-400 text-sm">
              Monitor disk usage, cleanup junk files, and check system status
            </p>
          </div>

          <div className="bg-gray-800/50 rounded-xl p-6 border border-gray-700">
            <div className="w-12 h-12 bg-purple-500/20 rounded-lg flex items-center justify-center mb-4">
              <Terminal className="w-6 h-6 text-purple-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">Real-time Logs</h3>
            <p className="text-gray-400 text-sm">
              View detailed logs and activity from all connected systems
            </p>
          </div>
        </div>

        <div className="mt-12 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
          <p className="text-blue-300 text-sm">
            Click "Start Bot" in the sidebar to begin monitoring your systems
          </p>
        </div>
      </div>
    </div>
  );
}

export default WelcomeView;
