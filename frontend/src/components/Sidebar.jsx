import React from 'react';
import { LayoutDashboard, Search, Database, MessageSquare, Download, Settings, Rocket, LogOut } from 'lucide-react';

const Sidebar = ({ activeTab, onTabChange, onLogout }) => {
  const menuItems = [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { id: 'search', icon: Search, label: 'Discovery' },
    { id: 'leads', icon: Database, label: 'Lead Vault' },
    { id: 'outreach', icon: MessageSquare, label: 'Outreach' },
    { id: 'export', icon: Download, label: 'Export' },
    { id: 'settings', icon: Settings, label: 'Settings' },
  ];

  return (
    <div className="w-64 h-screen fixed left-0 top-0 bg-[#020617] border-r border-white/5 flex flex-col p-6 z-50">
      <div className="flex items-center gap-2 mb-10 px-2 group cursor-pointer">
        <div className="w-8 h-8 bg-gradient-to-tr from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center shadow-lg shadow-blue-500/20 group-hover:scale-105 transition-transform">
          <Rocket className="text-white w-4 h-4" />
        </div>
        <span className="text-lg font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400 group-hover:to-blue-400 transition-colors">LeadForge AI</span>
      </div>

      <nav className="flex-1 space-y-2">
        {menuItems.map((item) => (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
              activeTab === item.id 
                ? 'bg-blue-600/10 text-blue-400 border border-blue-600/20' 
                : 'text-gray-500 hover:text-white hover:bg-white/5 border border-transparent'
            }`}
          >
            <item.icon className="w-5 h-5" />
            {item.label}
          </button>
        ))}
      </nav>

      <div className="pt-6 border-t border-white/5 space-y-4">
        <div className="px-4 py-3 bg-white/[0.02] rounded-2xl border border-white/5">
          <p className="text-[10px] text-gray-500 uppercase tracking-widest font-bold mb-1">Usage Status</p>
          <div className="flex justify-between items-center mb-1">
            <span className="text-xs text-gray-300 font-bold">142 / 200</span>
          </div>
          <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
            <div className="h-full bg-blue-600 w-[71%]" />
          </div>
        </div>
        
        <button onClick={onLogout} className="w-full flex items-center gap-3 px-4 py-3 text-sm text-gray-500 hover:text-red-400 transition-colors">
          <LogOut className="w-5 h-5" />
          Logout
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
