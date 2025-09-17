// Global variables
let currentUser = null;
let authToken = null;

// API configuration
const API_BASE = '/api';

// Initialize app
document.addEventListener('DOMContentLoaded', function() {
  checkAuth();
});

// Authentication functions
function checkAuth() {
  const token = localStorage.getItem('authToken');
  if (token) {
    authToken = token;
    axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    loadUserData();
  } else {
    showLoginScreen();
  }
}

function showLoginScreen() {
  document.getElementById('loginScreen').style.display = 'flex';
  document.getElementById('mainApp').style.display = 'none';
}

function showMainApp() {
  document.getElementById('loginScreen').style.display = 'none';
  document.getElementById('mainApp').style.display = 'block';
  loadDashboard();
}

async function loadUserData() {
  try {
    const response = await axios.get(`${API_BASE}/auth/me`);
    currentUser = response.data;
    document.getElementById('currentUserName').textContent = currentUser.name;
    showMainApp();
  } catch (error) {
    console.error('Failed to load user data:', error);
    showLoginScreen();
  }
}

// Login form handler
document.getElementById('loginForm').addEventListener('submit', async function(e) {
  e.preventDefault();
  
  const username = document.getElementById('loginUsername').value;
  const password = document.getElementById('loginPassword').value;
  
  try {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await axios.post(`${API_BASE}/auth/login`, formData);
    const { access_token } = response.data;
    
    localStorage.setItem('authToken', access_token);
    authToken = access_token;
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
    
    await loadUserData();
    
  } catch (error) {
    alert('Login failed: ' + (error.response?.data?.detail || 'Unknown error'));
  }
});

function logout() {
  localStorage.removeItem('authToken');
  authToken = null;
  currentUser = null;
  delete axios.defaults.headers.common['Authorization'];
  showLoginScreen();
}

// Navigation functions
function toggleSidebar(force) {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.querySelector('.sidebar-overlay');
  const willShow = typeof force === 'boolean' ? force : !sidebar.classList.contains('active');
  sidebar.classList.toggle('active', willShow);
  overlay.classList.toggle('active', willShow);
}

function changeTab(tabName, element) {
  document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
  if (element) element.classList.add('active');
  
  switch (tabName) {
    case 'dashboard':
      loadDashboard();
      break;
    case 'numbers':
      loadNumbers();
      break;
    case 'messages':
      loadMessages();
      break;
    case 'campaigns':
      loadCampaigns();
      break;
    case 'groups':
      loadGroups();
      break;
    case 'finances':
      loadFinances();
      break;
    default:
      loadPlaceholder(tabName);
  }
  
  if (window.innerWidth <= 768) toggleSidebar(false);
}

// Dashboard functions
async function loadDashboard() {
  const container = document.getElementById('mainContainer');
  
  try {
    const response = await axios.get(`${API_BASE}/dashboard/stats`);
    const stats = response.data;
    
    container.innerHTML = `
      <div class="header">
        <h1><i class="fas fa-chart-pie"></i> Dashboard</h1>
      </div>
      
      <div class="dashboard-metrics">
        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-title">Instâncias WhatsApp</div>
            <div class="metric-icon"><i class="fas fa-phone"></i></div>
          </div>
          <div class="metric-value">${stats.total_instances}</div>
          <div class="metric-subtitle">${stats.active_instances} ativas</div>
        </div>
        
        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-title">Conversas</div>
            <div class="metric-icon"><i class="fas fa-comments"></i></div>
          </div>
          <div class="metric-value">${stats.total_conversations}</div>
          <div class="metric-subtitle">${stats.unread_messages} não lidas</div>
        </div>
        
        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-title">Campanhas</div>
            <div class="metric-icon"><i class="fas fa-bullhorn"></i></div>
          </div>
          <div class="metric-value">${stats.total_campaigns}</div>
          <div class="metric-subtitle">${stats.active_campaigns} ativas</div>
        </div>
        
        <div class="metric-card">
          <div class="metric-header">
            <div class="metric-title">Status</div>
            <div class="metric-icon"><i class="fas fa-signal"></i></div>
          </div>
          <div class="metric-value">OK</div>
          <div class="metric-subtitle">sistema online</div>
        </div>
      </div>
    `;
    
    // Update unread badge
    const badge = document.getElementById('unreadBadge');
    if (stats.unread_messages > 0) {
      badge.textContent = stats.unread_messages;
      badge.style.display = 'inline';
    } else {
      badge.style.display = 'none';
    }
    
  } catch (error) {
    container.innerHTML = '<div class="header"><h1>Erro ao carregar dashboard</h1></div>';
  }
}

