import { Server } from 'lucide-react';

function Header() {
  const currentTime = new Date().toLocaleString('en-US', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <header className="bg-gray-950 border-b border-gray-800 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <Server className="w-6 h-6 text-blue-500" />
          <h1 className="text-2xl font-bold text-white">Remote Cleanup Bot Dashboard</h1>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-400">
            {currentTime}
          </div>
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold">
            A
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
