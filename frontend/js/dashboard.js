import { api, formatINR, formatDate, showToast, openModal, closeModal, initMonthPicker, setupShell } from './api.js';
import { renderCategoryDoughnut, renderTrendBarChart } from './charts.js';

let currentCategories = [];
let selectedMonth = '';

document.addEventListener('DOMContentLoaded', async () => {
  setupShell();

  // Initialize Month Picker
  selectedMonth = initMonthPicker('dashboardMonthSelect', (newMonth) => {
    selectedMonth = newMonth;
    loadDashboardData(newMonth);
  });

  // Setup Add Transaction Modal
  setupModalHandlers();

  // Load initial data
  await loadCategories();
  await loadDashboardData(selectedMonth);
});

async function loadCategories() {
  try {
    currentCategories = await api.getCategories();
    populateCategorySelect();
  } catch (err) {
    showToast('Failed to load categories: ' + err.message, 'error');
  }
}

function populateCategorySelect() {
  const select = document.getElementById('txCategory');
  const typeSelect = document.getElementById('txType');
  if (!select || !typeSelect) return;

  const currentType = typeSelect.value;
  select.innerHTML = '';

  const filtered = currentCategories.filter(c => c.type === currentType);
  filtered.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = cat.name;
    select.appendChild(opt);
  });
}

async function loadDashboardData(month) {
  try {
    const [summary, trend] = await Promise.all([
      api.getSummary(month),
      api.getTrend(6, month)
    ]);

    updateStatCards(summary);
    renderCategoryDoughnut('categoryChart', summary.categories);
    renderTrendBarChart('trendChart', trend);
    renderBudgetProgress(summary.categories);
    renderRecentTransactions(summary.recent_transactions);
    renderBudgetAlerts(summary.budget_warnings);
  } catch (err) {
    showToast('Error loading dashboard: ' + err.message, 'error');
  }
}

function updateStatCards(summary) {
  document.getElementById('statIncome').textContent = formatINR(summary.total_income);
  document.getElementById('statExpense').textContent = formatINR(summary.total_expense);
  
  const savingsEl = document.getElementById('statSavings');
  savingsEl.textContent = formatINR(summary.savings);
  if (summary.savings < 0) {
    savingsEl.style.color = 'var(--expense)';
  } else {
    savingsEl.style.color = 'var(--income)';
  }

  const rateEl = document.getElementById('statSavingsRate');
  rateEl.textContent = `${summary.savings_rate}%`;
  rateEl.style.color = summary.savings_rate >= 20 ? 'var(--income)' : (summary.savings_rate > 0 ? 'var(--warning)' : 'var(--expense)');
}

function renderBudgetAlerts(warnings) {
  const container = document.getElementById('budgetAlertsContainer');
  if (!container) return;

  if (!warnings || warnings.length === 0) {
    container.style.display = 'none';
    container.innerHTML = '';
    return;
  }

  container.style.display = 'block';
  container.innerHTML = `
    <div style="background-color: var(--warning-light); border: 1px solid var(--warning-border); border-radius: var(--radius-lg); padding: 14px 18px; display: flex; align-items: center; gap: 12px;">
      <svg style="width: 24px; height: 24px; color: var(--warning); flex-shrink: 0;" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
      </svg>
      <div>
        <strong style="color: #92400E; font-size: 0.9rem;">Budget Warning:</strong>
        <span style="color: #78350F; font-size: 0.85rem; margin-left: 6px;">
          ${warnings.map(w => `<strong>${w.category_name}</strong> is at ${w.budget_percentage}% of limit`).join(', ')}.
        </span>
      </div>
    </div>
  `;
}

function renderBudgetProgress(categories) {
  const container = document.getElementById('budgetProgressList');
  if (!container) return;

  const budgeted = (categories || []).filter(c => c.budget_limit > 0);

  if (budgeted.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="padding: 24px 10px;">
        <p class="empty-state-desc">No category budgets set for this month.</p>
        <a href="budgets.html" class="btn btn-secondary btn-sm" style="margin-top: 8px;">Set Budgets</a>
      </div>
    `;
    return;
  }

  container.innerHTML = budgeted.slice(0, 5).map(cat => {
    const pct = cat.budget_percentage;
    const barClass = pct > 100 ? 'over' : (pct >= 70 ? 'warning' : 'under');
    const widthPct = Math.min(pct, 100);

    return `
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <div style="display: flex; align-items: center; gap: 8px;">
            <span class="cat-dot" style="background-color: ${cat.category_color};"></span>
            <span style="font-size: 0.875rem; font-weight: 600;">${cat.category_name}</span>
          </div>
          <div style="font-size: 0.8rem; color: var(--text-muted);">
            <strong class="tabular-nums" style="color: var(--text);">${formatINR(cat.spent)}</strong> / ${formatINR(cat.budget_limit)}
            <span class="badge ${barClass === 'over' ? 'badge-expense' : (barClass === 'warning' ? 'badge-warning' : 'badge-income')}" style="margin-left: 6px;">
              ${pct}%
            </span>
          </div>
        </div>
        <div class="progress-container">
          <div class="progress-bar ${barClass}" style="width: ${widthPct}%;"></div>
        </div>
      </div>
    `;
  }).join('');
}

function renderRecentTransactions(transactions) {
  const tbody = document.getElementById('recentTransactionsTable');
  if (!tbody) return;

  if (!transactions || transactions.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="4" style="text-align: center; color: var(--text-muted); padding: 32px;">
          No transactions recorded for this month yet.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = transactions.map(tx => {
    const isIncome = tx.type === 'income';
    const sign = isIncome ? '+' : '-';
    const colorClass = isIncome ? 'color: var(--income); font-weight: 700;' : 'color: var(--expense); font-weight: 700;';

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
        <td style="text-align: right; ${colorClass}" class="tabular-nums">
          ${sign}${formatINR(tx.amount)}
        </td>
      </tr>
    `;
  }).join('');
}

function setupModalHandlers() {
  const quickAddBtn = document.getElementById('quickAddBtn');
  const closeBtn = document.getElementById('modalCloseBtn');
  const cancelBtn = document.getElementById('modalCancelBtn');
  const form = document.getElementById('transactionForm');
  const typeSelect = document.getElementById('txType');
  const dateInput = document.getElementById('txDate');

  if (quickAddBtn) {
    quickAddBtn.addEventListener('click', () => {
      form.reset();
      document.getElementById('editTxId').value = '';
      document.getElementById('modalTitle').textContent = 'Add Transaction';
      dateInput.value = new Date().toISOString().split('T')[0];
      populateCategorySelect();
      openModal('transactionModal');
    });
  }

  if (closeBtn) closeBtn.addEventListener('click', () => closeModal('transactionModal'));
  if (cancelBtn) cancelBtn.addEventListener('click', () => closeModal('transactionModal'));

  if (typeSelect) {
    typeSelect.addEventListener('change', populateCategorySelect);
  }

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('modalSubmitBtn');
      submitBtn.disabled = true;
      submitBtn.textContent = 'Saving...';

      const payload = {
        date: dateInput.value,
        description: document.getElementById('txDescription').value.trim(),
        amount: parseFloat(document.getElementById('txAmount').value),
        type: typeSelect.value,
        category_id: parseInt(document.getElementById('txCategory').value, 10)
      };

      try {
        await api.addTransaction(payload);
        showToast('Transaction added successfully!');
        closeModal('transactionModal');
        await loadDashboardData(selectedMonth);
      } catch (err) {
        showToast('Error saving transaction: ' + err.message, 'error');
      } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Save Transaction';
      }
    });
  }
}
