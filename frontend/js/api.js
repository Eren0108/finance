/**
 * Centralized API Client and Utilities for Personal Finance Tracker
 */

const API_BASE = '/api';

// Currency Formatter (INR)
const inrFormatter = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 2,
  minimumFractionDigits: 2
});

export function formatINR(amount) {
  const num = Number(amount) || 0;
  return inrFormatter.format(num);
}

// Date Formatter
export function formatDate(dateStr) {
  if (!dateStr) return '';
  const parts = dateStr.split('-');
  if (parts.length === 3) {
    const d = new Date(parts[0], parts[1] - 1, parts[2]);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
  }
  return dateStr;
}

// Generic Request Handler
async function request(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  const config = {
    headers: {
      'Accept': 'application/json',
      ...(!options.isFormData && { 'Content-Type': 'application/json' }),
      ...(options.headers || {})
    },
    ...options
  };

  if (options.body && !options.isFormData && typeof options.body === 'object') {
    config.body = JSON.stringify(options.body);
  }

  try {
    const res = await fetch(url, config);
    const result = await res.json();
    if (!res.ok || !result.success) {
      throw new Error(result.error || `Request failed with status ${res.status}`);
    }
    return result.data;
  } catch (err) {
    console.error(`API Error [${endpoint}]:`, err);
    throw err;
  }
}

// API Methods
export const api = {
  // Health
  getHealth: () => request('/health'),

  // Categories
  getCategories: (type) => request(`/categories${type ? `?type=${type}` : ''}`),
  addCategory: (data) => request('/categories', { method: 'POST', body: data }),

  // Transactions
  getTransactions: (params = {}) => {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([k, v]) => {
      if (v !== undefined && v !== null && v !== '') query.append(k, v);
    });
    return request(`/transactions?${query.toString()}`);
  },
  addTransaction: (data) => request('/transactions', { method: 'POST', body: data }),
  updateTransaction: (id, data) => request(`/transactions/${id}`, { method: 'PUT', body: data }),
  deleteTransaction: (id) => request(`/transactions/${id}`, { method: 'DELETE' }),

  // Budgets
  getBudgets: (month) => request(`/budgets${month ? `?month=${month}` : ''}`),
  setBudget: (data) => request('/budgets', { method: 'POST', body: data }),

  // Statements
  uploadStatement: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/statements/upload', {
      method: 'POST',
      body: formData,
      isFormData: true
    });
  },
  confirmStatement: (data) => request('/statements/confirm', { method: 'POST', body: data }),

  // Reports
  getSummary: (month) => request(`/reports/summary${month ? `?month=${month}` : ''}`),
  getTrend: (months = 6, endMonth = null) => {
    const query = new URLSearchParams({ months });
    if (endMonth) query.append('end_month', endMonth);
    return request(`/reports/trend?${query.toString()}`);
  },
  getExportUrl: (month) => `${API_BASE}/reports/export${month ? `?month=${month}` : ''}`
};

// Toast Notifications
export function showToast(message, type = 'success') {
  let container = document.getElementById('toast-container');
  if (!container) {
    container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
  }

  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;

  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'fadeOut 0.3s ease-out forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

// Modal Handlers
export function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
}

export function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (modal) {
    modal.classList.remove('active');
    document.body.style.overflow = '';
  }
}

// Global Month Picker Initialization
export function initMonthPicker(selectId, onMonthChange) {
  const select = document.getElementById(selectId);
  if (!select) return;

  const now = new Date();
  select.innerHTML = '';

  // Generate last 12 months
  for (let i = 0; i < 12; i++) {
    const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
    const val = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`;
    const label = d.toLocaleDateString('en-IN', { month: 'short', year: 'numeric' });
    
    const opt = document.createElement('option');
    opt.value = val;
    opt.textContent = label;
    select.appendChild(opt);
  }

  // Load saved month from localStorage or default to current
  const saved = localStorage.getItem('finance_selected_month');
  if (saved && [...select.options].some(o => o.value === saved)) {
    select.value = saved;
  } else {
    select.selectedIndex = 0;
  }

  select.addEventListener('change', () => {
    localStorage.setItem('finance_selected_month', select.value);
    if (typeof onMonthChange === 'function') {
      onMonthChange(select.value);
    }
  });

  return select.value;
}

// Setup common shell interactions
export function setupShell() {
  const mobileBtn = document.getElementById('mobileMenuBtn');
  const sidebar = document.querySelector('.sidebar');
  if (mobileBtn && sidebar) {
    mobileBtn.addEventListener('click', () => {
      sidebar.classList.toggle('mobile-open');
    });
  }

  // Close modals on escape key or backdrop click
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      document.querySelectorAll('.modal-backdrop.active').forEach(m => m.classList.remove('active'));
      document.body.style.overflow = '';
    }
  });

  document.querySelectorAll('.modal-backdrop').forEach(modal => {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  });
}
