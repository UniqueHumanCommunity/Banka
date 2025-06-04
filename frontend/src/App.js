import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('banka_token'));
  const [events, setEvents] = useState([]);
  const [publicEvents, setPublicEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [loading, setLoading] = useState(false);
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState(null);
  const [networkAdded, setNetworkAdded] = useState(false);
  const [userProfile, setUserProfile] = useState(null);

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // BNB Chain Testnet configuration
  const BNB_TESTNET_CONFIG = {
    chainId: '0x61', // 97 in decimal
    chainName: 'BNB Smart Chain Testnet',
    nativeCurrency: {
      name: 'BNB',
      symbol: 'tBNB',
      decimals: 18
    },
    rpcUrls: ['https://data-seed-prebsc-1-s1.binance.org:8545/'],
    blockExplorerUrls: ['https://testnet.bscscan.com/']
  };

  // Initialize app
  useEffect(() => {
    checkAPIHealth();
    checkWalletConnection();
    if (token) {
      loadUserProfile();
    }
    loadPublicEvents();
  }, [token]);

  // Load user profile and events
  const loadUserProfile = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setUserProfile(data);
        setUser(data.user);
        setEvents(data.events || []);
      } else if (response.status === 401) {
        // Token expired
        logout();
      }
    } catch (error) {
      console.error('Failed to load profile:', error);
    }
  };

  const loadPublicEvents = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/events/public`);
      const data = await response.json();
      setPublicEvents(data.events || []);
    } catch (error) {
      console.error('Failed to load public events:', error);
    }
  };

  const checkAPIHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/health`);
      const data = await response.json();
      console.log('API Health:', data);
    } catch (error) {
      console.error('API Health Check Failed:', error);
    }
  };

  // Authentication functions
  const login = async (email, password) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });
      
      const data = await response.json();
      if (response.ok) {
        setToken(data.token);
        setUser(data.user);
        localStorage.setItem('banka_token', data.token);
        await loadUserProfile();
        setCurrentView('dashboard');
        alert('Login realizado com sucesso!');
      } else {
        alert('Erro no login: ' + data.detail);
      }
    } catch (error) {
      alert('Erro no login: ' + error.message);
    }
    setLoading(false);
  };

  const register = async (userData) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      
      const data = await response.json();
      if (response.ok) {
        setToken(data.token);
        setUser(data.user);
        localStorage.setItem('banka_token', data.token);
        await loadUserProfile();
        setCurrentView('dashboard');
        alert('Registro realizado com sucesso! Carteira blockchain criada.');
      } else {
        alert('Erro no registro: ' + data.detail);
      }
    } catch (error) {
      alert('Erro no registro: ' + error.message);
    }
    setLoading(false);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    setUserProfile(null);
    setEvents([]);
    localStorage.removeItem('banka_token');
    setCurrentView('home');
  };

  // Wallet connection functions
  const checkWalletConnection = async () => {
    if (typeof window.ethereum !== 'undefined') {
      try {
        const accounts = await window.ethereum.request({ method: 'eth_accounts' });
        if (accounts.length > 0) {
          setWalletConnected(true);
          setWalletAddress(accounts[0]);
          await checkNetwork();
        }
      } catch (error) {
        console.error('Error checking wallet connection:', error);
      }
    }
  };

  const checkNetwork = async () => {
    try {
      const chainId = await window.ethereum.request({ method: 'eth_chainId' });
      if (chainId === BNB_TESTNET_CONFIG.chainId) {
        setNetworkAdded(true);
      }
    } catch (error) {
      console.error('Error checking network:', error);
    }
  };

  const connectWallet = async () => {
    if (typeof window.ethereum === 'undefined') {
      alert('MetaMask não está instalado! Por favor, instale o MetaMask para continuar.');
      window.open('https://metamask.io/download.html', '_blank');
      return;
    }

    try {
      setLoading(true);
      
      const accounts = await window.ethereum.request({
        method: 'eth_requestAccounts',
      });
      
      if (accounts.length > 0) {
        setWalletConnected(true);
        setWalletAddress(accounts[0]);
        await addBNBTestnetNetwork();
      }
    } catch (error) {
      console.error('Error connecting wallet:', error);
      alert('Erro ao conectar carteira. Verifique o MetaMask e tente novamente.');
    } finally {
      setLoading(false);
    }
  };

  const addBNBTestnetNetwork = async () => {
    try {
      await window.ethereum.request({
        method: 'wallet_addEthereumChain',
        params: [BNB_TESTNET_CONFIG],
      });
      setNetworkAdded(true);
      alert('✅ Rede BNB Chain Testnet adicionada com sucesso!');
    } catch (error) {
      console.error('Error adding network:', error);
      if (error.code === 4902) {
        alert('❌ Erro ao adicionar rede. Tente novamente.');
      } else if (error.code === -32002) {
        alert('⏳ Solicitação pendente no MetaMask. Verifique o MetaMask.');
      } else {
        alert('❌ Erro ao adicionar rede BNB Chain Testnet.');
      }
    }
  };

  const switchToBNBTestnet = async () => {
    try {
      await window.ethereum.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: BNB_TESTNET_CONFIG.chainId }],
      });
      setNetworkAdded(true);
    } catch (error) {
      console.error('Error switching network:', error);
      if (error.code === 4902) {
        await addBNBTestnetNetwork();
      }
    }
  };

  const openFaucet = () => {
    window.open('https://testnet.binance.org/faucet-smart', '_blank');
  };

  // Event management functions
  const createEvent = async (eventData) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(eventData),
      });
      const data = await response.json();
      if (response.ok) {
        alert('Evento criado com sucesso!');
        await loadUserProfile();
      } else {
        alert('Erro ao criar evento: ' + data.detail);
      }
    } catch (error) {
      alert('Erro ao criar evento: ' + error.message);
    }
    setLoading(false);
  };

  const createToken = async (eventId, tokenData) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/events/${eventId}/tokens`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(tokenData),
      });
      const data = await response.json();
      if (response.ok) {
        alert('Token criado com sucesso!');
        await loadUserProfile();
      } else {
        alert('Erro ao criar token: ' + data.detail);
      }
    } catch (error) {
      alert('Erro ao criar token: ' + error.message);
    }
    setLoading(false);
  };

  // Home Page Component
  const HomePage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-16">
        {/* Header with Auth */}
        <div className="absolute top-4 right-4 flex items-center space-x-4">
          {!user ? (
            <>
              <button
                onClick={() => setCurrentView('login')}
                className="px-6 py-2 text-white border border-white/30 rounded-lg hover:bg-white/10 transition-all"
              >
                Login
              </button>
              <button
                onClick={() => setCurrentView('register')}
                className="px-6 py-2 bg-yellow-500 text-black rounded-lg hover:bg-yellow-600 transition-all font-medium"
              >
                Registrar
              </button>
            </>
          ) : (
            <div className="flex items-center space-x-4">
              <div className="text-white text-sm">
                Olá, {user.name} (ADMIN)
              </div>
              <button
                onClick={() => setCurrentView('profile')}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Perfil
              </button>
              <button
                onClick={logout}
                className="px-4 py-2 text-white border border-white/30 rounded-lg hover:bg-red-500/20"
              >
                Sair
              </button>
            </div>
          )}
        </div>

        {/* Wallet Connection for non-authenticated users */}
        {!user && !walletConnected && (
          <div className="absolute top-4 left-4">
            <button
              onClick={connectWallet}
              disabled={loading}
              className="bg-yellow-500 hover:bg-yellow-600 text-black font-bold px-6 py-3 rounded-lg shadow-lg transition-all duration-200 hover:scale-105 disabled:opacity-50"
            >
              {loading ? '🔄 Conectando...' : '🦊 Conectar MetaMask'}
            </button>
          </div>
        )}

        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-white mb-6">
            Ban<span className="text-yellow-400">Ka</span>
          </h1>
          <p className="text-2xl text-blue-200 mb-8">
            O caixa do seu evento na era digital
          </p>
          <p className="text-lg text-blue-300 max-w-2xl mx-auto mb-8">
            Revolucione a experiência de pagamento em eventos com tokens digitais seguros na blockchain.
            Sem filas, sem dinheiro físico, apenas tecnologia.
          </p>
          
          <div className="bg-orange-500/20 border border-orange-400 rounded-lg p-4 max-w-2xl mx-auto">
            <p className="text-orange-200 font-medium">
              🚀 <strong>MODO APRESENTAÇÃO ATIVO:</strong> Todos os usuários têm privilégios de administrador
            </p>
          </div>
        </div>

        {user ? (
          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            <div 
              onClick={() => setCurrentView('dashboard')}
              className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105"
            >
              <div className="text-6xl mb-4">🎪</div>
              <h3 className="text-2xl font-bold text-white mb-4">Meus Eventos</h3>
              <p className="text-blue-200">
                Gerencie seus eventos e tokens
              </p>
            </div>

            <div 
              onClick={() => setCurrentView('marketplace')}
              className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105"
            >
              <div className="text-6xl mb-4">🎫</div>
              <h3 className="text-2xl font-bold text-white mb-4">Marketplace</h3>
              <p className="text-blue-200">
                Compre e transfira tokens
              </p>
            </div>

            <div 
              onClick={() => setCurrentView('profile')}
              className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105"
            >
              <div className="text-6xl mb-4">👤</div>
              <h3 className="text-2xl font-bold text-white mb-4">Perfil</h3>
              <p className="text-blue-200">
                Carteira e configurações
              </p>
            </div>
          </div>
        ) : (
          <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div 
              onClick={() => setCurrentView('register')}
              className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105"
            >
              <div className="text-6xl mb-4">🎪</div>
              <h3 className="text-2xl font-bold text-white mb-4">Organizador</h3>
              <p className="text-blue-200">
                Crie eventos, gerencie tokens e monitore vendas
              </p>
            </div>

            <div 
              onClick={() => setCurrentView('marketplace')}
              className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105"
            >
              <div className="text-6xl mb-4">🎫</div>
              <h3 className="text-2xl font-bold text-white mb-4">Participante</h3>
              <p className="text-blue-200">
                Compre tokens e pague vendedores
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );

  // Login Component
  const LoginPage = () => {
    const [formData, setFormData] = useState({ email: '', password: '' });

    const handleSubmit = (e) => {
      e.preventDefault();
      login(formData.email, formData.password);
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-gray-800">Login</h2>
            <p className="text-gray-600 mt-2">Entre na sua conta BanKa</p>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                name="email"
                id="email"
                required
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Senha</label>
              <input
                type="password"
                name="password"
                id="password"
                required
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium mb-4"
            >
              {loading ? 'Entrando...' : 'Entrar'}
            </button>
          </form>
          
          <div className="text-center">
            <button
              onClick={() => setCurrentView('register')}
              className="text-blue-600 hover:underline"
            >
              Não tem conta? Registre-se
            </button>
            <br />
            <button
              onClick={() => setCurrentView('home')}
              className="text-gray-600 hover:underline mt-2"
            >
              ← Voltar
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Register Component
  const RegisterPage = () => {
    const [formData, setFormData] = useState({
      name: '',
      email: '',
      password: '',
      phone: ''
    });

    const handleSubmit = (e) => {
      e.preventDefault();
      register(formData);
    };

    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900 flex items-center justify-center">
        <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
          <div className="text-center mb-6">
            <h2 className="text-3xl font-bold text-gray-800">Registrar</h2>
            <p className="text-gray-600 mt-2">Crie sua conta BanKa com carteira blockchain</p>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Nome Completo</label>
              <input
                type="text"
                name="name"
                id="name"
                required
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                name="email"
                id="reg_email"
                required
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                value={formData.email}
                onChange={(e) => setFormData({...formData, email: e.target.value})}
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2">Senha (mín. 6 caracteres)</label>
              <input
                type="password"
                name="password"
                id="reg_password"
                required
                minLength="6"
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                value={formData.password}
                onChange={(e) => setFormData({...formData, password: e.target.value})}
              />
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2">Telefone (opcional)</label>
              <input
                type="tel"
                name="phone"
                id="phone"
                className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium mb-4"
            >
              {loading ? 'Criando conta...' : 'Criar Conta & Carteira'}
            </button>
          </form>
          
          <div className="text-center">
            <button
              onClick={() => setCurrentView('login')}
              className="text-blue-600 hover:underline"
            >
              Já tem conta? Faça login
            </button>
            <br />
            <button
              onClick={() => setCurrentView('home')}
              className="text-gray-600 hover:underline mt-2"
            >
              ← Voltar
            </button>
          </div>
        </div>
      </div>
    );
  };

  // Profile Page Component
  const ProfilePage = () => {
    const [showPrivateKey, setShowPrivateKey] = useState(false);

    if (!userProfile) {
      return (
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="spinner mb-4"></div>
            <p>Carregando perfil...</p>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">Meu Perfil</h1>
            <button
              onClick={() => setCurrentView('home')}
              className="px-4 py-2 text-blue-600 hover:text-blue-800"
            >
              ← Voltar
            </button>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* User Info */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
                <h3 className="text-xl font-bold mb-4">Informações Pessoais</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-600">Nome</label>
                    <p className="text-lg">{userProfile.user.name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600">Email</label>
                    <p className="text-lg">{userProfile.user.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600">Membro desde</label>
                    <p className="text-lg">{new Date(userProfile.user.created_at).toLocaleDateString('pt-BR')}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-600">Telefone</label>
                    <p className="text-lg">{userProfile.user.phone || 'Não informado'}</p>
                  </div>
                </div>
              </div>

              {/* Blockchain Wallet */}
              <div className="bg-white rounded-xl shadow-sm border p-6 mb-6">
                <h3 className="text-xl font-bold mb-4">🔗 Carteira Blockchain</h3>
                
                <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-lg p-4 mb-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm opacity-80">Saldo BNB</p>
                      <p className="text-2xl font-bold">{userProfile.wallet.assets.bnb_balance} tBNB</p>
                    </div>
                    <div className="text-4xl">💰</div>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="block text-sm font-medium text-gray-600">Endereço da Carteira</label>
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-mono bg-gray-100 p-2 rounded flex-1">
                        {userProfile.wallet.address}
                      </p>
                      <button
                        onClick={() => navigator.clipboard.writeText(userProfile.wallet.address)}
                        className="px-3 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                      >
                        Copiar
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-600">Chave Privada</label>
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-mono bg-gray-100 p-2 rounded flex-1">
                        {showPrivateKey ? userProfile.wallet.private_key : '••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••'}
                      </p>
                      <button
                        onClick={() => setShowPrivateKey(!showPrivateKey)}
                        className="px-3 py-2 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
                      >
                        {showPrivateKey ? '🙈' : '👁️'}
                      </button>
                      {showPrivateKey && (
                        <button
                          onClick={() => navigator.clipboard.writeText(userProfile.wallet.private_key)}
                          className="px-3 py-2 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                        >
                          Copiar
                        </button>
                      )}
                    </div>
                    <p className="text-xs text-red-600 mt-1">
                      ⚠️ Nunca compartilhe sua chave privada com ninguém!
                    </p>
                  </div>

                  <div className="flex space-x-3">
                    <a
                      href={`https://testnet.bscscan.com/address/${userProfile.wallet.address}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 text-sm"
                    >
                      Ver no BSCScan
                    </a>
                    <button
                      onClick={openFaucet}
                      className="px-4 py-2 bg-yellow-500 text-black rounded hover:bg-yellow-600 text-sm"
                    >
                      Obter tBNB Grátis
                    </button>
                  </div>
                </div>
              </div>

              {/* Token Assets */}
              <div className="bg-white rounded-xl shadow-sm border p-6">
                <h3 className="text-xl font-bold mb-4">🎫 Meus Tokens</h3>
                {userProfile.wallet.assets.tokens && userProfile.wallet.assets.tokens.length > 0 ? (
                  <div className="grid gap-4">
                    {userProfile.wallet.assets.tokens.map((token, index) => (
                      <div key={index} className="bg-gray-50 rounded-lg p-4">
                        <div className="flex justify-between items-center">
                          <div>
                            <h4 className="font-bold">{token.name}</h4>
                            <p className="text-sm text-gray-600">{token.event_name}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-2xl font-bold">{token.balance}</p>
                            <p className="text-sm text-gray-600">tokens</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">Nenhum token encontrado</p>
                )}
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Events Summary */}
              <div className="bg-white rounded-xl shadow-sm border p-6">
                <h3 className="text-lg font-bold mb-4">📊 Meus Eventos</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span>Eventos criados:</span>
                    <span className="font-bold">{userProfile.events.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Eventos ativos:</span>
                    <span className="font-bold">
                      {userProfile.events.filter(e => e.is_active).length}
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setCurrentView('dashboard')}
                  className="w-full mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Gerenciar Eventos
                </button>
              </div>

              {/* Recent Transactions */}
              <div className="bg-white rounded-xl shadow-sm border p-6">
                <h3 className="text-lg font-bold mb-4">💳 Transações Recentes</h3>
                {userProfile.recent_transactions && userProfile.recent_transactions.length > 0 ? (
                  <div className="space-y-3">
                    {userProfile.recent_transactions.slice(0, 5).map((tx, index) => (
                      <div key={index} className="border-b pb-2 last:border-b-0">
                        <div className="flex justify-between">
                          <span className="text-sm">
                            {tx.type === 'purchase' ? '💰 Compra' : '📤 Transferência'}
                          </span>
                          <span className="text-sm font-bold">{tx.amount}</span>
                        </div>
                        <p className="text-xs text-gray-500">
                          {new Date(tx.timestamp).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-sm">Nenhuma transação</p>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Dashboard Component
  const DashboardPage = () => {
    const [showCreateEvent, setShowCreateEvent] = useState(false);
    const [showCreateToken, setShowCreateToken] = useState(false);

    const CreateEventForm = () => {
      const [formData, setFormData] = useState({
        name: '',
        date: '',
        description: '',
        location: ''
      });

      const handleSubmit = (e) => {
        e.preventDefault();
        createEvent({
          ...formData,
          date: new Date(formData.date).toISOString()
        });
        setShowCreateEvent(false);
        setFormData({ name: '', date: '', description: '', location: '' });
      };

      return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <h3 className="text-2xl font-bold mb-6">Criar Novo Evento</h3>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Nome do Evento</label>
                <input
                  type="text"
                  required
                  className="w-full p-3 border rounded-lg"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Data do Evento</label>
                <input
                  type="datetime-local"
                  required
                  className="w-full p-3 border rounded-lg"
                  value={formData.date}
                  onChange={(e) => setFormData({...formData, date: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Local</label>
                <input
                  type="text"
                  className="w-full p-3 border rounded-lg"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Descrição</label>
                <textarea
                  className="w-full p-3 border rounded-lg"
                  rows="3"
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowCreateEvent(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Criando...' : 'Criar Evento'}
                </button>
              </div>
            </form>
          </div>
        </div>
      );
    };

    const CreateTokenForm = () => {
      const [formData, setFormData] = useState({
        name: '',
        price_cents: '',
        initial_supply: '',
        sale_mode: 'both'
      });

      const handleSubmit = (e) => {
        e.preventDefault();
        createToken(selectedEvent.id, {
          ...formData,
          price_cents: parseInt(formData.price_cents),
          initial_supply: parseInt(formData.initial_supply)
        });
        setShowCreateToken(false);
        setFormData({ name: '', price_cents: '', initial_supply: '', sale_mode: 'both' });
      };

      return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <h3 className="text-2xl font-bold mb-6">Criar Token</h3>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Nome do Token</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: CERVEJA, HOTDOG"
                  className="w-full p-3 border rounded-lg"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Preço (centavos)</label>
                <input
                  type="number"
                  required
                  placeholder="Ex: 500 (R$ 5,00)"
                  className="w-full p-3 border rounded-lg"
                  value={formData.price_cents}
                  onChange={(e) => setFormData({...formData, price_cents: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Quantidade Inicial</label>
                <input
                  type="number"
                  required
                  placeholder="Ex: 1000"
                  className="w-full p-3 border rounded-lg"
                  value={formData.initial_supply}
                  onChange={(e) => setFormData({...formData, initial_supply: e.target.value})}
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Modo de Venda</label>
                <select
                  className="w-full p-3 border rounded-lg"
                  value={formData.sale_mode}
                  onChange={(e) => setFormData({...formData, sale_mode: e.target.value})}
                >
                  <option value="both">Online + Offline</option>
                  <option value="online">Apenas Online (Crypto)</option>
                  <option value="offline">Apenas Offline (Caixa)</option>
                </select>
              </div>
              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowCreateToken(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Criando...' : 'Criar Token'}
                </button>
              </div>
            </form>
          </div>
        </div>
      );
    };

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">Meus Eventos</h1>
            <div className="flex space-x-4">
              <button
                onClick={() => setCurrentView('profile')}
                className="px-4 py-2 text-blue-600 hover:text-blue-800"
              >
                Perfil
              </button>
              <button
                onClick={() => setCurrentView('home')}
                className="px-4 py-2 text-blue-600 hover:text-blue-800"
              >
                ← Home
              </button>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold">Dashboard</h2>
            <button
              onClick={() => setShowCreateEvent(true)}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
            >
              + Criar Evento
            </button>
          </div>

          <div className="grid gap-6">
            {events.map((event) => (
              <div key={event.id} className="bg-white rounded-xl shadow-sm border p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">{event.name}</h3>
                    <p className="text-gray-600">
                      {new Date(event.date).toLocaleDateString('pt-BR')} 
                      {event.location && ` • ${event.location}`}
                    </p>
                    {event.description && (
                      <p className="text-gray-600 mt-2">{event.description}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => {
                        setSelectedEvent(event);
                        setShowCreateToken(true);
                      }}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                    >
                      + Token
                    </button>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h4 className="font-medium mb-3">Tokens do Evento:</h4>
                  {event.tokens && event.tokens.length > 0 ? (
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {event.tokens.map((token) => (
                        <div key={token.id} className="bg-gray-50 rounded-lg p-4">
                          <div className="flex justify-between items-start mb-2">
                            <div className="font-medium">{token.name}</div>
                            <a
                              href={`https://testnet.bscscan.com/address/${token.contract_address}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="text-blue-500 hover:text-blue-700"
                              title="Ver contrato no BSCScan"
                            >
                              ℹ️
                            </a>
                          </div>
                          <div className="text-sm text-gray-600">
                            R$ {(token.price_cents / 100).toFixed(2)}
                          </div>
                          <div className="text-sm text-gray-600">
                            Estoque: {token.initial_supply - token.total_sold}
                          </div>
                          <div className="text-xs mt-1">
                            <span className={`px-2 py-1 rounded-full ${
                              token.sale_mode === 'online' ? 'bg-blue-100 text-blue-800' :
                              token.sale_mode === 'offline' ? 'bg-green-100 text-green-800' :
                              'bg-purple-100 text-purple-800'
                            }`}>
                              {token.sale_mode === 'online' ? 'Online' : 
                               token.sale_mode === 'offline' ? 'Offline' : 'Online + Offline'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">Nenhum token criado ainda</p>
                  )}
                </div>
              </div>
            ))}
          </div>

          {events.length === 0 && (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">🎪</div>
              <h3 className="text-xl font-medium text-gray-600 mb-2">
                Nenhum evento criado ainda
              </h3>
              <p className="text-gray-500">
                Clique em "Criar Evento" para começar
              </p>
            </div>
          )}
        </div>

        {showCreateEvent && <CreateEventForm />}
        {showCreateToken && <CreateTokenForm />}
      </div>
    );
  };

  // Marketplace Component with offline transfer
  const MarketplacePage = () => {
    const [showOfflineTransfer, setShowOfflineTransfer] = useState(false);
    const [offlineFormData, setOfflineFormData] = useState({
      user_email: '',
      token_address: '',
      amount: '',
      cashier_id: 'Transferência Livre'
    });

    const OfflineTransferForm = () => {
      const handleSubmit = async (e) => {
        e.preventDefault();
        if (!user) {
          alert('Você precisa estar logado para realizar transferências');
          return;
        }

        setLoading(true);
        try {
          const response = await fetch(`${API_BASE}/api/transfer/offline`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify(offlineFormData),
          });
          
          const data = await response.json();
          if (response.ok) {
            alert('✅ Tokens transferidos com sucesso!');
            setShowOfflineTransfer(false);
            setOfflineFormData({ user_email: '', token_address: '', amount: '', cashier_id: 'Transferência Livre' });
          } else {
            alert('❌ Erro: ' + data.detail);
          }
        } catch (error) {
          alert('❌ Erro na transferência: ' + error.message);
        }
        setLoading(false);
      };

      return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <h3 className="text-2xl font-bold mb-6">🎁 Transferência Livre de Tokens</h3>
            <p className="text-gray-600 mb-6 text-sm">
              <strong>Modo Admin:</strong> Transfira qualquer quantidade de tokens para qualquer usuário instantaneamente.
            </p>
            
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">📧 Email do Destinatário</label>
                <input
                  type="email"
                  required
                  placeholder="usuario@email.com"
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500"
                  value={offlineFormData.user_email}
                  onChange={(e) => setOfflineFormData({...offlineFormData, user_email: e.target.value})}
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">🎫 Token</label>
                <select
                  required
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500"
                  value={offlineFormData.token_address}
                  onChange={(e) => setOfflineFormData({...offlineFormData, token_address: e.target.value})}
                >
                  <option value="">Selecione um token</option>
                  {publicEvents.map(event => 
                    event.tokens?.map(token => (
                      <option key={token.contract_address} value={token.contract_address}>
                        {token.name} - {event.name} - R$ {(token.price_cents / 100).toFixed(2)}
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">📊 Quantidade</label>
                <input
                  type="number"
                  required
                  min="1"
                  placeholder="Ex: 10"
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500"
                  value={offlineFormData.amount}
                  onChange={(e) => setOfflineFormData({...offlineFormData, amount: e.target.value})}
                />
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">🏪 Origem/Motivo</label>
                <input
                  type="text"
                  placeholder="Ex: Gift, Promoção, Admin Transfer"
                  className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-green-500"
                  value={offlineFormData.cashier_id}
                  onChange={(e) => setOfflineFormData({...offlineFormData, cashier_id: e.target.value})}
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                <p className="text-sm text-blue-800">
                  <strong>🔓 Modo Apresentação:</strong> Esta transferência é livre e não requer validação de pagamento.
                </p>
              </div>

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowOfflineTransfer(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {loading ? 'Transferindo...' : '🚀 Transferir'}
                </button>
              </div>
            </form>
          </div>
        </div>
      );
    };

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-gray-800">🛍️ Marketplace de Tokens</h1>
            <div className="flex space-x-4">
              {user && (
                <button
                  onClick={() => setShowOfflineTransfer(true)}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
                >
                  🎁 Transferir Tokens
                </button>
              )}
              <button
                onClick={() => setCurrentView('home')}
                className="px-4 py-2 text-blue-600 hover:text-blue-800"
              >
                ← Voltar
              </button>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          {/* Info Cards */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl p-6">
              <h3 className="text-xl font-bold mb-2">💳 Compra Online</h3>
              <p className="text-blue-100 mb-4">
                Participantes podem comprar tokens diretamente com criptomoedas
              </p>
              <div className="text-sm bg-white/20 rounded-lg p-3">
                <p>✅ Pagamento instantâneo</p>
                <p>✅ Tokens na carteira imediatamente</p>
                <p>✅ Sem intermediários</p>
              </div>
            </div>

            <div className="bg-gradient-to-r from-green-500 to-teal-600 text-white rounded-xl p-6">
              <h3 className="text-xl font-bold mb-2">🎁 Transferência Livre</h3>
              <p className="text-green-100 mb-4">
                Durante a apresentação, qualquer usuário pode transferir tokens livremente
              </p>
              <div className="text-sm bg-white/20 rounded-lg p-3">
                <p>✅ Transferência instantânea</p>
                <p>✅ Sem validação de pagamento</p>
                <p>✅ Modo admin ativo</p>
              </div>
            </div>
          </div>

          {/* Events Grid */}
          <div className="grid gap-6">
            {publicEvents.map((event) => (
              <div key={event.id} className="bg-white rounded-xl shadow-sm border p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold mb-2">{event.name}</h3>
                    <p className="text-gray-600 mb-2">
                      📅 {new Date(event.date).toLocaleDateString('pt-BR')}
                      {event.location && ` • 📍 ${event.location}`}
                    </p>
                    {event.description && (
                      <p className="text-gray-600 mb-4">{event.description}</p>
                    )}
                  </div>
                  <div className="text-right">
                    <span className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                      🟢 Ativo
                    </span>
                  </div>
                </div>
                
                {event.tokens && event.tokens.length > 0 ? (
                  <div>
                    <h4 className="font-medium mb-3">🎫 Tokens Disponíveis:</h4>
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {event.tokens.map((token) => (
                        <div key={token.id} className="bg-gray-50 rounded-lg p-4 border">
                          <div className="flex justify-between items-start mb-2">
                            <div className="font-medium text-lg">{token.name}</div>
                            <div className="flex items-center space-x-2">
                              <div className="text-lg font-bold text-green-600">
                                R$ {(token.price_cents / 100).toFixed(2)}
                              </div>
                              <a
                                href={`https://testnet.bscscan.com/address/${token.contract_address}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-500 hover:text-blue-700 text-lg"
                                title="Ver contrato no BSCScan"
                              >
                                ℹ️
                              </a>
                            </div>
                          </div>
                          
                          <div className="text-sm text-gray-600 mb-3">
                            📦 Disponível: {token.initial_supply - token.total_sold}
                          </div>
                          
                          <div className="mb-3">
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              token.sale_mode === 'online' ? 'bg-blue-100 text-blue-800' :
                              token.sale_mode === 'offline' ? 'bg-green-100 text-green-800' :
                              'bg-purple-100 text-purple-800'
                            }`}>
                              {token.sale_mode === 'online' ? '💳 Apenas Online' : 
                               token.sale_mode === 'offline' ? '🏪 Apenas Offline' : 
                               '💳🏪 Online + Offline'}
                            </span>
                          </div>
                          
                          <div className="text-xs text-gray-500 mb-3 font-mono">
                            {token.contract_address?.substr(0, 12)}...
                          </div>
                          
                          <div className="flex gap-2">
                            {(token.sale_mode === 'online' || token.sale_mode === 'both') && user && (
                              <button className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                                💳 Comprar
                              </button>
                            )}
                            {user && (
                              <button 
                                onClick={() => {
                                  setOfflineFormData(prev => ({...prev, token_address: token.contract_address}));
                                  setShowOfflineTransfer(true);
                                }}
                                className="flex-1 px-3 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
                              >
                                🎁 Transferir
                              </button>
                            )}
                            {!user && (
                              <button 
                                onClick={() => setCurrentView('login')}
                                className="w-full px-3 py-2 bg-gray-400 text-white rounded text-sm"
                              >
                                Fazer Login
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">📭 Nenhum token disponível para este evento</p>
                )}
              </div>
            ))}
          </div>

          {publicEvents.length === 0 && (
            <div className="text-center py-16">
              <div className="text-6xl mb-4">🎪</div>
              <h3 className="text-xl font-medium text-gray-600 mb-2">
                Nenhum evento disponível
              </h3>
              <p className="text-gray-500">
                Aguarde novos eventos serem criados
              </p>
            </div>
          )}
        </div>

        {showOfflineTransfer && <OfflineTransferForm />}
      </div>
    );
  };

  // Main App Router
  const renderCurrentView = () => {
    switch (currentView) {
      case 'login':
        return <LoginPage />;
      case 'register':
        return <RegisterPage />;
      case 'profile':
        return user ? <ProfilePage /> : <LoginPage />;
      case 'dashboard':
        return user ? <DashboardPage /> : <LoginPage />;
      case 'marketplace':
        return <MarketplacePage />;
      default:
        return <HomePage />;
    }
  };

  return (
    <div className="App">
      {renderCurrentView()}
    </div>
  );
}

export default App;