import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('home');
  const [events, setEvents] = useState([]);
  const [users, setUsers] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [walletConnected, setWalletConnected] = useState(false);
  const [walletAddress, setWalletAddress] = useState(null);
  const [networkAdded, setNetworkAdded] = useState(false);

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

  // Fetch events on load
  useEffect(() => {
    fetchEvents();
    checkAPIHealth();
  }, []);

  const checkAPIHealth = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/health`);
      const data = await response.json();
      console.log('API Health:', data);
    } catch (error) {
      console.error('API Health Check Failed:', error);
    }
  };

  const fetchEvents = async () => {
    try {
      const response = await fetch(`${API_BASE}/api/events`);
      const data = await response.json();
      setEvents(data.events || []);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    }
  };

  const createEvent = async (eventData) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/organizers/events`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(eventData),
      });
      const data = await response.json();
      if (response.ok) {
        alert('Evento criado com sucesso!');
        fetchEvents();
        setCurrentView('organizer');
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
        },
        body: JSON.stringify(tokenData),
      });
      const data = await response.json();
      if (response.ok) {
        alert('Token criado com sucesso!');
        fetchEvents();
      } else {
        alert('Erro ao criar token: ' + data.detail);
      }
    } catch (error) {
      alert('Erro ao criar token: ' + error.message);
    }
    setLoading(false);
  };

  const registerUser = async (userData) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/users/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });
      const data = await response.json();
      if (response.ok) {
        alert('Usuário registrado com sucesso!');
        setSelectedUser(data);
        setCurrentView('user');
      } else {
        alert('Erro ao registrar usuário: ' + data.detail);
      }
    } catch (error) {
      alert('Erro ao registrar usuário: ' + error.message);
    }
    setLoading(false);
  };

  const purchaseTokens = async (userId, tokenAddress, amount) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/users/${userId}/purchase`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token_address: tokenAddress,
          amount: parseInt(amount)
        }),
      });
      const data = await response.json();
      if (response.ok) {
        alert('Tokens comprados com sucesso!');
      } else {
        alert('Erro ao comprar tokens: ' + data.detail);
      }
    } catch (error) {
      alert('Erro ao comprar tokens: ' + error.message);
    }
    setLoading(false);
  };

  const transferTokens = async (userId, toAddress, tokenAddress, amount) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/api/users/${userId}/transfer`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          to_address: toAddress,
          token_address: tokenAddress,
          amount: parseInt(amount)
        }),
      });
      const data = await response.json();
      if (response.ok) {
        alert('Pagamento realizado com sucesso!');
      } else {
        alert('Erro ao realizar pagamento: ' + data.detail);
      }
    } catch (error) {
      alert('Erro ao realizar pagamento: ' + error.message);
    }
    setLoading(false);
  };

  // Home Page Component
  const HomePage = () => (
    <div className="min-h-screen bg-gradient-to-br from-blue-900 via-purple-900 to-indigo-900">
      <div className="container mx-auto px-4 py-16">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold text-white mb-6">
            Ban<span className="text-yellow-400">Ka</span>
          </h1>
          <p className="text-2xl text-blue-200 mb-8">
            O caixa do seu evento na era digital
          </p>
          <p className="text-lg text-blue-300 max-w-2xl mx-auto">
            Revolucione a experiência de pagamento em eventos com tokens digitais seguros na blockchain.
            Sem filas, sem dinheiro físico, apenas tecnologia.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8 max-w-4xl mx-auto">
          <div 
            onClick={() => setCurrentView('organizer')}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105"
          >
            <div className="text-6xl mb-4">🎪</div>
            <h3 className="text-2xl font-bold text-white mb-4">Organizador</h3>
            <p className="text-blue-200">
              Crie eventos, gerencie tokens e monitore vendas em tempo real
            </p>
          </div>

          <div 
            onClick={() => setCurrentView('participant')}
            className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 text-center cursor-pointer hover:bg-white/20 transition-all duration-300 hover:scale-105"
          >
            <div className="text-6xl mb-4">🎫</div>
            <h3 className="text-2xl font-bold text-white mb-4">Participante</h3>
            <p className="text-blue-200">
              Compre tokens, pague vendedores e gerencie sua carteira digital
            </p>
          </div>
        </div>

        <div className="mt-16 text-center">
          <div className="grid md:grid-cols-3 gap-8 max-w-4xl mx-auto">
            <div className="text-center">
              <div className="text-4xl mb-4">⚡</div>
              <h4 className="text-xl font-bold text-white mb-2">Instantâneo</h4>
              <p className="text-blue-300">Pagamentos em segundos via QR Code</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">🔒</div>
              <h4 className="text-xl font-bold text-white mb-2">Seguro</h4>
              <p className="text-blue-300">Blockchain BNB Chain para máxima segurança</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">📱</div>
              <h4 className="text-xl font-bold text-white mb-2">Simples</h4>
              <p className="text-blue-300">Interface intuitiva para todos</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  // Organizer Dashboard
  const OrganizerDashboard = () => {
    const [showCreateEvent, setShowCreateEvent] = useState(false);
    const [showCreateToken, setShowCreateToken] = useState(false);

    const CreateEventForm = () => {
      const [formData, setFormData] = useState({
        name: '',
        date: '',
        description: ''
      });

      const handleSubmit = (e) => {
        e.preventDefault();
        createEvent({
          ...formData,
          date: new Date(formData.date).toISOString()
        });
        setShowCreateEvent(false);
        setFormData({ name: '', date: '', description: '' });
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
        initial_supply: ''
      });

      const handleSubmit = (e) => {
        e.preventDefault();
        createToken(selectedEvent.id, {
          ...formData,
          price_cents: parseInt(formData.price_cents),
          initial_supply: parseInt(formData.initial_supply)
        });
        setShowCreateToken(false);
        setFormData({ name: '', price_cents: '', initial_supply: '' });
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
              <div className="mb-6">
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
            <h1 className="text-2xl font-bold text-gray-800">Painel do Organizador</h1>
            <button
              onClick={() => setCurrentView('home')}
              className="px-4 py-2 text-blue-600 hover:text-blue-800"
            >
              ← Voltar
            </button>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-3xl font-bold">Meus Eventos</h2>
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
                          <div className="font-medium">{token.name}</div>
                          <div className="text-sm text-gray-600">
                            R$ {(token.price_cents / 100).toFixed(2)}
                          </div>
                          <div className="text-sm text-gray-600">
                            Estoque: {token.initial_supply - token.total_sold}
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

  // Participant App
  const ParticipantApp = () => {
    const [showRegister, setShowRegister] = useState(!selectedUser);
    const [showPurchase, setShowPurchase] = useState(false);
    const [showPayment, setShowPayment] = useState(false);

    const RegisterForm = () => {
      const [formData, setFormData] = useState({
        name: '',
        email: '',
        phone: ''
      });

      const handleSubmit = (e) => {
        e.preventDefault();
        registerUser(formData);
        setShowRegister(false);
      };

      return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <h3 className="text-2xl font-bold mb-6">Registrar no BanKa</h3>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Nome Completo</label>
                <input
                  type="text"
                  required
                  className="w-full p-3 border rounded-lg"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                />
              </div>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Email</label>
                <input
                  type="email"
                  required
                  className="w-full p-3 border rounded-lg"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                />
              </div>
              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Telefone (opcional)</label>
                <input
                  type="tel"
                  className="w-full p-3 border rounded-lg"
                  value={formData.phone}
                  onChange={(e) => setFormData({...formData, phone: e.target.value})}
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="w-full px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium"
              >
                {loading ? 'Registrando...' : 'Criar Carteira'}
              </button>
            </form>
          </div>
        </div>
      );
    };

    const PurchaseForm = () => {
      const [selectedEventId, setSelectedEventId] = useState('');
      const [selectedTokenId, setSelectedTokenId] = useState('');
      const [amount, setAmount] = useState('');

      const selectedEventData = events.find(e => e.id === selectedEventId);
      const selectedToken = selectedEventData?.tokens?.find(t => t.id === selectedTokenId);

      const handleSubmit = (e) => {
        e.preventDefault();
        if (selectedToken) {
          purchaseTokens(selectedUser.id, selectedToken.contract_address, amount);
          setShowPurchase(false);
          setSelectedEventId('');
          setSelectedTokenId('');
          setAmount('');
        }
      };

      return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <h3 className="text-2xl font-bold mb-6">Comprar Tokens</h3>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Evento</label>
                <select
                  required
                  className="w-full p-3 border rounded-lg"
                  value={selectedEventId}
                  onChange={(e) => {
                    setSelectedEventId(e.target.value);
                    setSelectedTokenId('');
                  }}
                >
                  <option value="">Selecione um evento</option>
                  {events.map(event => (
                    <option key={event.id} value={event.id}>{event.name}</option>
                  ))}
                </select>
              </div>
              
              {selectedEventData && (
                <div className="mb-4">
                  <label className="block text-sm font-medium mb-2">Token</label>
                  <select
                    required
                    className="w-full p-3 border rounded-lg"
                    value={selectedTokenId}
                    onChange={(e) => setSelectedTokenId(e.target.value)}
                  >
                    <option value="">Selecione um token</option>
                    {selectedEventData.tokens?.map(token => (
                      <option key={token.id} value={token.id}>
                        {token.name} - R$ {(token.price_cents / 100).toFixed(2)}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Quantidade</label>
                <input
                  type="number"
                  required
                  min="1"
                  className="w-full p-3 border rounded-lg"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                />
                {selectedToken && amount && (
                  <p className="text-sm text-gray-600 mt-2">
                    Total: R$ {((selectedToken.price_cents * parseInt(amount || 0)) / 100).toFixed(2)}
                  </p>
                )}
              </div>

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowPurchase(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading || !selectedToken}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Comprando...' : 'Comprar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      );
    };

    const PaymentForm = () => {
      const [vendorAddress, setVendorAddress] = useState('');
      const [selectedTokenAddress, setSelectedTokenAddress] = useState('');
      const [amount, setAmount] = useState('');

      const handleSubmit = (e) => {
        e.preventDefault();
        transferTokens(selectedUser.id, vendorAddress, selectedTokenAddress, amount);
        setShowPayment(false);
        setVendorAddress('');
        setSelectedTokenAddress('');
        setAmount('');
      };

      return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-2xl p-8 max-w-md w-full mx-4">
            <h3 className="text-2xl font-bold mb-6">Pagar Vendedor</h3>
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Endereço do Vendedor</label>
                <input
                  type="text"
                  required
                  placeholder="Escaneie QR Code ou digite"
                  className="w-full p-3 border rounded-lg"
                  value={vendorAddress}
                  onChange={(e) => setVendorAddress(e.target.value)}
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium mb-2">Token</label>
                <select
                  required
                  className="w-full p-3 border rounded-lg"
                  value={selectedTokenAddress}
                  onChange={(e) => setSelectedTokenAddress(e.target.value)}
                >
                  <option value="">Selecione um token</option>
                  {events.map(event => 
                    event.tokens?.map(token => (
                      <option key={token.contract_address} value={token.contract_address}>
                        {token.name} ({event.name})
                      </option>
                    ))
                  )}
                </select>
              </div>

              <div className="mb-6">
                <label className="block text-sm font-medium mb-2">Quantidade</label>
                <input
                  type="number"
                  required
                  min="1"
                  className="w-full p-3 border rounded-lg"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                />
              </div>

              <div className="flex gap-4">
                <button
                  type="button"
                  onClick={() => setShowPayment(false)}
                  className="flex-1 px-4 py-2 border rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                >
                  {loading ? 'Pagando...' : 'Pagar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      );
    };

    if (!selectedUser) {
      return (
        <div className="min-h-screen bg-gradient-to-br from-green-900 via-blue-900 to-purple-900 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-4xl font-bold text-white mb-8">BanKa Participante</h1>
            <p className="text-xl text-green-200 mb-8">
              Registre-se para começar a usar tokens digitais
            </p>
            {showRegister && <RegisterForm />}
          </div>
        </div>
      );
    }

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="bg-white shadow-sm">
          <div className="container mx-auto px-4 py-4 flex justify-between items-center">
            <div>
              <h1 className="text-xl font-bold text-gray-800">Olá, {selectedUser.name}</h1>
              <p className="text-sm text-gray-600">
                Carteira: {selectedUser.wallet_address?.substr(0, 10)}...
              </p>
            </div>
            <button
              onClick={() => setCurrentView('home')}
              className="px-4 py-2 text-blue-600 hover:text-blue-800"
            >
              ← Voltar
            </button>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="grid sm:grid-cols-2 gap-6 mb-8">
            <button
              onClick={() => setShowPurchase(true)}
              className="bg-blue-600 text-white rounded-xl p-6 text-center hover:bg-blue-700 transition-colors"
            >
              <div className="text-4xl mb-2">💰</div>
              <h3 className="text-xl font-bold mb-2">Comprar Tokens</h3>
              <p className="text-blue-100">Carregue sua carteira com tokens de eventos</p>
            </button>

            <button
              onClick={() => setShowPayment(true)}
              className="bg-green-600 text-white rounded-xl p-6 text-center hover:bg-green-700 transition-colors"
            >
              <div className="text-4xl mb-2">📱</div>
              <h3 className="text-xl font-bold mb-2">Pagar Vendedor</h3>
              <p className="text-green-100">Escaneie QR code e pague instantaneamente</p>
            </button>
          </div>

          <div className="bg-white rounded-xl shadow-sm border p-6">
            <h3 className="text-xl font-bold mb-4">Eventos Disponíveis</h3>
            {events.length > 0 ? (
              <div className="grid gap-4">
                {events.map(event => (
                  <div key={event.id} className="border rounded-lg p-4">
                    <h4 className="font-bold">{event.name}</h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {new Date(event.date).toLocaleDateString('pt-BR')}
                    </p>
                    {event.tokens && event.tokens.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {event.tokens.map(token => (
                          <span
                            key={token.id}
                            className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm"
                          >
                            {token.name} - R$ {(token.price_cents / 100).toFixed(2)}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-gray-500 text-center py-8">Nenhum evento disponível</p>
            )}
          </div>
        </div>

        {showPurchase && <PurchaseForm />}
        {showPayment && <PaymentForm />}
      </div>
    );
  };

  // Main App Router
  const renderCurrentView = () => {
    switch (currentView) {
      case 'organizer':
        return <OrganizerDashboard />;
      case 'participant':
        return <ParticipantApp />;
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