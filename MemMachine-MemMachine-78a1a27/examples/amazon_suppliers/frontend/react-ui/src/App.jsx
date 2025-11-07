import { useState, useEffect } from 'react';
import Login from './components/Login';
import Sidebar from './components/Sidebar';
import AddSupplierData from './components/AddSupplierData';
import QuerySupplier from './components/QuerySupplier';
import AddSupplierProfile from './components/AddSupplierProfile';
import AllSuppliers from './components/AllSuppliers';
import { LogOut, Zap } from 'lucide-react';

function App() {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('add-data');
  const [modelId, setModelId] = useState('gpt-4.1-mini');
  const [queryHistory, setQueryHistory] = useState([]);

  // Check for existing session on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      try {
        setUser(JSON.parse(savedUser));
      } catch (e) {
        localStorage.removeItem('user');
      }
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    // Set default tab based on role
    if (userData.role === 'head-sales') {
      setActiveTab('query');
    } else {
      setActiveTab('add-data');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('user');
    setUser(null);
    setActiveTab('add-data');
    setQueryHistory([]);
  };

  // Show login page if not authenticated
  if (!user) {
    return <Login onLogin={handleLogin} />;
  }

  // Determine which tabs are accessible based on role
  const canAccessAddData = user.role === 'sales' || user.role === 'operations' || user.role === 'head-sales';
  const canAccessQuery = user.role === 'head-sales';
  const canAccessCRM = user.role === 'sales' || user.role === 'operations';
  const canAccessAllSuppliers = true; // All roles can access

  return (
    <div className="flex h-screen bg-slate-50 animated-bg relative">
      {/* Animated particles */}
      <div className="particle particle-1"></div>
      <div className="particle particle-purple particle-2"></div>
      <div className="particle particle-green particle-3"></div>
      <div className="particle particle-4"></div>
      <div className="particle particle-purple particle-5"></div>
      <div className="particle particle-green particle-6"></div>
      <div className="particle particle-7"></div>
      <div className="particle particle-purple particle-8"></div>
      <div className="particle particle-9"></div>
      <div className="particle particle-purple particle-10"></div>
      <div className="particle particle-green particle-11"></div>
      <div className="particle particle-12"></div>
      <div className="particle particle-purple particle-13"></div>
      <div className="particle particle-green particle-14"></div>
      <div className="particle particle-15"></div>
      <div className="particle particle-purple particle-16"></div>
      
      <Sidebar 
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        modelId={modelId}
        setModelId={setModelId}
        queryHistory={queryHistory}
        setQueryHistory={setQueryHistory}
        user={user}
        onLogout={handleLogout}
        canAccessAddData={canAccessAddData}
        canAccessQuery={canAccessQuery}
        canAccessCRM={canAccessCRM}
        canAccessAllSuppliers={canAccessAllSuppliers}
      />
      <main className="flex-1 overflow-y-auto bg-slate-50 relative z-10">
        <div className="max-w-7xl mx-auto p-8">
          <div className="mb-8 pb-6 border-b border-slate-200 flex items-start justify-between">
            <div>
              <div className="flex items-center gap-4 mb-2">
                <div className="flex items-center justify-center w-14 h-14 bg-slate-900 rounded-xl shadow-lg">
                  <Zap className="w-7 h-7 text-white" />
                </div>
                <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
                  PartnerPulse
                </h1>
              </div>
              <p className="text-sm text-slate-500">
                AI-Powered Assistant for Amazon Marketplace Supplier Management
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <p className="text-sm font-semibold text-slate-900">{user.username}</p>
                <p className="text-xs text-slate-600">{user.roleName}</p>
              </div>
              <button
                onClick={handleLogout}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg font-medium text-sm transition-colors flex items-center gap-2"
              >
                <LogOut className="w-4 h-4" />
                Logout
              </button>
            </div>
          </div>

          {activeTab === 'add-data' && canAccessAddData && <AddSupplierData />}
          {activeTab === 'add-data' && !canAccessAddData && (
            <div className="card">
              <div className="text-center py-12">
                <p className="text-slate-600 font-medium">You don't have access to this page.</p>
              </div>
            </div>
          )}
          
          {activeTab === 'query' && canAccessQuery && (
            <QuerySupplier 
              modelId={modelId}
              queryHistory={queryHistory}
              setQueryHistory={setQueryHistory}
            />
          )}
          {activeTab === 'query' && !canAccessQuery && (
            <div className="card">
              <div className="text-center py-12">
                <p className="text-slate-600 font-medium">You don't have access to this page.</p>
              </div>
            </div>
          )}
          
          {activeTab === 'crm' && canAccessCRM && <AddSupplierProfile />}
          {activeTab === 'crm' && !canAccessCRM && (
            <div className="card">
              <div className="text-center py-12">
                <p className="text-slate-600 font-medium">You don't have access to this page.</p>
              </div>
            </div>
          )}
          
          {activeTab === 'all-suppliers' && canAccessAllSuppliers && <AllSuppliers />}
        </div>
      </main>
    </div>
  );
}

export default App;

