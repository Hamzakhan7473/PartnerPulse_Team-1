import { Home, Search, UserPlus, Database, X, LogOut, Zap } from 'lucide-react';
import { supplierApi } from '../services/api';

const MODEL_CHOICES = [
  'gpt-4.1-mini',
  'anthropic.claude-3-sonnet-20240229-v1:0',
  'anthropic.claude-3-5-haiku-20241022-v1:0',
  'us.deepseek.r1-v1:0',
  'meta.llama3-8b-instruct-v1:0',
  'meta.llama3-70b-instruct-v1:0',
  'mistral.mixtral-8x7b-instruct-v0:1',
  'mistral.mistral-7b-instruct-v0:2',
];

function Sidebar({ 
  activeTab, 
  setActiveTab, 
  modelId, 
  setModelId, 
  queryHistory, 
  setQueryHistory,
  user,
  onLogout,
  canAccessAddData,
  canAccessQuery,
  canAccessCRM,
  canAccessAllSuppliers
}) {
  const allTabs = [
    { id: 'add-data', label: 'Add Supplier Data', icon: Home, canAccess: canAccessAddData },
    { id: 'query', label: 'Query Supplier', icon: Search, canAccess: canAccessQuery },
    { id: 'crm', label: 'Add Supplier Profile', icon: UserPlus, canAccess: canAccessCRM },
    { id: 'all-suppliers', label: 'All Suppliers', icon: Database, canAccess: canAccessAllSuppliers },
  ];

  // Filter tabs based on access
  const tabs = allTabs.filter(tab => tab.canAccess);

  return (
    <aside className="w-72 bg-slate-900 border-r border-slate-800 flex flex-col shadow-xl relative z-10">
      <div className="p-6 border-b border-slate-800 bg-slate-950">
        <div className="flex items-center gap-3">
          <div className="flex items-center justify-center w-10 h-10 bg-slate-800 rounded-lg">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <h2 className="text-xl font-bold text-white">PartnerPulse</h2>
        </div>
        <p className="text-xs text-slate-400 mt-2">
          AI-Powered Assistant for Amazon Marketplace Supplier Management
        </p>
        {user && (
          <div className="mt-3 pt-3 border-t border-slate-800">
            <p className="text-xs text-slate-500 uppercase tracking-wide mb-1">Logged in as</p>
            <p className="text-sm font-semibold text-white">{user.username}</p>
            <p className="text-xs text-slate-400">{user.roleName}</p>
          </div>
        )}
      </div>

      <nav className="flex-1 p-4">
        <ul className="space-y-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <li key={tab.id}>
                  <button
                    onClick={() => setActiveTab(tab.id)}
                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-slate-800 text-white font-semibold shadow-md border-l-4 border-blue-500'
                        : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                    }`}
                  >
                    <Icon className={`w-5 h-5 ${isActive ? 'text-blue-400' : 'text-slate-400'}`} />
                    <span>{tab.label}</span>
                  </button>
              </li>
            );
          })}
        </ul>
      </nav>

            <div className="p-4 border-t border-slate-800 space-y-4 bg-slate-950">
              {queryHistory.length > 0 && (
                <button
                  onClick={() => setQueryHistory([])}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-800 text-slate-300 rounded-lg hover:bg-slate-700 transition-colors font-medium text-sm border border-slate-700"
                >
                  <X className="w-4 h-4" />
                  <span>Clear History</span>
                </button>
              )}

              <button
                onClick={onLogout}
                className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-red-600/20 hover:bg-red-600/30 text-red-400 rounded-lg transition-colors font-medium text-sm border border-red-600/30 mt-4"
              >
                <LogOut className="w-4 h-4" />
                <span>Logout</span>
              </button>
            </div>
    </aside>
  );
}

export default Sidebar;

