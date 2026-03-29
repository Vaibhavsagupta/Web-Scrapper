import React, { useState } from 'react';
import { Mail, Phone, Globe, Linkedin, Instagram, X, MessageSquare, Target, Zap, ChevronRight, Copy, CheckCircle, ShieldCheck } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const LeadDetailModal = ({ lead, onClose, onAnalyze, isAnalyzing }) => {
  const [activeTab, setActiveTab] = useState('insights');
  const [copied, setCopied] = useState(null);

  const copyToClipboard = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(null), 2000);
  };

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-6 bg-black/60 backdrop-blur-sm">
      <motion.div 
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        exit={{ scale: 0.9, opacity: 0 }}
        className="w-full max-w-4xl max-h-[90vh] bg-[#0f172a] border border-white/10 rounded-[2.5rem] shadow-2xl overflow-hidden flex flex-col"
      >
        {/* Header */}
        <div className="px-8 py-6 border-b border-white/5 flex justify-between items-center bg-white/[0.02]">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-2xl bg-blue-600/20 flex items-center justify-center border border-blue-600/30">
              <Zap className="text-blue-400 w-6 h-6" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">{lead.company_name}</h2>
              <p className="text-sm text-gray-500">{lead.website}</p>
            </div>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-full transition-all"><X className="w-6 h-6" /></button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-8">
          <div className="flex gap-4 mb-8">
            {['insights', 'outreach', 'context'].map(tab => (
              <button 
                key={tab} 
                onClick={() => setActiveTab(tab)}
                className={`px-6 py-2.5 rounded-full text-sm font-bold capitalize transition-all ${activeTab === tab ? 'bg-blue-600 text-white' : 'bg-white/5 text-gray-400 hover:bg-white/10'}`}
              >
                {tab}
              </button>
            ))}
          </div>

          <AnimatePresence mode="wait">
            {activeTab === 'insights' && (
              <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-widest text-blue-400 mb-2">AI Summary</h3>
                      <p className="text-gray-300 leading-relaxed italic border-l-2 border-blue-600/30 pl-4">
                        {lead.ai_summary || "AI analysis not yet performed. Click start to enrich."}
                      </p>
                    </div>
                    <div>
                      <h3 className="text-xs font-bold uppercase tracking-widest text-indigo-400 mb-2 flex items-center gap-2">
                        <Target className="w-3 h-3" /> Likely Pain Points
                      </h3>
                      <div className="flex flex-wrap gap-2">
                        {(lead.pain_points || []).map((p, i) => (
                          <span key={i} className="px-3 py-1 bg-white/5 rounded-lg text-xs text-gray-400 border border-white/5">{p}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                  <div className="space-y-6 bg-white/[0.02] p-6 rounded-3xl border border-white/5">
                    <div className="flex justify-between items-center">
                      <span className="text-sm text-gray-400 font-medium">Lead Quality Score</span>
                      <span className="text-xl font-bold text-blue-400">{Math.min(100, lead.final_lead_score || lead.score || 0)}%</span>
                    </div>
                    <div className="w-full h-2 bg-white/5 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500" style={{ width: `${Math.min(100, lead.final_lead_score || lead.score || 0)}%` }} />
                    </div>
                    <div className="pt-4 border-t border-white/5">
                      <h3 className="text-xs font-bold uppercase tracking-widest text-gray-500 mb-3">Qualification</h3>
                      <div className="flex items-center gap-2">
                        <CheckCircle className={`w-4 h-4 ${lead.priority_level === 'High Priority' ? 'text-green-500' : 'text-gray-500'}`} />
                        <span className="font-bold">{lead.priority_level || 'Pending Analysis'}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}

            {activeTab === 'outreach' && (
              <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} className="space-y-6">
                <div className="p-6 bg-blue-600/5 border border-blue-600/20 rounded-3xl relative">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="font-bold flex items-center gap-2"><Mail className="w-4 h-4" /> Personalized Cold Email</h3>
                    <button 
                      onClick={() => copyToClipboard(lead.outreach_email, 'email')}
                      className="text-xs text-blue-400 font-bold flex items-center gap-1 hover:text-white"
                    >
                      {copied === 'email' ? <CheckCircle className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3" />}
                      {copied === 'email' ? 'Copied' : 'Copy Draft'}
                    </button>
                  </div>
                  <pre className="text-gray-400 text-sm whitespace-pre-wrap font-sans leading-relaxed">
                    {lead.outreach_email || "Click 'Perform AI Analysis' to generate custom outreach pitches."}
                  </pre>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-white/[0.03] border border-white/5 rounded-2xl">
                    <h4 className="flex items-center gap-2 text-sm font-bold mb-2"><MessageSquare className="w-4 h-4 text-green-500" /> WhatsApp</h4>
                    <p className="text-gray-400 text-xs italic">{lead.outreach_whatsapp || "Pending..."}</p>
                  </div>
                  <div className="p-4 bg-white/[0.03] border border-white/5 rounded-2xl">
                    <h4 className="flex items-center gap-2 text-sm font-bold mb-2"><Linkedin className="w-4 h-4 text-blue-500" /> LinkedIn</h4>
                    <p className="text-gray-400 text-xs italic">{lead.outreach_linkedin || "Pending..."}</p>
                  </div>
                </div>
              </motion.div>
            )}
            
            {activeTab === 'context' && (
              <motion.div initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }}>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                  <div className="space-y-6">
                    <h3 className="text-xl font-bold flex items-center gap-2 mb-4">
                      <ShieldCheck className="w-5 h-5 text-green-400" /> Lead Origin & Provenance
                    </h3>
                    
                    <div className="space-y-4">
                      <div className="p-4 bg-white/[0.03] border border-white/5 rounded-2xl">
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Source Platform</p>
                        <p className="text-sm font-bold text-blue-400">{lead.source_platform}</p>
                      </div>
                      
                      <div className="p-4 bg-white/[0.03] border border-white/5 rounded-2xl">
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Discovery Source</p>
                        <p className="text-sm font-bold text-gray-200">{lead.discovery_source}</p>
                        <a href={lead.discovery_url} target="_blank" className="text-[10px] text-blue-500 truncate block mt-1 hover:underline">
                          {lead.discovery_url}
                        </a>
                      </div>

                      <div className="p-4 bg-white/[0.03] border border-white/5 rounded-2xl">
                        <p className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Authenticity Status</p>
                        <div className="flex items-center gap-2 mt-1">
                          <span className={`px-2 py-1 rounded-lg text-[10px] font-bold ${
                            lead.authenticity_status === 'Verified Public Source' ? 'bg-green-600/10 text-green-400 border border-green-600/20' : 
                            'bg-yellow-600/10 text-yellow-400 border border-yellow-600/20'
                          }`}>
                            {lead.authenticity_status}
                          </span>
                        </div>
                        <p className="text-[11px] text-gray-500 mt-2 italic">“{lead.authenticity_reason}”</p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-6">
                    <h3 className="text-sm font-bold uppercase tracking-widest text-gray-500 mb-4">Crawl History</h3>
                    <div className="p-6 bg-white/[0.02] border border-white/5 rounded-3xl">
                       <p className="text-[10px] text-gray-500 uppercase font-bold mb-3">Scraped Pages ({lead.scraped_pages?.length || 0})</p>
                       <ul className="space-y-2">
                          {(lead.scraped_pages || []).map((page, i) => (
                            <li key={i} className="text-[10px] text-gray-400 flex items-center gap-2 truncate">
                              <ChevronRight className="w-3 h-3 text-blue-500" /> {page}
                            </li>
                          ))}
                       </ul>
                       <div className="mt-6 pt-4 border-t border-white/5">
                          <p className="text-[10px] text-gray-500 uppercase font-bold mb-1">Scraped At</p>
                          <p className="text-xs text-gray-400">{lead.scraped_at ? new Date(lead.scraped_at).toLocaleString() : 'N/A'}</p>
                       </div>
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Footer */}
        <div className="px-8 py-6 bg-black/40 border-t border-white/5 flex justify-between items-center">
          <p className="text-xs text-gray-500 max-w-sm">Lead ID: #{lead.id} | Scraped: {new Date(lead.created_at).toLocaleDateString()}</p>
          <div className="flex gap-4">
            <button onClick={onAnalyze} disabled={isAnalyzing} className={`px-6 py-2.5 rounded-xl text-sm font-bold flex items-center gap-2 transition-all ${isAnalyzing ? 'bg-blue-600/50 cursor-not-allowed text-gray-300' : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 text-white'}`}>
              <Zap className={`w-4 h-4 fill-current ${isAnalyzing ? 'animate-pulse' : ''}`} /> 
              {isAnalyzing ? 'Analyzing with Gemini...' : 'Perform AI Analysis'}
            </button>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

export default LeadDetailModal;