// WhatsApp Numbers functions
async function loadNumbers() {
  const container = document.getElementById('mainContainer');
  
  try {
    const response = await axios.get(`${API_BASE}/instances`);
    const instances = response.data;
    
    let content = `
      <div class="header">
        <h1><i class="fas fa-phone"></i> Números Conectados</h1>
        <button class="btn-primary" onclick="createInstanceModal()">
          <i class="fas fa-plus"></i> Conectar Número
        </button>
      </div>
      
      <div class="content-grid">
    `;
    
    if (instances.length === 0) {
      content += `
        <div class="content-card">
          <div class="card-header">
            <h3 class="card-title">Nenhum número conectado</h3>
          </div>
          <p class="card-subtitle">Clique em "Conectar Número" para adicionar sua primeira instância WhatsApp.</p>
        </div>
      `;
    } else {
      instances.forEach(instance => {
        const statusClass = instance.status === 'active' ? 'status-active' : 
                          instance.status === 'pending' ? 'status-pending' : 'status-offline';
        const statusText = instance.status === 'active' ? 'Online' : 
                         instance.status === 'pending' ? 'Conectando' : 'Offline';
        
        content += `
          <div class="content-card">
            <div class="card-status ${statusClass}">${statusText}</div>
            <div class="card-header">
              <div>
                <h3 class="card-title">${instance.name}</h3>
                <p class="card-subtitle">${instance.phone || 'Aguardando conexão'}</p>
              </div>
            </div>
            
            <div class="card-actions">
              <button class="btn-action btn-edit" onclick="editInstance('${instance.id}')">
                <i class="fas fa-cog"></i> Configurar
              </button>
              ${instance.status === 'pending' ? 
                `<button class="btn-action btn-connect" onclick="showQRCode('${instance.id}')">
                  <i class="fas fa-qrcode"></i> QR Code
                </button>` : 
                `<button class="btn-action btn-connect" onclick="syncInstance('${instance.id}')">
                  <i class="fas fa-sync"></i> Sincronizar
                </button>`
              }
              <button class="btn-action btn-delete" onclick="deleteInstance('${instance.id}')">
                <i class="fas fa-trash"></i> Remover
              </button>
            </div>
          </div>
        `;
      });
    }
    
    content += '</div>';
    container.innerHTML = content;
    
  } catch (error) {
    container.innerHTML = '<div class="header"><h1>Erro ao carregar números</h1></div>';
  }
}

// Modal and form functions
function createModal(title, content, buttons = []) {
  const modal = document.createElement('div');
  modal.className = 'modal-overlay';
  modal.innerHTML = `
    <div class="modal-box">
      <div class="modal-header">
        <div class="modal-title">${title}</div>
        <button class="modal-close" onclick="closeModal(this)">&times;</button>
      </div>
      <div class="modal-body">${content}</div>
      <div class="modal-footer">
        ${buttons.map(btn => `<button class="btn-${btn.type || 'ghost'}" onclick="${btn.action}">${btn.text}</button>`).join('')}
      </div>
    </div>
  `;
  
  document.body.appendChild(modal);
  return modal;
}

function closeModal(element) {
  const modal = element.closest('.modal-overlay');
  if (modal) {
    document.body.removeChild(modal);
  }
}

