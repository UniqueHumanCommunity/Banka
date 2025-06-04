import React, { useState, useEffect } from 'react';
import { IDKitWidget, VerificationLevel, ISuccessResult } from '@worldcoin/idkit';
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
  const [loginType, setLoginType] = useState('');

  const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // World ID configuration
  const WORLD_APP_ID = 'app_2c25889e31357b3124c625f0f5db188f';
  const WORLD_ACTION = 'banka_login';

  // BNB Chain Testnet configuration
  const BNB_TESTNET_CONFIG = {
    chainId: '0x61',
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

  const loadUserProfile = async () => {
    if (!token) return;
    
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
        alert('Sessão expirada. Faça login novamente.');
        logout();
      } else {
        const errorData = await response.json();
        console.error('Failed to load profile:', errorData);
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
      setPublicEvents([]); // Ensure it's always an array
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

  const login = async (email, password, externalWallet = null) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          email, 
          password,
          external_wallet: externalWallet
        }),
      });
      
      const data = await response.json();
      if (response.ok) {
        setToken(data.token);
        setUser(data.user);
        localStorage.setItem('banka_token', data.token);
        await loadUserProfile();
        setCurrentView('dashboard');
        showSuccessMessage('Login realizado com sucesso!');
      } else {
        showErrorMessage('Erro no login: ' + data.detail);
      }
    } catch (error) {
      showErrorMessage('Erro no login: ' + error.message);
    }
    setLoading(false);
  };

  const register = async (userData, externalWallet = null) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          ...userData,
          external_wallet: externalWallet
        }),
      });
      
      const data = await response.json();
      if (response.ok) {
        setToken(data.token);
        setUser(data.user);
        localStorage.setItem('banka_token', data.token);
        await loadUserProfile();
        setCurrentView('dashboard');
        showSuccessMessage('Registro realizado com sucesso! Carteira blockchain criada.');
      } else {
        showErrorMessage('Erro no registro: ' + data.detail);
      }
    } catch (error) {
      showErrorMessage('Erro no registro: ' + error.message);
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
    setLoginType('');
  };

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
      showErrorMessage('MetaMask não está instalado! Por favor, instale o MetaMask para continuar.');
      window.open('https://metamask.io/download.html', '_blank');
      return null;
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
        return accounts[0];
      }
    } catch (error) {
      console.error('Error connecting wallet:', error);
      showErrorMessage('Erro ao conectar carteira. Verifique o MetaMask e tente novamente.');
    } finally {
      setLoading(false);
    }
    return null;
  };

  const addBNBTestnetNetwork = async () => {
    try {
      await window.ethereum.request({
        method: 'wallet_addEthereumChain',
        params: [BNB_TESTNET_CONFIG],
      });
      setNetworkAdded(true);
    } catch (error) {
      console.error('Error adding network:', error);
    }
  };

  const openFaucet = () => {
    window.open('https://testnet.binance.org/faucet-smart', '_blank');
  };

  // MetaMask Token Addition Function
  const addTokenToMetaMask = async (tokenAddress, tokenSymbol, tokenName, decimals = 18) => {
    if (typeof window.ethereum === 'undefined') {
      showErrorMessage('MetaMask não está instalado! Por favor, instale o MetaMask para continuar.');
      return;
    }

    try {
      setLoading(true);
      
      // First ensure user is connected to the correct network
      await addBNBTestnetNetwork();
      
      // Add token to MetaMask
      const wasAdded = await window.ethereum.request({
        method: 'wallet_watchAsset',
        params: {
          type: 'ERC20',
          options: {
            address: tokenAddress,
            symbol: tokenSymbol,
            decimals: decimals,
            image: null, // Could add token image URL here
          },
        },
      });

      if (wasAdded) {
        showSuccessMessage(`Token ${tokenSymbol} adicionado ao MetaMask com sucesso!`);
      } else {
        showErrorMessage('Token não foi adicionado ao MetaMask.');
      }
    } catch (error) {
      console.error('Error adding token to MetaMask:', error);
      showErrorMessage('Erro ao adicionar token ao MetaMask: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const showSuccessMessage = (message) => {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-green-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => {
      notification.remove();
    }, 3000);
  };

  const showErrorMessage = (message) => {
    const notification = document.createElement('div');
    notification.className = 'fixed top-4 right-4 bg-red-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 animate-bounce';
    notification.textContent = message;
    document.body.appendChild(notification);
    setTimeout(() => {
      notification.remove();
    }, 3000);
  };

  const createEvent = async (eventData) => {
    if (!token) {
      alert('Você precisa estar logado para criar um evento');
      setCurrentView('login');
      return;
    }

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
      } else if (response.status === 401) {
        alert('Sessão expirada. Faça login novamente.');
        logout();
      } else {
        alert('Erro ao criar evento: ' + (data.detail || 'Erro desconhecido'));
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
        showSuccessMessage('Token criado com sucesso!');
        await loadUserProfile();
      } else {
        showErrorMessage('Erro ao criar token: ' + data.detail);
      }
    } catch (error) {
      showErrorMessage('Erro ao criar token: ' + error.message);
    }
    setLoading(false);
  };

  const onWorldIDSuccess = (result) => {
    console.log('World ID verification successful:', result);
    showSuccessMessage('Verificação World ID realizada com sucesso!');
  };

  // Home Page Component - REDESIGNED
  const HomePage = () => (
    <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-16">
          <div className="flex justify-center items-center mb-8">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8">
              <h1 className="text-7xl font-bold text-white mb-4">
                Ban<span className="text-yellow-400">Ka</span>
              </h1>
              <div className="flex items-center justify-center space-x-4 text-white/80">
                <div className="w-12 h-px bg-white/40"></div>
                <span className="text-sm uppercase tracking-wider">Blockchain Event Payments</span>
                <div className="w-12 h-px bg-white/40"></div>
              </div>
            </div>
          </div>
          
          <p className="text-2xl text-blue-200 mb-6 font-light">
            O caixa do seu evento na era digital
          </p>
          <p className="text-lg text-blue-300 max-w-3xl mx-auto leading-relaxed">
            Sistema revolucionário de pagamentos para eventos usando tokens digitais na blockchain. 
            Elimine filas, dinheiro físico e complicações - apenas tecnologia de ponta.
          </p>

          {/* Status Indicators */}
          <div className="flex justify-center items-center space-x-8 mt-8">
            <div className="flex items-center space-x-2 text-green-400">
              <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
              <span className="text-sm">Blockchain Ativo</span>
            </div>
            <div className="flex items-center space-x-2 text-yellow-400">
              <div className="w-3 h-3 bg-yellow-400 rounded-full"></div>
              <span className="text-sm">Modo Apresentação</span>
            </div>
            {walletConnected && (
              <div className="flex items-center space-x-2 text-blue-400">
                <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
                <span className="text-sm">MetaMask Conectado</span>
              </div>
            )}
          </div>
        </header>

        {/* Authentication Section */}
        {!user ? (
          <div className="max-w-6xl mx-auto">
            {/* Login Type Selection */}
            {!loginType && (
              <div className="text-center mb-12">
                <h2 className="text-3xl font-bold text-white mb-8">Como você quer acessar o BanKa?</h2>
                <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
                  <div 
                    onClick={() => setLoginType('organizer')}
                    className="group bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105 border border-white/20"
                  >
                    <div className="text-6xl mb-6 group-hover:scale-110 transition-transform">🎪</div>
                    <h3 className="text-2xl font-bold text-white mb-4">Sou Organizador</h3>
                    <p className="text-blue-200 mb-6">
                      Crie eventos, gerencie tokens digitais e monitore vendas em tempo real
                    </p>
                    <ul className="text-sm text-blue-300 space-y-2">
                      <li>✅ Criar eventos na blockchain</li>
                      <li>✅ Emitir tokens personalizados</li>
                      <li>✅ Dashboard de vendas</li>
                      <li>✅ Gestão de caixas</li>
                    </ul>
                  </div>

                  <div 
                    onClick={() => setLoginType('participant')}
                    className="group bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105 border border-white/20"
                  >
                    <div className="text-6xl mb-6 group-hover:scale-110 transition-transform">🎫</div>
                    <h3 className="text-2xl font-bold text-white mb-4">Sou Participante</h3>
                    <p className="text-blue-200 mb-6">
                      Compre tokens, pague vendedores e gerencie sua carteira digital
                    </p>
                    <ul className="text-sm text-blue-300 space-y-2">
                      <li>✅ Carteira blockchain automática</li>
                      <li>✅ Comprar tokens facilmente</li>
                      <li>✅ Pagamentos via QR code</li>
                      <li>✅ Histórico transparente</li>
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Login/Register Forms */}
            {loginType && (
              <div className="max-w-md mx-auto">
                <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20">
                  <div className="text-center mb-6">
                    <button
                      onClick={() => setLoginType('')}
                      className="text-blue-300 hover:text-white mb-4 text-sm"
                    >
                      ← Voltar à seleção
                    </button>
                    <div className="text-4xl mb-4">
                      {loginType === 'organizer' ? '🎪' : '🎫'}
                    </div>
                    <h2 className="text-2xl font-bold text-white">
                      {loginType === 'organizer' ? 'Acesso para Organizadores' : 'Acesso para Participantes'}
                    </h2>
                    <p className="text-blue-200 mt-2">
                      Faça login ou crie sua conta no BanKa
                    </p>
                  </div>

                  <AuthenticationComponent loginType={loginType} />
                </div>
              </div>
            )}
          </div>
        ) : (
          /* User Dashboard Navigation */
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-8">
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-4 inline-block mb-8">
                <p className="text-white">
                  Bem-vindo, <span className="font-bold text-yellow-400">{user.name}</span>
                  <span className="ml-2 px-2 py-1 bg-orange-500/30 text-orange-200 rounded text-xs">ADMIN</span>
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-8">
              <div 
                onClick={() => setCurrentView('dashboard')}
                className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105 border border-white/20"
              >
                <div className="text-6xl mb-4">🎪</div>
                <h3 className="text-2xl font-bold text-white mb-4">Meus Eventos</h3>
                <p className="text-blue-200">
                  Gerencie seus eventos e tokens
                </p>
              </div>

              <div 
                onClick={() => setCurrentView('marketplace')}
                className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105 border border-white/20"
              >
                <div className="text-6xl mb-4">🛍️</div>
                <h3 className="text-2xl font-bold text-white mb-4">Marketplace</h3>
                <p className="text-blue-200">
                  Compre e transfira tokens
                </p>
              </div>

              <div 
                onClick={() => setCurrentView('profile')}
                className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105 border border-white/20"
              >
                <div className="text-6xl mb-4">👤</div>
                <h3 className="text-2xl font-bold text-white mb-4">Meu Perfil</h3>
                <p className="text-blue-200">
                  Carteira e configurações
                </p>
              </div>
            </div>

            <div className="text-center mt-8">
              <button
                onClick={logout}
                className="px-6 py-3 bg-red-500/20 text-red-200 rounded-lg hover:bg-red-500/30 transition-all border border-red-500/30"
              >
                Sair do Sistema
              </button>
            </div>
          </div>
        )}

        {/* Features Section */}
        <div className="mt-20 max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-white mb-4">Por que escolher o BanKa?</h3>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="bg-blue-500/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">⚡</span>
              </div>
              <h4 className="text-xl font-bold text-white mb-2">Instantâneo</h4>
              <p className="text-blue-300">Pagamentos em segundos via QR Code e blockchain</p>
            </div>
            <div className="text-center">
              <div className="bg-green-500/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🔒</span>
              </div>
              <h4 className="text-xl font-bold text-white mb-2">Seguro</h4>
              <p className="text-blue-300">BNB Chain Testnet para máxima segurança e transparência</p>
            </div>
            <div className="text-center">
              <div className="bg-purple-500/20 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">📱</span>
              </div>
              <h4 className="text-xl font-bold text-white mb-2">Simples</h4>
              <p className="text-blue-300">Interface intuitiva para todos os níveis de usuário</p>
            </div>
          </div>
        </div>

        {/* Blockchain Info Footer */}
        <footer className="mt-20 text-center">
          <div className="bg-white/5 backdrop-blur-lg rounded-xl p-6 max-w-2xl mx-auto border border-white/10">
            <h4 className="text-lg font-bold text-white mb-3">🔗 Tecnologia Blockchain</h4>
            <div className="text-sm text-blue-200 space-y-1">
              <p><strong>Rede:</strong> BNB Smart Chain Testnet</p>
              <p><strong>Contrato Principal:</strong> 0xB03c97E3357f1D4D33E421164a5205E36bACD779</p>
              <div className="flex justify-center space-x-4 mt-4">
                <a href="https://testnet.bscscan.com" target="_blank" rel="noopener noreferrer" 
                   className="text-yellow-400 hover:underline">Explorer</a>
                <a href="https://testnet.binance.org/faucet-smart" target="_blank" rel="noopener noreferrer" 
                   className="text-yellow-400 hover:underline">Faucet tBNB</a>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );

  // Authentication Component with multiple login methods
  const AuthenticationComponent = ({ loginType }) => {
    const [isLogin, setIsLogin] = useState(true);
    const [formData, setFormData] = useState({
      name: '',
      email: '',
      password: '',
      phone: ''
    });

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (isLogin) {
        await login(formData.email, formData.password);
      } else {
        await register(formData);
      }
    };

    const handleMetaMaskLogin = async () => {
      const walletAddress = await connectWallet();
      if (walletAddress) {
        if (isLogin) {
          await login(`metamask_${walletAddress.toLowerCase()}@banka.com`, 'metamask_login', walletAddress);
        } else {
          await register({
            name: `MetaMask User ${walletAddress.substr(0, 8)}`,
            email: `metamask_${walletAddress.toLowerCase()}@banka.com`,
            password: 'metamask_login',
            phone: ''
          }, walletAddress);
        }
      }
    };

    return (
      <div className="space-y-6">
        {/* Toggle Login/Register */}
        <div className="flex bg-white/10 rounded-lg p-1">
          <button
            onClick={() => setIsLogin(true)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
              isLogin ? 'bg-white/20 text-white' : 'text-white/70 hover:text-white'
            }`}
          >
            Fazer Login
          </button>
          <button
            onClick={() => setIsLogin(false)}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-all ${
              !isLogin ? 'bg-white/20 text-white' : 'text-white/70 hover:text-white'
            }`}
          >
            Criar Conta
          </button>
        </div>

        {/* Alternative Login Methods */}
        <div className="space-y-3">
          <button
            onClick={handleMetaMaskLogin}
            disabled={loading}
            className="w-full flex items-center justify-center space-x-3 py-3 px-4 bg-gradient-to-r from-orange-600 to-orange-700 hover:from-orange-700 hover:to-orange-800 text-white rounded-lg transition-all disabled:opacity-50 shadow-lg"
          >
            <span className="text-xl">🦊</span>
            <span>{isLogin ? 'Login' : 'Registrar'} com MetaMask</span>
          </button>
{/* World ID login removed */}
        </div>

        <div className="flex items-center">
          <div className="flex-1 border-t border-white/20"></div>
          <span className="px-4 text-white/60 text-sm">ou use email</span>
          <div className="flex-1 border-t border-white/20"></div>
        </div>

        {/* Traditional Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">Nome Completo</label>
              <input
                type="text"
                required
                className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Seu nome completo"
                value={formData.name}
                onChange={(e) => setFormData({...formData, name: e.target.value})}
              />
            </div>
          )}
          
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">Email</label>
            <input
              type="email"
              required
              className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="seu@email.com"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-white/80 mb-2">Senha</label>
            <input
              type="password"
              required
              minLength="6"
              className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="Mínimo 6 caracteres"
              value={formData.password}
              onChange={(e) => setFormData({...formData, password: e.target.value})}
            />
          </div>
          
          {!isLogin && (
            <div>
              <label className="block text-sm font-medium text-white/80 mb-2">Telefone (opcional)</label>
              <input
                type="tel"
                className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="(11) 99999-9999"
                value={formData.phone}
                onChange={(e) => setFormData({...formData, phone: e.target.value})}
              />
            </div>
          )}
          
          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-4 bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white rounded-lg font-medium transition-all disabled:opacity-50 shadow-lg"
          >
            {loading ? 'Processando...' : (isLogin ? 'Entrar' : 'Criar Conta & Carteira')}
          </button>
        </form>

        {/* Demo Accounts */}
        <div className="mt-6 p-4 bg-white/5 rounded-lg border border-white/10">
          <h4 className="text-sm font-medium text-white/80 mb-2">🎭 Contas Demo Disponíveis:</h4>
          <div className="text-xs text-white/60 space-y-1">
            <p><strong>Organizador:</strong> organizador@banka.com / 123456</p>
            <p><strong>Participante:</strong> participante@banka.com / 123456</p>
            <p><strong>Caixa:</strong> caixa@banka.com / 123456</p>
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
        <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 flex items-center justify-center">
          <div className="text-center">
            <div className="w-16 h-16 border-4 border-white/20 border-t-white rounded-full animate-spin mx-auto mb-4"></div>
            <p className="text-white">Carregando perfil...</p>
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
        <div className="bg-white/10 backdrop-blur-lg border-b border-white/20">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-white">💎 Meu Perfil</h1>
            <button
              onClick={() => setCurrentView('home')}
              className="px-4 py-2 text-white/80 hover:text-white transition-all"
            >
              ← Voltar
            </button>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="grid lg:grid-cols-3 gap-8">
            {/* User Info */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">👤 Informações Pessoais</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-white/60">Nome</label>
                    <p className="text-lg text-white">{userProfile.user.name}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white/60">Email</label>
                    <p className="text-lg text-white">{userProfile.user.email}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white/60">Membro desde</label>
                    <p className="text-lg text-white">{new Date(userProfile.user.created_at).toLocaleDateString('pt-BR')}</p>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-white/60">Telefone</label>
                    <p className="text-lg text-white">{userProfile.user.phone || 'Não informado'}</p>
                  </div>
                </div>
              </div>

              {/* Blockchain Wallet */}
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">🔗 Carteira Blockchain</h3>
                
                <div className="bg-gradient-to-r from-blue-500/20 to-purple-600/20 rounded-lg p-4 mb-4 border border-blue-500/30">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm text-white/60">Saldo BNB</p>
                      <p className="text-2xl font-bold text-white">{userProfile.wallet.assets.bnb_balance} tBNB</p>
                    </div>
                    <div className="text-4xl">💰</div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-white/60 mb-2">Endereço da Carteira</label>
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-mono bg-black/20 p-3 rounded flex-1 text-white border border-white/10">
                        {userProfile.wallet.address}
                      </p>
                      <button
                        onClick={() => navigator.clipboard.writeText(userProfile.wallet.address)}
                        className="px-3 py-3 bg-blue-500 text-white rounded hover:bg-blue-600 text-sm"
                      >
                        📋
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-white/60 mb-2">Chave Privada</label>
                    <div className="flex items-center space-x-2">
                      <p className="text-sm font-mono bg-black/20 p-3 rounded flex-1 text-white border border-white/10">
                        {showPrivateKey ? userProfile.wallet.private_key : '••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••'}
                      </p>
                      <button
                        onClick={() => setShowPrivateKey(!showPrivateKey)}
                        className="px-3 py-3 bg-gray-500 text-white rounded hover:bg-gray-600 text-sm"
                      >
                        {showPrivateKey ? '🙈' : '👁️'}
                      </button>
                      {showPrivateKey && (
                        <button
                          onClick={() => navigator.clipboard.writeText(userProfile.wallet.private_key)}
                          className="px-3 py-3 bg-red-500 text-white rounded hover:bg-red-600 text-sm"
                        >
                          📋
                        </button>
                      )}
                    </div>
                    <p className="text-xs text-red-300 mt-1">
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
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">🎫 Meus Tokens</h3>
                {userProfile.wallet.assets.tokens && userProfile.wallet.assets.tokens.length > 0 ? (
                  <div className="grid gap-4">
                    {userProfile.wallet.assets.tokens.map((token, index) => (
                      <div key={index} className="bg-white/5 rounded-lg p-4 border border-white/10">
                        <div className="flex justify-between items-center mb-3">
                          <div>
                            <h4 className="font-bold text-white">{token.name}</h4>
                            <p className="text-sm text-white/60">{token.event_name}</p>
                            {token.address && (
                              <p className="text-xs text-white/40 font-mono">{token.address.substr(0, 12)}...</p>
                            )}
                          </div>
                          <div className="text-right">
                            <p className="text-2xl font-bold text-white">{token.balance}</p>
                            <p className="text-sm text-white/60">tokens</p>
                          </div>
                        </div>
                        
                        {/* Add to MetaMask button for profile tokens */}
                        {token.address && (
                          <button
                            onClick={() => addTokenToMetaMask(
                              token.address,
                              token.name?.toUpperCase().substr(0, 5) || 'TOKEN',
                              token.name,
                              18
                            )}
                            disabled={loading}
                            className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 text-sm disabled:opacity-50"
                          >
                            <span>🦊</span>
                            <span>Adicionar ao MetaMask</span>
                          </button>
                        )}
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-white/60 text-center py-8">Nenhum token encontrado</p>
                )}
              </div>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Events Summary */}
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-lg font-bold text-white mb-4">📊 Meus Eventos</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-white/70">Eventos criados:</span>
                    <span className="font-bold text-white">{userProfile.events.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-white/70">Eventos ativos:</span>
                    <span className="font-bold text-white">
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
              <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                <h3 className="text-lg font-bold text-white mb-4">💳 Transações Recentes</h3>
                {userProfile.recent_transactions && userProfile.recent_transactions.length > 0 ? (
                  <div className="space-y-3">
                    {userProfile.recent_transactions.slice(0, 5).map((tx, index) => (
                      <div key={index} className="border-b border-white/10 pb-2 last:border-b-0">
                        <div className="flex justify-between">
                          <span className="text-sm text-white">
                            {tx.type === 'purchase' ? '💰 Compra' : '📤 Transferência'}
                          </span>
                          <span className="text-sm font-bold text-white">{tx.amount}</span>
                        </div>
                        <p className="text-xs text-white/60">
                          {new Date(tx.timestamp).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-white/60 text-sm">Nenhuma transação</p>
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
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md w-full mx-4 border border-white/20">
            <h3 className="text-2xl font-bold text-white mb-6">✨ Criar Novo Evento</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Nome do Evento</label>
                <input
                  type="text"
                  required
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Festival de Verão 2024"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Data do Evento</label>
                <input
                  type="datetime-local"
                  required
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                  value={formData.date}
                  onChange={(e) => setFormData({...formData, date: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Local</label>
                <input
                  type="text"
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500"
                  placeholder="Ex: Parque da Cidade"
                  value={formData.location}
                  onChange={(e) => setFormData({...formData, location: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Descrição</label>
                <textarea
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500"
                  rows="3"
                  placeholder="Descreva seu evento..."
                  value={formData.description}
                  onChange={(e) => setFormData({...formData, description: e.target.value})}
                />
              </div>
              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateEvent(false)}
                  className="flex-1 px-4 py-2 bg-white/10 text-white border border-white/20 rounded-lg hover:bg-white/20"
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
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md w-full mx-4 border border-white/20">
            <h3 className="text-2xl font-bold text-white mb-6">🎫 Criar Token</h3>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Nome do Token</label>
                <input
                  type="text"
                  required
                  placeholder="Ex: CERVEJA, HOTDOG, ENTRADA"
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Preço (centavos)</label>
                <input
                  type="number"
                  required
                  placeholder="Ex: 500 (R$ 5,00)"
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500"
                  value={formData.price_cents}
                  onChange={(e) => setFormData({...formData, price_cents: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Quantidade Inicial</label>
                <input
                  type="number"
                  required
                  placeholder="Ex: 1000"
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-blue-500"
                  value={formData.initial_supply}
                  onChange={(e) => setFormData({...formData, initial_supply: e.target.value})}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">Modo de Venda</label>
                <select
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-blue-500"
                  value={formData.sale_mode}
                  onChange={(e) => setFormData({...formData, sale_mode: e.target.value})}
                >
                  <option value="both" className="bg-gray-800">Online + Offline</option>
                  <option value="online" className="bg-gray-800">Apenas Online (Crypto)</option>
                  <option value="offline" className="bg-gray-800">Apenas Offline (Caixa)</option>
                </select>
              </div>
              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateToken(false)}
                  className="flex-1 px-4 py-2 bg-white/10 text-white border border-white/20 rounded-lg hover:bg-white/20"
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
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
        <div className="bg-white/10 backdrop-blur-lg border-b border-white/20">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-white">🎪 Meus Eventos</h1>
            <div className="flex space-x-4">
              <button
                onClick={() => setCurrentView('profile')}
                className="px-4 py-2 text-white/80 hover:text-white transition-all"
              >
                Perfil
              </button>
              <button
                onClick={() => setCurrentView('home')}
                className="px-4 py-2 text-white/80 hover:text-white transition-all"
              >
                ← Home
              </button>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold text-white">Dashboard</h2>
            <button
              onClick={() => setShowCreateEvent(true)}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 font-medium shadow-lg"
            >
              ✨ Criar Evento
            </button>
          </div>

          <div className="grid gap-6">
            {Array.isArray(events) && events.length > 0 ? events.map((event) => (
              <div key={event.id} className="bg-white rounded-xl shadow-sm border p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-bold text-gray-800">{event.name || 'Evento sem nome'}</h3>
                    <p className="text-gray-600">
                      {event.date ? new Date(event.date).toLocaleDateString('pt-BR') : 'Data não informada'}
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
                  {event.tokens && Array.isArray(event.tokens) && event.tokens.length > 0 ? (
                    <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                      {event.tokens.map((token) => (
                        <div key={token.id} className="bg-gray-50 rounded-lg p-4">
                          <div className="font-medium">{token.name || 'Token'}</div>
                          <div className="text-sm text-gray-600">
                            R$ {((token.price_cents || 0) / 100).toFixed(2)}
                          </div>
                          <div className="text-sm text-gray-600">
                            Estoque: {(token.initial_supply || 0) - (token.total_sold || 0)}
                          </div>
                          <div className="text-xs mt-1 mb-2">
                            <span className={`px-2 py-1 rounded-full ${
                              token.sale_mode === 'online' ? 'bg-blue-100 text-blue-800' :
                              token.sale_mode === 'offline' ? 'bg-green-100 text-green-800' :
                              'bg-purple-100 text-purple-800'
                            }`}>
                              {token.sale_mode === 'online' ? 'Online' : 
                               token.sale_mode === 'offline' ? 'Offline' : 'Online + Offline'}
                            </span>
                          </div>
                          
                          {/* Contract Address Display */}
                          {token.contract_address && (
                            <div className="text-xs text-gray-500 mb-2">
                              <span className="font-mono">{token.contract_address.substr(0, 12)}...</span>
                              {token.deployment_status && (
                                <span className={`ml-2 px-1 py-0.5 rounded text-xs ${
                                  token.deployment_status === 'deployed' ? 'bg-green-100 text-green-700' :
                                  token.deployment_status === 'failed' ? 'bg-red-100 text-red-700' :
                                  'bg-yellow-100 text-yellow-700'
                                }`}>
                                  {token.deployment_status === 'deployed' ? '✅ Deployed' :
                                   token.deployment_status === 'failed' ? '❌ Failed' : 
                                   '⏳ Mock'}
                                </span>
                              )}
                            </div>
                          )}
                          
                          {/* MetaMask Button for Dashboard */}
                          <button
                            onClick={() => addTokenToMetaMask(
                              token.contract_address,
                              token.symbol || token.name?.toUpperCase().substr(0, 5) || 'TOKEN',
                              token.full_name || token.name,
                              token.decimals || 18
                            )}
                            disabled={!token.contract_address || token.contract_address.startsWith('0x000000') || loading || token.deployment_status !== 'deployed'}
                            className="w-full flex items-center justify-center space-x-1 px-2 py-1.5 bg-orange-600 text-white rounded hover:bg-orange-700 text-xs disabled:opacity-50 disabled:cursor-not-allowed"
                            title={token.deployment_status !== 'deployed' ? 'Token não disponível na blockchain' : 'Adicionar token ao MetaMask'}
                          >
                            <span>🦊</span>
                            <span>MetaMask</span>
                          </button>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 italic">Nenhum token criado ainda</p>
                  )}
                </div>
              </div>
            )) : (
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
        </div>

        {showCreateEvent && <CreateEventForm />}
        {showCreateToken && <CreateTokenForm />}
      </div>
    );
  };

  // Marketplace Component
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
          showErrorMessage('Você precisa estar logado para realizar transferências');
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
            showSuccessMessage('Tokens transferidos com sucesso!');
            setShowOfflineTransfer(false);
            setOfflineFormData({ user_email: '', token_address: '', amount: '', cashier_id: 'Transferência Livre' });
          } else {
            showErrorMessage('Erro: ' + data.detail);
          }
        } catch (error) {
          showErrorMessage('Erro na transferência: ' + error.message);
        }
        setLoading(false);
      };

      return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 max-w-md w-full mx-4 border border-white/20">
            <h3 className="text-2xl font-bold text-white mb-6">🎁 Transferência Livre de Tokens</h3>
            <p className="text-white/70 mb-6 text-sm">
              <strong>Modo Admin:</strong> Transfira qualquer quantidade de tokens para qualquer usuário instantaneamente.
            </p>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">📧 Email do Destinatário</label>
                <input
                  type="email"
                  required
                  placeholder="usuario@email.com"
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-green-500"
                  value={offlineFormData.user_email}
                  onChange={(e) => setOfflineFormData({...offlineFormData, user_email: e.target.value})}
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">🎫 Token</label>
                <select
                  required
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white focus:ring-2 focus:ring-green-500"
                  value={offlineFormData.token_address}
                  onChange={(e) => setOfflineFormData({...offlineFormData, token_address: e.target.value})}
                >
                  <option value="">Selecione um token</option>
                  {Array.isArray(publicEvents) && publicEvents.length > 0 ? 
                    publicEvents.map(event => 
                      event.tokens && Array.isArray(event.tokens) && event.tokens.length > 0 ? 
                        event.tokens.map(token => (
                          <option key={`${event.id}-${token.id}`} value={token.contract_address || token.id}>
                            {token.name} - {event.name} - R$ {(token.price_cents / 100).toFixed(2)}
                          </option>
                        )) : null
                    ) : (
                      <option disabled>Nenhum token disponível</option>
                    )
                  }
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">📊 Quantidade</label>
                <input
                  type="number"
                  required
                  min="1"
                  placeholder="Ex: 10"
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-green-500"
                  value={offlineFormData.amount}
                  onChange={(e) => setOfflineFormData({...offlineFormData, amount: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-white/80 mb-2">🏪 Origem/Motivo</label>
                <input
                  type="text"
                  placeholder="Ex: Gift, Promoção, Admin Transfer"
                  className="w-full p-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:ring-2 focus:ring-green-500"
                  value={offlineFormData.cashier_id}
                  onChange={(e) => setOfflineFormData({...offlineFormData, cashier_id: e.target.value})}
                />
              </div>

              <div className="bg-blue-500/20 border border-blue-500/30 rounded-lg p-4">
                <p className="text-sm text-blue-300">
                  <strong>🔓 Modo Apresentação:</strong> Esta transferência é livre e não requer validação de pagamento.
                </p>
              </div>

              <div className="flex gap-4 pt-4">
                <button
                  type="button"
                  onClick={() => setShowOfflineTransfer(false)}
                  className="flex-1 px-4 py-2 bg-white/10 text-white border border-white/20 rounded-lg hover:bg-white/20"
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
      <div className="min-h-screen bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
        <div className="bg-white/10 backdrop-blur-lg border-b border-white/20">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <h1 className="text-2xl font-bold text-white">🛍️ Marketplace de Tokens</h1>
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
                className="px-4 py-2 text-white/80 hover:text-white transition-all"
              >
                ← Voltar
              </button>
            </div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          {/* Info Cards */}
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            <div className="bg-gradient-to-r from-blue-500/20 to-purple-600/20 border border-blue-500/30 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-2">💳 Compra Online</h3>
              <p className="text-blue-200 mb-4">
                Participantes podem comprar tokens diretamente com criptomoedas
              </p>
              <div className="text-sm text-blue-300 space-y-1">
                <p>✅ Pagamento instantâneo</p>
                <p>✅ Tokens na carteira imediatamente</p>
                <p>✅ Sem intermediários</p>
              </div>
            </div>

            <div className="bg-gradient-to-r from-green-500/20 to-teal-600/20 border border-green-500/30 rounded-xl p-6">
              <h3 className="text-xl font-bold text-white mb-2">🎁 Transferência Livre</h3>
              <p className="text-green-200 mb-4">
                Durante a apresentação, qualquer usuário pode transferir tokens livremente
              </p>
              <div className="text-sm text-green-300 space-y-1">
                <p>✅ Transferência instantânea</p>
                <p>✅ Sem validação de pagamento</p>
                <p>✅ Modo admin ativo</p>
              </div>
            </div>
          </div>

          {/* Events Grid */}
          <div className="grid gap-6">
            {Array.isArray(publicEvents) && publicEvents.length > 0 ? (
              publicEvents.map((event) => (
                <div key={event.id} className="bg-white/10 backdrop-blur-lg rounded-xl p-6 border border-white/20">
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">{event.name || 'Evento sem nome'}</h3>
                      <p className="text-white/70 mb-2">
                        📅 {event.date ? new Date(event.date).toLocaleDateString('pt-BR') : 'Data não informada'}
                        {event.location && ` • 📍 ${event.location}`}
                      </p>
                      {event.description && (
                        <p className="text-white/60 mb-4">{event.description}</p>
                      )}
                    </div>
                    <div className="text-right">
                      <span className="px-3 py-1 bg-green-500/20 text-green-300 rounded-full text-sm border border-green-500/30">
                        🟢 Ativo
                      </span>
                    </div>
                  </div>
                  
                  {event.tokens && Array.isArray(event.tokens) && event.tokens.length > 0 ? (
                    <div>
                      <h4 className="font-medium text-white mb-3">🎫 Tokens Disponíveis:</h4>
                      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
                        {event.tokens.map((token) => (
                          <div key={token.id} className="bg-white/5 rounded-lg p-4 border border-white/10">
                            <div className="flex justify-between items-start mb-2">
                              <div className="font-medium text-lg text-white">{token.name || 'Token'}</div>
                              <div className="flex items-center space-x-2">
                                <div className="text-lg font-bold text-green-400">
                                  R$ {((token.price_cents || 0) / 100).toFixed(2)}
                                </div>
                                <a
                                  href={`https://testnet.bscscan.com/address/${token.contract_address || ''}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="text-blue-400 hover:text-blue-300 text-lg"
                                  title="Ver contrato no BSCScan"
                                >
                                  ℹ️
                                </a>
                              </div>
                            </div>
                            
                            <div className="text-sm text-white/70 mb-3">
                              📦 Disponível: {(token.initial_supply || 0) - (token.total_sold || 0)}
                            </div>
                            
                            <div className="mb-3">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                                token.sale_mode === 'online' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                                token.sale_mode === 'offline' ? 'bg-green-500/20 text-green-300 border border-green-500/30' :
                                'bg-purple-500/20 text-purple-300 border border-purple-500/30'
                              }`}>
                                {token.sale_mode === 'online' ? '💳 Apenas Online' : 
                                 token.sale_mode === 'offline' ? '🏪 Apenas Offline' : 
                                 '💳🏪 Online + Offline'}
                              </span>
                            </div>
                            
                            <div className="text-xs text-white/50 mb-3 font-mono">
                              {token.contract_address ? `${token.contract_address.substr(0, 12)}...` : 'N/A'}
                            </div>
                            
                            <div className="space-y-2">
                              <div className="flex gap-2">
                                {(token.sale_mode === 'online' || token.sale_mode === 'both') && user && (
                                  <button className="flex-1 px-3 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm">
                                    💳 Comprar
                                  </button>
                                )}
                                {user && (
                                  <button 
                                    onClick={() => {
                                      setOfflineFormData(prev => ({...prev, token_address: token.contract_address || token.id}));
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
                                    className="w-full px-3 py-2 bg-white/20 text-white rounded text-sm"
                                  >
                                    Fazer Login
                                  </button>
                                )}
                              </div>
                              
                              {/* Add to MetaMask Button - Always visible */}
                              <button
                                onClick={() => addTokenToMetaMask(
                                  token.contract_address,
                                  token.symbol || token.name?.toUpperCase().substr(0, 5) || 'TOKEN',
                                  token.full_name || token.name,
                                  token.decimals || 18
                                )}
                                disabled={!token.contract_address || token.contract_address.startsWith('0x000000') || loading}
                                className="w-full flex items-center justify-center space-x-2 px-3 py-2 bg-orange-600 text-white rounded hover:bg-orange-700 text-sm disabled:opacity-50 disabled:cursor-not-allowed"
                                title={!token.contract_address || token.contract_address.startsWith('0x000000') ? 'Token ainda não deployado na blockchain' : 'Adicionar token ao MetaMask'}
                              >
                                <span>🦊</span>
                                <span>Adicionar ao MetaMask</span>
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  ) : (
                    <p className="text-white/50 text-center py-8">📭 Nenhum token disponível para este evento</p>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-16">
                <div className="text-6xl mb-4">🎪</div>
                <h3 className="text-xl font-medium text-white/70 mb-2">
                  Nenhum evento disponível
                </h3>
                <p className="text-white/50">
                  Aguarde novos eventos serem criados
                </p>
              </div>
            )}
          </div>
        </div>

        {showOfflineTransfer && <OfflineTransferForm />}
      </div>
    );
  };

  // Main App Router
  const renderCurrentView = () => {
    switch (currentView) {
      case 'profile':
        return user ? <ProfilePage /> : <HomePage />;
      case 'dashboard':
        return user ? <DashboardPage /> : <HomePage />;
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