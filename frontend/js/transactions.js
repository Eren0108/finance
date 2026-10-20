import { api, formatINR, formatDate, showToast, openModal, closeModal, setupShell } from './api.js';

let categories = [];
let currentPage = 1;
const pageLimit = 20;
let deleteTargetId = null;
let currentTransactions = [];

document.addEventListener('DOMContentLoaded', async () => {
  setupShell();

  await loadCategories();
  setupEventListeners();
  loadTransactions();
});

async function loadCategories() {
  try {
    categories = await api.getCategories();
    populateCategoryDropdowns();
  } catch (err) {
    showToast('Failed to load categories: ' + err.message, 'error');
  }
}

function populateCategoryDropdowns() {
  const filterCat = document.getElementById('filterCategory');
  const formCat = document.getElementById('txCategory');
  const typeSelect = document.getElementById('txType');

  if (filterCat) {
    filterCat.innerHTML = '<option value="">All Categories</option>';
    categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.name;
      filterCat.appendChild(opt);
    });
  }

  if (formCat && typeSelect) {
    const currentType = typeSelect.value;
    formCat.innerHTML = '';
    const filtered = categories.filter(c => c.type === currentType);
    filtered.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c.id;
      opt.textContent = c.name;
      formCat.appendChild(opt);
    });
  }
}

async function loadTransactions() {
  const tbody = document.getElementById('transactionsTableBody');
  tbody.innerHTML = `
    <tr>
      <td colspan="7" style="text-align: center; padding: 40px;">
        <span class="spinner"></span>
        <p style="margin-top: 8px; color: var(--text-muted); font-size: 0.85rem;">Loading transactions...</p>
      </td>
    </tr>
  `;

  const params = {
    page: currentPage,
    limit: pageLimit,
    search: document.getElementById('filterSearch').value.trim(),
    categoryId: document.getElementById('filterCategory').value,
    type: document.getElementById('filterType').value,
    startDate: document.getElementById('filterStartDate').value,
    endDate: document.getElementById('filterEndDate').value
  };

  try {
    const data = await api.getTransactions(params);
    currentTransactions = data.items;
    renderTransactionsTable(data.items);
    renderPagination(data.pagination);
  } catch (err) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--expense); padding: 30px;">
          Failed to load transactions: ${err.message}
        </td>
      </tr>
    `;
    showToast('Failed to load transactions', 'error');
  }
}

function renderTransactionsTable(items) {
  const tbody = document.getElementById('transactionsTableBody');

  if (!items || items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7">
          <div class="empty-state">
            <div class="empty-state-icon">
              <svg fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
            </div>
            <h4 class="empty-state-title">No transactions found</h4>
            <p class="empty-state-desc">Try clearing your filters or add a new transaction.</p>
            <button id="emptyStateAddBtn" class="btn btn-primary btn-sm">Add Transaction</button>
          </div>
        </td>
      </tr>
    `;
    const emptyBtn = document.getElementById('emptyStateAddBtn');
    if (emptyBtn) emptyBtn.addEventListener('click', openAddModal);
    return;
  }

  tbody.innerHTML = items.map(tx => {
    const isIncome = tx.type === 'income';
    const sign = isIncome ? '+' : '-';
    const amountColor = isIncome ? 'color: var(--income); font-weight: 700;' : 'color: var(--expense); font-weight: 700;';

    return `
      <tr>
        <td style="white-space: nowrap; color: var(--text-muted); font-size: 0.825rem;">
          ${formatDate(tx.date)}
        </td>
        <td>
          <span style="font-weight: 600;">${tx.description}</span>
        </td>
        <td>
          <span class="badge badge-category">
            <span class="cat-dot" style="background-color: ${tx.category_color};"></span>
            ${tx.category_name}
          </span>
        </td>
        <td>
          <span class="badge ${isIncome ? 'badge-income' : 'badge-expense'}">
            ${tx.type}
          </span>
        </td>
        <td style="text-align: right; ${amountColor}" class="tabular-nums">
          ${sign}${formatINR(tx.amount)}
        </td>
        <td style="text-align: center;">
          <span style="font-size: 0.775rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-muted);">
            ${tx.source}
          </span>
        </td>
        <td style="text-align: center;">
          <div class="action-buttons" style="justify-content: center;">
            <button class="action-icon-btn edit-tx-btn" data-id="${tx.id}" title="Edit transaction" aria-label="Edit">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button class="action-icon-btn delete delete-tx-btn" data-id="${tx.id}" title="Delete transaction" aria-label="Delete">
              <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
            </button>
          </div>
        </td>
      </tr>
    `;
  }).join('');

  // Attach row action listeners
  document.querySelectorAll('.edit-tx-btn').forEach(btn => {
    btn.addEventListener('click', () => openEditModal(parseInt(btn.getAttribute('data-id'), 10)));
  });

  document.querySelectorAll('.delete-tx-btn').forEach(btn => {
    btn.addEventListener('click', () => promptDelete(parseInt(btn.getAttribute('data-id'), 10)));
  });
}

