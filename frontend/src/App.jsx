import React, { useState, useEffect } from 'react';
import { Search, Database, MessageSquare, Download, Settings, LayoutDashboard, Rocket, Zap, Clock, Globe, Loader2, ChevronRight, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import Sidebar from './components/Sidebar';
import DashboardHome from './pages/DashboardHome';
import LeadTable from './components/LeadTable';
import LeadDetailModal from './components/LeadDetailModal';

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

const App = () => {
  const [user, setUser] = useState(localStorage.getItem('leadforge_user') || null);
  const [loginUsername, setLoginUsername] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginError, setLoginError] = useState('');

  const [activeTab, setActiveTab] = useState('dashboard');
  const [keyword, setKeyword] = useState('');
  const [location, setLocation] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchId, setSearchId] = useState(null);
  const [searchStatus, setSearchStatus] = useState(null);
  const [leads, setLeads] = useState([]);
  const [allLeads, setAllLeads] = useState([]);
  const [selectedLead, setSelectedLead] = useState(null);
  const [analyzingLeads, setAnalyzingLeads] = useState({});
  const [platform, setPlatform] = useState('all');

  // Fetch leads for vault
  const fetchLeads = async () => {
    try {
      if (!user) return;
      let url = `${API_BASE}/export/json?owner_id=${user}`;
      if (searchId) url += `&search_id=${searchId}`;
      const res = await axios.get(url);
      
      setLeads(res.data);
      if (!searchId) setAllLeads(res.data);
      
      if (searchId) {
        const dbgRes = await axios.get(`${API_BASE}/search/debug/${searchId}`);
        setSearchStatus(dbgRes.data);
        if (dbgRes.data.status === 'completed') {
            setIsSearching(false);
        }
      } else {
        setIsSearching(false);
      }
    } catch (err) {
      console.error("Failed to fetch leads", err);
    }
  };

  useEffect(() => {
    if (activeTab === 'leads') {
        fetchLeads();
        let interval;
        if (isSearching) {
            interval = setInterval(fetchLeads, 3000);
        }
        return () => clearInterval(interval);
    }
  }, [activeTab, isSearching, searchId]);

  const startSearch = async (e) => {
    e.preventDefault();
    if (!keyword) return;
    
    setIsSearching(true);
    setSearchStatus(null);
    try {
      const res = await axios.post(`${API_BASE}/search/`, {
        keyword,
        location,
        lead_count: 10,
        owner_id: user,
        platform: platform
      });
      setSearchId(res.data.id);
      setActiveTab('leads');
    } catch (err) {
      console.error("Search failed", err);
    }
  };

  const analyzeLead = async (leadId) => {
    if (analyzingLeads[leadId]) return; // prevent duplicate clicks
    
    try {
      setAnalyzingLeads(prev => ({...prev, [leadId]: true}));
      await axios.post(`${API_BASE}/ai/analyze-lead/${leadId}`);
      
      // Poll for updates every 3 seconds
      const pollInterval = setInterval(async () => {
          try {
              const res = await axios.get(`${API_BASE}/ai/lead-insights/${leadId}`);
              const data = res.data;
              
              // Only update UI once AI has truly populated the records
              if (data.ai_summary && data.ai_summary !== "") {
                  clearInterval(pollInterval);
                  setAnalyzingLeads(prev => ({...prev, [leadId]: false}));
                  
                  const mappedUpdates = {
                      ai_summary: data.ai_summary,
                      pain_points: data.pain_points,
                      final_lead_score: data.score,
                      priority_level: data.qualification,
                      outreach_email: data.outreach?.email || '',
                      outreach_whatsapp: data.outreach?.whatsapp || '',
                      outreach_linkedin: data.outreach?.linkedin || ''
                  };
                  
                  setSelectedLead(prev => prev?.id === leadId ? { ...prev, ...mappedUpdates } : prev);
                  setLeads(prev => prev.map(l => l.id === leadId ? { ...l, ...mappedUpdates } : l));
                  setAllLeads(prev => prev.map(l => l.id === leadId ? { ...l, ...mappedUpdates } : l));
              }
          } catch(e) {
              console.error("Polling error", e);
          }
      }, 3000);
      
      // Timeout after 60 seconds to stop polling if it completely failed
      setTimeout(() => {
          clearInterval(pollInterval);
          setAnalyzingLeads(prev => ({...prev, [leadId]: false}));
      }, 60000);
      
    } catch (err) {
      console.error("Analysis failed", err);
      setAnalyzingLeads(prev => ({...prev, [leadId]: false}));
    }
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (loginUsername === 'vaibhav123' && loginPassword === 'vaib2005') {
      localStorage.setItem('leadforge_user', loginUsername);
      setUser(loginUsername);
      setLoginError('');
    } else {
      setLoginError('Invalid credentials');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('leadforge_user');
    setUser(null);
    setSearchId(null);
    setLeads([]);
  };

  const handleExportCSV = () => {
    if (!user) return;
    let url = `http://localhost:8880${API_BASE}/export/csv?owner_id=${user}`;
    if (searchId) url += `&search_id=${searchId}`;
    window.open(url, '_blank');
  };

  if (!user) {
    return (
      <div className="min-h-screen bg-[#020617] text-white flex items-center justify-center font-sans tracking-wide">
        <div className="w-full max-w-sm p-8 bg-white/[0.02] border border-white/5 rounded-[2rem] shadow-2xl backdrop-blur-md">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-blue-600/20 rounded-2xl flex items-center justify-center mx-auto mb-4 border border-blue-600/30">
              <Zap className="text-blue-400 w-8 h-8" />
            </div>
            <h2 className="text-2xl font-bold">Welcome Back</h2>
            <p className="text-gray-500 text-sm mt-2">Login to your workspace</p>
          </div>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1 block">Username</label>
              <input value={loginUsername} onChange={e=>setLoginUsername(e.target.value)} type="text" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-blue-500 transition-all text-sm font-medium" />
            </div>
            <div>
              <label className="text-xs font-bold uppercase tracking-widest text-gray-400 mb-1 block">Password</label>
              <input value={loginPassword} onChange={e=>setLoginPassword(e.target.value)} type="password" className="w-full bg-black/40 border border-white/10 rounded-xl px-4 py-3 outline-none focus:border-blue-500 transition-all text-sm font-medium" />
            </div>
            {loginError && <p className="text-red-400 text-xs text-center font-bold">{loginError}</p>}
            <button type="submit" className="w-full mt-4 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl py-3 font-bold text-sm shadow-lg shadow-blue-500/20 active:scale-95 transition-all">
              Sign In
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-[#020617] text-white font-sans tracking-wide overflow-hidden">
      <Sidebar activeTab={activeTab} onTabChange={setActiveTab} onLogout={handleLogout} />
      
      <main className="ml-64 p-12 w-full h-screen overflow-y-auto">
        {/* Background Gradients */}
        <div className="fixed top-0 left-64 w-full h-full pointer-events-none -z-10 overflow-hidden">
          <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-blue-600/5 blur-[120px] rounded-full" />
          <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-600/5 blur-[120px] rounded-full" />
        </div>

        <AnimatePresence mode="wait">
          {activeTab === 'dashboard' && (
            <DashboardHome key="dash" onNavigate={setActiveTab} />
          )}

          {activeTab === 'search' && (
            <motion.div key="search" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
              <div className="text-center max-w-2xl mx-auto py-12">
                <h1 className="text-4xl font-bold mb-4">Lead Discovery Engine</h1>
                <p className="text-gray-500">Configure your discovery parameters and let LeadForge find high-intent prospects for your business.</p>
              </div>

              <div className="max-w-3xl mx-auto p-8 bg-white/[0.02] border border-white/5 rounded-[2.5rem] shadow-2xl">
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                        <label className="text-xs font-bold uppercase tracking-widest text-gray-500">Niche / Keyword</label>
                        <div className="relative flex items-center p-4 bg-black/40 border border-white/10 rounded-2xl">
                            <Search className="w-5 h-5 text-gray-500 mr-3" />
                            <input value={keyword} onChange={(e) => setKeyword(e.target.value)} placeholder="e.g. Real Estate Agencies" className="bg-transparent border-none outline-none w-full text-white font-medium" />
                        </div>
                    </div>
                    <div className="space-y-2">
                        <label className="text-xs font-bold uppercase tracking-widest text-gray-500">Target Location</label>
                        <div className="relative flex items-center p-4 bg-black/40 border border-white/10 rounded-2xl">
                            <Globe className="w-5 h-5 text-gray-500 mr-3" />
                            <input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. Bhopal, IN" className="bg-transparent border-none outline-none w-full text-white font-medium" />
                        </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <label className="text-xs font-bold uppercase tracking-widest text-gray-500">Target Platforms</label>
                    <div className="grid grid-cols-3 gap-4">
                        {[
                          { id: 'all', label: 'General Web', icon: Globe },
                          { id: 'reddit', label: 'Reddit', icon: MessageSquare },
                          { id: 'linkedin', label: 'LinkedIn', icon: CheckCircle2 }
                        ].map(p => (
                            <button 
                                key={p.id}
                                onClick={() => setPlatform(p.id)}
                                className={`flex flex-col items-center justify-center p-4 rounded-2xl border transition-all ${platform === p.id ? 'bg-blue-600/20 border-blue-500 text-blue-400 shadow-lg shadow-blue-500/10' : 'bg-black/40 border-white/10 text-gray-500 hover:border-white/20'}`}
                            >
                                <p.icon className="w-6 h-6 mb-2" />
                                <span className="text-[10px] font-bold uppercase tracking-wider">{p.label}</span>
                            </button>
                        ))}
                    </div>
                  </div>

                  <button onClick={startSearch} className="w-full py-5 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-2xl text-lg font-bold hover:shadow-xl hover:shadow-blue-600/20 active:scale-95 transition-all">
                    Initialize Discovery
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'search-progress' && (
              <motion.div key="prog" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex flex-col items-center justify-center py-20 text-center">
                  <Loader2 className="w-16 h-16 text-blue-500 animate-spin mb-8" />
                  <h2 className="text-3xl font-bold mb-2">Scraping in Progress...</h2>
                  <p className="text-gray-500 max-w-md">Our engine is currently identifying businesses and extracting intelligence. This usually takes 1-2 minutes.</p>
                  <button onClick={() => setActiveTab('leads')} className="mt-8 px-6 py-3 border border-white/10 rounded-xl text-sm font-bold text-gray-400 hover:bg-white/5">View Leads So Far</button>
              </motion.div>
          )}

          {activeTab === 'leads' && (
            <motion.div key="leads" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
              <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold flex items-center gap-3"><Database className="text-blue-400 w-8 h-8" /> Lead Vault</h1>
                <div className="flex gap-4">
                  {searchId && (
                    <button onClick={() => { setSearchId(null); setSearchStatus(null); }} className="px-4 py-2 bg-white/5 border border-white/10 text-white font-bold rounded-xl hover:bg-white/10 transition-all text-xs">
                      Clear Filter
                    </button>
                  )}
                  <button onClick={handleExportCSV} className="flex items-center gap-2 px-6 py-2 bg-white text-black font-bold rounded-xl hover:bg-gray-100 transition-all shadow-md">
                    <Download className="w-4 h-4" /> Export CSV
                  </button>
                </div>
              </div>
              <LeadTable leads={searchId ? leads : (allLeads.length > 0 ? allLeads : leads)} isSearching={isSearching} searchStatus={searchStatus} onDetail={(lead) => setSelectedLead(lead)} />
            </motion.div>
          )}

          {activeTab === 'outreach' && (
            <motion.div key="outreach" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8 flex flex-col items-center justify-center h-[80vh]">
              <div className="w-24 h-24 bg-blue-600/10 rounded-[2rem] flex items-center justify-center border border-blue-600/20 mb-6">
                <MessageSquare className="w-12 h-12 text-blue-500" />
              </div>
              <h1 className="text-4xl font-bold text-center">Global Outreach Center</h1>
              <p className="text-gray-400 text-center max-w-lg mb-8">
                Mass Email and Automated Campaign management is currently under development. To view AI-generated outreach pitches, go to the <b className="text-white cursor-pointer hover:underline" onClick={() => setActiveTab('leads')}>Lead Vault</b>, click 'Details' on a specific lead, and navigate to the Outreach tab.
              </p>
              <button onClick={() => setActiveTab('leads')} className="px-8 py-3 bg-white text-black font-bold rounded-xl hover:bg-gray-100 transition-all shadow-xl hover:scale-105 active:scale-95 text-sm">
                Go to Lead Vault
              </button>
            </motion.div>
          )}

          {activeTab === 'export' && (
            <motion.div key="export" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
              <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold flex items-center gap-3"><Download className="text-blue-400 w-8 h-8" /> Data Export Center</h1>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="p-8 bg-white/[0.02] border border-white/5 rounded-[2.5rem] flex flex-col items-center text-center">
                  <div className="w-16 h-16 bg-blue-600/10 rounded-2xl flex items-center justify-center mb-6">
                    <Database className="w-8 h-8 text-blue-400" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">CSV Spreadsheet</h3>
                  <p className="text-gray-500 text-sm mb-8">Download all your discovered leads in a clean CSV format compatible with Excel and Google Sheets.</p>
                  <button onClick={handleExportCSV} className="w-full py-4 bg-white text-black font-bold rounded-2xl hover:bg-gray-100 transition-all">
                    Download All Leads (.csv)
                  </button>
                </div>
                <div className="p-8 bg-white/[0.02] border border-white/5 rounded-[2.5rem] flex flex-col items-center text-center">
                  <div className="w-16 h-16 bg-indigo-600/10 rounded-2xl flex items-center justify-center mb-6">
                    <Rocket className="w-8 h-8 text-indigo-400" />
                  </div>
                  <h3 className="text-xl font-bold mb-2">JSON Export</h3>
                  <p className="text-gray-500 text-sm mb-8">Export lead data for developer use or importing into other automation tools.</p>
                  <button onClick={() => window.open(`http://localhost:8880${API_BASE}/export/json?owner_id=${user}`, '_blank')} className="w-full py-4 bg-white/5 border border-white/10 text-white font-bold rounded-2xl hover:bg-white/10 transition-all">
                    Download Raw Data (.json)
                  </button>
                </div>
              </div>
            </motion.div>
          )}

          {activeTab === 'settings' && (
            <motion.div key="settings" initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
              <h1 className="text-3xl font-bold flex items-center gap-3"><Settings className="text-gray-400 w-8 h-8" /> Workspace Settings</h1>
              <div className="max-w-2xl bg-white/[0.02] border border-white/5 rounded-[2.5rem] p-8 space-y-8">
                <div>
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">Account Profile</h3>
                  <div className="flex items-center gap-4 p-4 bg-white/[0.02] rounded-2xl border border-white/5">
                    <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center font-bold text-xl uppercase">
                      {user.charAt(0)}
                    </div>
                    <div>
                      <p className="font-bold">{user}</p>
                      <p className="text-xs text-gray-500 italic">LeadForge Pro Member</p>
                    </div>
                  </div>
                </div>
                <div>
                  <h3 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-4">System Status</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center text-sm p-4 bg-black/40 rounded-xl border border-white/5">
                      <span className="text-gray-400">Backend API</span>
                      <span className="flex items-center gap-2 text-green-400 font-bold"><div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" /> Operational</span>
                    </div>
                    <div className="flex justify-between items-center text-sm p-4 bg-black/40 rounded-xl border border-white/5">
                      <span className="text-gray-400">Scraping Engine</span>
                      <span className="flex items-center gap-2 text-green-400 font-bold"><div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" /> Ready</span>
                    </div>
                    <div className="flex justify-between items-center text-sm p-4 bg-black/40 rounded-xl border border-white/5">
                      <span className="text-gray-400">AI Processing</span>
                      <span className="flex items-center gap-2 text-green-400 font-bold"><div className="w-2 h-2 bg-green-400 rounded-full animate-pulse" /> Online</span>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Selected Lead Modal */}
        <AnimatePresence>
          {selectedLead && (
            <LeadDetailModal 
                lead={selectedLead} 
                onClose={() => setSelectedLead(null)} 
                onAnalyze={() => analyzeLead(selectedLead.id)} 
                isAnalyzing={analyzingLeads[selectedLead.id]}
            />
          )}
        </AnimatePresence>
      </main>
    </div>
  );
};

export default App;
