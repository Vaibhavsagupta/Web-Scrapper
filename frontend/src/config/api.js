/**
 * API Configuration for LeadForge Frontend
 * Standardizes the Backend API URL across all environments.
 */

// Vite uses import.meta.env for environment variables
// VITE_API_BASE_URL should be set in the Vercel/Production environment
const API_URL_FROM_ENV = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL;

// If we have an explicit URL, ensure it follows the /api pattern if needed
let centralized_base = API_URL_FROM_ENV || "/api";

if (centralized_base.startsWith('http')) {
    // If it's a full URL and doesn't end with /api, append it (unless the backend doesn't use the prefix)
    // Our backend uses /api as a prefix for all routes
    if (!centralized_base.endsWith('/api') && !centralized_base.endsWith('/api/')) {
        centralized_base = centralized_base.endsWith('/') 
            ? `${centralized_base}api` 
            : `${centralized_base}/api`;
    }
}

// Production Diagnostics
if (import.meta.env.PROD) {
    console.log("🚀 LeadForge Production Mode Active");
    console.log("🔗 Connecting to Backend API at:", centralized_base);
    
    if (centralized_base.includes("localhost") || centralized_base.includes("127.0.0.1")) {
        console.warn("⚠️ WARNING: Frontend is pointing to LOCALHOST in a Production build!");
    }
} else {
    console.log("🛠️ LeadForge Development Mode Active");
    console.log("🔗 Local Proxy / API Base:", centralized_base);
}

export const API_BASE = centralized_base;
export default API_BASE;
