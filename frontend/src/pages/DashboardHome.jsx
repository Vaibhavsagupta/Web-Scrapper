import React, { useState, useEffect } from 'react';
import { Database, Search, MessageSquare, Zap, TrendingUp, BarChart, Rocket, ChevronRight, CheckCircle, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

const DashboardHome = ({ onNavigate, apiBase }) => {
  const [stats, setStats] = useState({
    total_leads: 0,
    high_priority: 0,
    total_searches: 0,
    outreach_generated: 0,
    industry_distribution: []
  });

  const [recent, setRecent] = useState({
    recent_leads: [],
    recent_searches: []
  });

  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const statsRes = await axios.get(`${apiBase}/analytics/stats`);
        setStats(statsRes.data);
        const recentRes = await axios.get(`${apiBase}/analytics/recent-activity`);
        setRecent(recentRes.data);
      } catch (err) {
        console.error("Dashboard data fetch failed", err);
      } finally {
        setLoading(false);
      }
    };
    if (apiBase) fetchData();
  }, [apiBase]);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Welcome Header */}
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Welcome to <span className="text-blue-400">LeadForge AI</span></h1>
          <p className="text-gray-500 text-sm mt-1">Growth strategies, powered by automated intelligence.</p>
        </div>
        <button 
          onClick={() => onNavigate('search')}
          className="px-6 py-3 bg-blue-600 rounded-2xl text-sm font-bold flex items-center gap-2 hover:bg-blue-500 transition-all shadow-xl shadow-blue-600/20 active:scale-95 transition-transform"
        >
          <Search className="w-4 h-4" /> Start Scraper
        </button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {[
          { icon: Database, bg: 'bg-blue-600/10', color: 'text-blue-400', label: 'Total Leads', val: stats.total_leads, trend: '+12% this week' },
          { icon: Zap, bg: 'bg-yellow-600/10', color: 'text-yellow-400', label: 'High Priority', val: stats.high_priority, trend: 'Top opportunities' },
          { icon: Search, bg: 'bg-indigo-600/10', color: 'text-indigo-400', label: 'Search Results', val: stats.total_searches, trend: 'Completed Scraping' },
          { icon: MessageSquare, bg: 'bg-green-600/10', color: 'text-green-400', label: 'Outreach Crafted', val: stats.outreach_generated, trend: 'AI Drafts' },
        ].map((item, i) => (
          <div key={i} className="p-6 bg-white/[0.03] border border-white/5 rounded-3xl hover:bg-white/[0.05] transition-all">
            <div className={`w-12 h-12 rounded-2xl ${item.bg} flex items-center justify-center mb-4`}>
              <item.icon className={`${item.color} w-6 h-6`} />
            </div>
            <p className="text-xs text-gray-500 uppercase font-bold tracking-widest">{item.label}</p>
            <h3 className="text-3xl font-bold mt-1 text-white">{item.val}</h3>
            <p className="text-[10px] text-gray-400 mt-2 flex items-center gap-1">
              <TrendingUp className="w-3 h-3 text-blue-500" /> {item.trend}
            </p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {/* Industry Chart */}
        <div className="md:col-span-2 p-8 bg-white/[0.02] border border-white/5 rounded-[2.5rem]">
          <div className="flex justify-between items-center mb-8">
            <h3 className="text-xl font-bold flex items-center gap-2"><BarChart className="w-5 h-5 text-blue-400" /> Industry Analysis</h3>
            <span className="text-xs text-gray-500">Global lead categorization</span>
          </div>
          <div className="space-y-6">
            {stats.industry_distribution.length > 0 ? stats.industry_distribution.map((ind, i) => (
                <div key={i}>
                <div className="flex justify-between text-sm mb-2">
                    <span className="text-gray-400">{ind.name}</span>
                    <span className="font-bold">{ind.value}</span>
                </div>
                <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-blue-600" style={{ width: `${(ind.value / (stats.total_leads || 1)) * 100}%` }} />
                </div>
                </div>
            )) : <p className="text-gray-500 text-center py-10">Start discovery to see analytics insights.</p>}
          </div>
        </div>

        {/* Recent Searches */}
        <div className="p-8 bg-white/[0.02] border border-white/5 rounded-[2.5rem]">
          <h3 className="text-xl font-bold mb-6 flex items-center gap-2"><Clock className="w-5 h-5 text-indigo-400" /> Recent Actions</h3>
          <div className="space-y-4">
            {recent.recent_searches.map((res, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-white/[0.02] rounded-2xl border border-white/5 hover:bg-white/[0.05] transition-all cursor-pointer">
                <div>
                  <p className="text-sm font-bold truncate max-w-[120px]">{res.keyword}</p>
                  <p className="text-[10px] text-gray-500">{res.location}</p>
                </div>
                <div className={`text-[10px] px-2 py-1 rounded-full ${res.status === 'completed' ? 'bg-green-600/10 text-green-400' : 'bg-blue-600/10 text-blue-400 animate-pulse'}`}>
                  {res.status}
                </div>
              </div>
            ))}
            {recent.recent_searches.length === 0 && <p className="text-gray-600 text-xs py-10 text-center">No history yet.</p>}
          </div>
          <button 
            onClick={() => onNavigate('leads')}
            className="w-full mt-6 py-3 border border-white/5 rounded-xl text-xs font-bold text-gray-400 hover:text-white hover:bg-white/5 transition-all flex items-center justify-center gap-2"
          >
            Manage All Vault <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardHome;
