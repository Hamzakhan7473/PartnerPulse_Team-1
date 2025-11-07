import { useState } from 'react';
import { LogIn, Briefcase, Users, UserCheck, Zap } from 'lucide-react';

const USER_ROLES = [
  {
    id: 'sales',
    name: 'Sales Personnel',
    description: 'Access to supplier information management',
    icon: Briefcase,
    color: 'from-blue-600 to-blue-700',
  },
  {
    id: 'operations',
    name: 'Operations and Logistic Personnel',
    description: 'Access to supplier information management',
    icon: Users,
    color: 'from-emerald-600 to-emerald-700',
  },
  {
    id: 'head-sales',
    name: 'Supplier Account Manager',
    description: 'Access to supplier query and analytics',
    icon: UserCheck,
    color: 'from-purple-600 to-purple-700',
  },
];

function Login({ onLogin }) {
  const [selectedRole, setSelectedRole] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleRoleSelect = (roleId) => {
    setSelectedRole(roleId);
    setError('');
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!selectedRole) {
      setError('Please select a role');
      return;
    }

    if (!username.trim()) {
      setError('Please enter your username');
      return;
    }

    if (!password.trim()) {
      setError('Please enter your password');
      return;
    }

    // Simple authentication (in production, this would call an API)
    // For demo purposes, we'll accept any password
    const userData = {
      username,
      role: selectedRole,
      roleName: USER_ROLES.find(r => r.id === selectedRole)?.name,
      loginTime: new Date().toISOString(),
    };

    // Store in localStorage
    localStorage.setItem('user', JSON.stringify(userData));
    
    // Call parent callback
    onLogin(userData);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-slate-200 flex items-center justify-center p-4 animated-bg relative overflow-hidden">
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
      
      <div className="w-full max-w-4xl">
        <div className="text-center mb-8">
          <div className="flex flex-col items-center">
            <div className="flex items-center gap-4 mb-3">
              <div className="inline-flex items-center justify-center w-16 h-16 bg-slate-900 rounded-2xl shadow-lg">
                <Zap className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-4xl font-bold text-slate-900">PartnerPulse</h1>
            </div>
            <p className="text-slate-600 text-sm">
              AI-Powered Assistant for Amazon Marketplace Supplier Management
            </p>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden relative z-10">
          <div className="grid md:grid-cols-2">
            {/* Left Side - Role Selection */}
            <div className="bg-gradient-to-br from-slate-900 to-slate-800 p-8 text-white">
              <h2 className="text-2xl font-bold mb-6">Select Your Role</h2>
              <div className="space-y-4">
                {USER_ROLES.map((role) => {
                  const Icon = role.icon;
                  const isSelected = selectedRole === role.id;
                  return (
                    <button
                      key={role.id}
                      onClick={() => handleRoleSelect(role.id)}
                      className={`w-full p-4 rounded-xl border-2 transition-all duration-200 text-left ${
                        isSelected
                          ? `bg-gradient-to-r ${role.color} border-white shadow-lg transform scale-105`
                          : 'bg-slate-800/50 border-slate-700 hover:bg-slate-800 hover:border-slate-600'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                          isSelected ? 'bg-white/20' : 'bg-slate-700'
                        }`}>
                          <Icon className="w-5 h-5" />
                        </div>
                        <div className="flex-1">
                          <p className={`font-bold ${isSelected ? 'text-white' : 'text-slate-200'}`}>
                            {role.name}
                          </p>
                          <p className={`text-xs mt-1 ${isSelected ? 'text-white/90' : 'text-slate-400'}`}>
                            {role.description}
                          </p>
                        </div>
                        {isSelected && (
                          <div className="w-6 h-6 rounded-full bg-white flex items-center justify-center">
                            <div className="w-3 h-3 rounded-full bg-blue-600"></div>
                          </div>
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Right Side - Login Form */}
            <div className="p-8">
              <div className="mb-6">
                <h2 className="text-2xl font-bold text-slate-900 mb-2">Login</h2>
                <p className="text-slate-600 text-sm">
                  {selectedRole 
                    ? `Login as ${USER_ROLES.find(r => r.id === selectedRole)?.name}`
                    : 'Please select your role first'}
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-semibold text-slate-800 mb-2">
                    Username
                  </label>
                  <input
                    type="text"
                    value={username}
                    onChange={(e) => {
                      setUsername(e.target.value);
                      setError('');
                    }}
                    placeholder="Enter your username"
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-slate-50 hover:bg-white text-slate-900"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-800 mb-2">
                    Password
                  </label>
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      setError('');
                    }}
                    placeholder="Enter your password"
                    className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-500 focus:border-slate-500 transition-all duration-200 bg-slate-50 hover:bg-white text-slate-900"
                    required
                  />
                </div>

                {error && (
                  <div className="p-3 bg-red-50 border-l-4 border-red-500 rounded-lg">
                    <p className="text-sm text-red-800 font-medium">{error}</p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={!selectedRole}
                  className="w-full px-6 py-3.5 bg-slate-900 hover:bg-slate-950 text-white font-semibold rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed transform hover:scale-[1.02] active:scale-[0.98]"
                >
                  <LogIn className="w-5 h-5" />
                  <span>Login</span>
                </button>
              </form>

              <div className="mt-6 p-4 bg-slate-50 rounded-lg border border-slate-200">
                <p className="text-xs text-slate-600 font-medium">
                  <strong>Demo Mode:</strong> Any username and password will work. Select your role to continue.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Login;