function renderPagination(pagination) {
  const infoEl = document.getElementById('paginationInfo');
  const prevBtn = document.getElementById('prevPageBtn');
  const nextBtn = document.getElementById('nextPageBtn');
  const pageNumbersEl = document.getElementById('pageNumbers');

  const { page, total_items, total_pages, limit } = pagination;
  const start = total_items === 0 ? 0 : (page - 1) * limit + 1;
  const end = Math.min(page * limit, total_items);

  infoEl.textContent = `Showing ${start} to ${end} of ${total_items} entries`;

  prevBtn.disabled = page <= 1;
  nextBtn.disabled = page >= total_pages;

  pageNumbersEl.innerHTML = '';
  // Show page buttons
  for (let i = 1; i <= total_pages; i++) {
    if (i === 1 || i === total_pages || (i >= page - 1 && i <= page + 1)) {
      const btn = document.createElement('button');
      btn.className = `page-btn ${i === page ? 'active' : ''}`;
      btn.textContent = i;
      btn.addEventListener('click', () => {
        currentPage = i;
        loadTransactions();
      });
      pageNumbersEl.appendChild(btn);
    }
  }
}

function openAddModal() {
  const form = document.getElementById('transactionForm');
  form.reset();
  document.getElementById('editTxId').value = '';
  document.getElementById('modalTitle').textContent = 'Add Transaction';
  document.getElementById('txDate').value = new Date().toISOString().split('T')[0];
  populateCategoryDropdowns();
  openModal('transactionModal');
}

function openEditModal(txId) {
  const tx = currentTransactions.find(t => t.id === txId);
  if (!tx) return;

  document.getElementById('editTxId').value = tx.id;
  document.getElementById('modalTitle').textContent = 'Edit Transaction';
  document.getElementById('txType').value = tx.type;
  document.getElementById('txDate').value = tx.date;
  document.getElementById('txDescription').value = tx.description;
  document.getElementById('txAmount').value = tx.amount;

  populateCategoryDropdowns();
  document.getElementById('txCategory').value = tx.category_id;

  openModal('transactionModal');
}

function promptDelete(txId) {
  deleteTargetId = txId;
  openModal('deleteConfirmModal');
}

function setupEventListeners() {
  document.getElementById('addTransactionBtn').addEventListener('click', openAddModal);
  document.getElementById('modalCloseBtn').addEventListener('click', () => closeModal('transactionModal'));
  document.getElementById('modalCancelBtn').addEventListener('click', () => closeModal('transactionModal'));

  document.getElementById('deleteCloseBtn').addEventListener('click', () => closeModal('deleteConfirmModal'));
  document.getElementById('deleteCancelBtn').addEventListener('click', () => closeModal('deleteConfirmModal'));

  document.getElementById('deleteConfirmBtn').addEventListener('click', async () => {
    if (!deleteTargetId) return;
    try {
      await api.deleteTransaction(deleteTargetId);
      showToast('Transaction deleted successfully!');
      closeModal('deleteConfirmModal');
      loadTransactions();
    } catch (err) {
      showToast('Delete failed: ' + err.message, 'error');
    }
  });

  document.getElementById('txType').addEventListener('change', populateCategoryDropdowns);

  // Form submit
  document.getElementById('transactionForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const editId = document.getElementById('editTxId').value;
    const submitBtn = document.getElementById('modalSubmitBtn');
    submitBtn.disabled = true;

    const payload = {
      date: document.getElementById('txDate').value,
      description: document.getElementById('txDescription').value.trim(),
      amount: parseFloat(document.getElementById('txAmount').value),
      type: document.getElementById('txType').value,
      category_id: parseInt(document.getElementById('txCategory').value, 10)
    };

    try {
      if (editId) {
        await api.updateTransaction(editId, payload);
        showToast('Transaction updated successfully!');
      } else {
        await api.addTransaction(payload);
        showToast('Transaction added successfully!');
      }
      closeModal('transactionModal');
      loadTransactions();
    } catch (err) {
      showToast('Failed to save: ' + err.message, 'error');
    } finally {
      submitBtn.disabled = false;
    }
  });

  // Filter change handlers
  let searchTimeout = null;
  document.getElementById('filterSearch').addEventListener('input', () => {
    clearTimeout(searchTimeout);
    searchTimeout = setTimeout(() => {
      currentPage = 1;
      loadTransactions();
    }, 300);
  });

  document.getElementById('filterCategory').addEventListener('change', () => {
    currentPage = 1;
    loadTransactions();
  });

  document.getElementById('filterType').addEventListener('change', () => {
    currentPage = 1;
    loadTransactions();
  });

  document.getElementById('filterStartDate').addEventListener('change', () => {
    currentPage = 1;
    loadTransactions();
  });

  document.getElementById('filterEndDate').addEventListener('change', () => {
    currentPage = 1;
    loadTransactions();
  });

  document.getElementById('resetFiltersBtn').addEventListener('click', () => {
    document.getElementById('filterSearch').value = '';
    document.getElementById('filterCategory').value = '';
    document.getElementById('filterType').value = '';
    document.getElementById('filterStartDate').value = '';
    document.getElementById('filterEndDate').value = '';
    currentPage = 1;
    loadTransactions();
  });

  document.getElementById('prevPageBtn').addEventListener('click', () => {
    if (currentPage > 1) {
      currentPage--;
      loadTransactions();
    }
  });

  document.getElementById('nextPageBtn').addEventListener('click', () => {
    currentPage++;
    loadTransactions();
  });
}
