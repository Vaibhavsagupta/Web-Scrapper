import React from 'react';
import { Mail, Phone, Globe, Linkedin, Instagram, ExternalLink, ShieldCheck } from 'lucide-react';

const LeadTable = ({ leads, searchStatus, onDetail }) => {
  if (!leads || leads.length === 0) {
    return (
      <div className="w-full relative overflow-hidden rounded-3xl border border-white/5 bg-white/[0.02] p-8 text-center backdrop-blur-md">
        <h3 className="text-xl font-bold mb-4">No leads found for this search.</h3>
        
        {searchStatus ? (
          <div className="text-left bg-black/40 p-6 rounded-2xl max-w-2xl mx-auto border border-white/5 font-mono text-sm space-y-2 relative">
            <h4 className="text-blue-400 font-bold mb-4 flex items-center justify-between">
              Debug Summary: {searchStatus.status === 'completed' ? <span className="text-green-400 text-xs">Completed</span> : <span className="text-yellow-400 animate-pulse text-xs">Processing...</span>}
            </h4>
            <p className="text-gray-300">- Candidates discovered: <span className="text-white font-bold">{searchStatus.candidate_count || 0}</span></p>
            <p className="text-gray-300">- Leads accepted: <span className="text-white font-bold">{searchStatus.accepted_leads || 0}</span></p>
            <p className="text-gray-300">- Leads rejected: <span className="text-white font-bold">{searchStatus.rejected_leads || 0}</span></p>
            
            {searchStatus.rejection_reasons && searchStatus.rejection_reasons.length > 0 && (
              <div className="mt-4 pt-4 border-t border-white/10">
                <p className="text-red-400 font-bold mb-2">Rejection reasons:</p>
                <ul className="list-disc leading-relaxed list-inside text-xs text-gray-400 max-h-40 overflow-y-auto w-full">
                    {searchStatus.rejection_reasons.map((r, i) => (
                      <li key={i} className="mb-1 truncate">{r}</li>
                    ))}
                </ul>
              </div>
            )}
          </div>
        ) : (
          <p className="text-gray-500 text-sm">Please start a new search or clear the filter.</p>
        )}
      </div>
    );
  }

  return (
    <div className="w-full overflow-x-auto rounded-3xl border border-white/5 bg-white/[0.02] backdrop-blur-md">
      <table className="w-full text-left border-collapse">
        <thead>
          <tr className="border-b border-white/10 bg-white/5">
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Company</th>
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Contact Info</th>
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Socials</th>
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Score</th>
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Source</th>
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Authenticity</th>
            <th className="px-6 py-4 text-xs font-bold uppercase tracking-wider text-gray-400">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-white/5">
          {leads.map((lead, i) => (
            <tr key={i} className="hover:bg-white/[0.04] transition-colors group">
              <td className="px-6 py-5">
                <div className="flex flex-col">
                  <span className="font-bold text-white group-hover:text-blue-400 transition-colors">{lead.company_name}</span>
                  <span className="text-xs text-gray-500 flex items-center gap-1 mt-1">
                    <Globe className="w-3 h-3" /> {lead.website}
                  </span>
                </div>
              </td>
              <td className="px-6 py-5">
                <div className="flex flex-col gap-1">
                  {lead.email && (
                    <div className="flex items-center gap-2 text-sm text-gray-300">
                      <Mail className="w-4 h-4 text-blue-500/70" /> {lead.email}
                    </div>
                  )}
                  {lead.phone && (
                    <div className="flex items-center gap-2 text-sm text-gray-300">
                      <Phone className="w-4 h-4 text-green-500/70" /> {lead.phone}
                    </div>
                  )}
                  {!lead.email && !lead.phone && <span className="text-gray-600 text-xs italic">No direct contact found</span>}
                </div>
              </td>
              <td className="px-6 py-5">
                <div className="flex gap-2">
                  {lead.linkedin_url && (
                    <a href={lead.linkedin_url} target="_blank" className="p-2 rounded-lg bg-blue-600/10 text-blue-400 hover:bg-blue-600/20 transition-all">
                      <Linkedin className="w-4 h-4" />
                    </a>
                  )}
                  {lead.instagram_url && (
                    <a href={lead.instagram_url} target="_blank" className="p-2 rounded-lg bg-pink-600/10 text-pink-400 hover:bg-pink-600/20 transition-all">
                      <Instagram className="w-4 h-4" />
                    </a>
                  )}
                  {!lead.linkedin_url && !lead.instagram_url && <span className="text-gray-600 text-xs">-</span>}
                </div>
              </td>
              <td className="px-6 py-5">
                <div className="flex items-center gap-2">
                  <div className="w-12 h-2 bg-white/5 rounded-full overflow-hidden">
                    <div className="h-full bg-gradient-to-r from-blue-500 to-indigo-500" style={{ width: `${Math.min(100, lead.final_lead_score || lead.score || 0)}%` }} />
                  </div>
                  <span className="text-sm font-bold text-gray-300">{Math.min(100, lead.final_lead_score || lead.score || 0)}%</span>
                </div>
              </td>
              <td className="px-6 py-5">
                <div className="flex flex-col">
                  <span className="text-[10px] font-bold text-blue-400 uppercase tracking-tighter">{lead.source_platform}</span>
                  <a href={lead.source_url} target="_blank" className="text-[10px] text-gray-500 hover:text-blue-500 truncate max-w-[100px]">
                    Source Link
                  </a>
                </div>
              </td>
              <td className="px-6 py-5">
                <div className={`px-2 py-1 rounded-lg text-[9px] font-bold text-center inline-block ${
                  lead.authenticity_status === 'Verified Public Source' ? 'bg-green-600/10 text-green-400 border border-green-600/20' : 
                  lead.authenticity_status === 'Low Confidence' ? 'bg-yellow-600/10 text-yellow-400 border border-yellow-600/20' : 
                  'bg-red-600/10 text-red-400 border border-red-600/20'
                }`}>
                  {lead.authenticity_status}
                </div>
              </td>
              <td className="px-6 py-5">
                <button 
                  onClick={() => onDetail(lead)}
                  className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-xs font-bold hover:bg-white/10 transition-all"
                >
                  Details <ExternalLink className="w-3 h-3" />
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default LeadTable;