async function createInstanceModal() {
  const content = `
    <form id="instanceForm" class="modal-form">
      <div class="form-row">
        <label>Nome da Instância</label>
        <input type="text" name="name" required placeholder="Ex: Comercial 01">
      </div>
      <div class="form-row">
        <label>Telefone (opcional)</label>
        <input type="text" name="phone" placeholder="+55 31 99999-0000">
      </div>
    </form>
  `;
  
  createModal('Conectar Número WhatsApp', content, [
    { text: 'Cancelar', action: 'closeModal(this)' },
    { text: 'Conectar', type: 'primary', action: 'submitInstanceForm()' }
  ]);
}

async function submitInstanceForm() {
  const form = document.getElementById('instanceForm');
  const formData = new FormData(form);
  
  try {
    const data = {
      name: formData.get('name'),
      phone: formData.get('phone') || null
    };
    
    await axios.post(`${API_BASE}/instances`, data);
    closeModal(document.querySelector('.modal-overlay'));
    loadNumbers();
    
  } catch (error) {
    alert('Erro ao criar instância: ' + (error.response?.data?.detail || 'Erro desconhecido'));
  }
}

async function showQRCode(instanceId) {
  try {
    const response = await axios.get(`${API_BASE}/instances/${instanceId}/qr-code`);
    const { qr_code } = response.data;
    
    const content = `
      <div style="text-align: center;">
        <p style="margin-bottom: 20px;">Escaneie este QR Code com seu WhatsApp:</p>
        <div style="background: white; padding: 20px; border-radius: 10px; display: inline-block;">
          <img src="${qr_code}" alt="QR Code" style="max-width: 300px;">
        </div>
        <p style="margin-top: 20px; font-size: 12px; color: #666;">
          Abra o WhatsApp > Menu > Dispositivos conectados > Conectar dispositivo
        </p>
      </div>
    `;
    
    createModal('QR Code para Conexão', content, [
      { text: 'Fechar', action: 'closeModal(this)' }
    ]);
    
  } catch (error) {
    alert('Erro ao obter QR Code: ' + (error.response?.data?.detail || 'Erro desconhecido'));
  }
}

async function deleteInstance(instanceId) {
  if (confirm('Tem certeza que deseja remover esta instância?')) {
    try {
      await axios.delete(`${API_BASE}/instances/${instanceId}`);
      loadNumbers();
    } catch (error) {
      alert('Erro ao remover instância: ' + (error.response?.data?.detail || 'Erro desconhecido'));
    }
  }
}

async function syncInstance(instanceId) {
  try {
    await axios.post(`${API_BASE}/instances/${instanceId}/sync`);
    loadNumbers();
  } catch (error) {
    alert('Erro ao sincronizar: ' + (error.response?.data?.detail || 'Erro desconhecido'));
  }
}

function editInstance(instanceId) {
  alert('Funcionalidade de edição será implementada em breve!');
}

// Placeholder functions for other tabs
function loadPlaceholder(tabName) {
  const container = document.getElementById('mainContainer');
  const titles = {
    messages: 'Central de Mensagens',
    campaigns: 'Campanhas',
    groups: 'Grupos',
    finances: 'Finanças'
  };
  
  container.innerHTML = `
    <div class="header">
      <h1><i class="fas fa-wrench"></i> ${titles[tabName] || 'Em Desenvolvimento'}</h1>
    </div>
    <div style="text-align:center;padding:60px 20px;background:var(--card-bg);border-radius:18px;box-shadow:var(--shadow-lg);">
      <i class="fas fa-code" style="font-size:64px;color:#9ca3af;margin-bottom:20px;"></i>
      <h2 style="margin:0 0 10px 0;color:#4b5563;">Em construção</h2>
      <p style="margin:0;color:#6b7280;">Esta funcionalidade será implementada em breve.</p>
    </div>
  `;
}

function loadMessages() { loadPlaceholder('messages'); }
function loadCampaigns() { loadPlaceholder('campaigns'); }
function loadGroups() { loadPlaceholder('groups'); }
function loadFinances() { loadPlaceholder('finances'); }