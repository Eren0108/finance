import { api, formatINR, showToast, openModal, closeModal, initMonthPicker, setupShell } from './api.js';

let selectedMonth = '';
let currentBudgetData = null;
let expenseCategories = [];

document.addEventListener('DOMContentLoaded', async () => {
  setupShell();

  selectedMonth = initMonthPicker('budgetsMonthSelect', (newMonth) => {
    selectedMonth = newMonth;
    loadBudgets(newMonth);
  });

  setupModalHandlers();
  await loadCategories();
  await loadBudgets(selectedMonth);
});

async function loadCategories() {
  try {
    const all = await api.getCategories('expense');
    expenseCategories = all;
    populateCategoryModalSelect();
  } catch (err) {
    showToast('Failed to load expense categories: ' + err.message, 'error');
  }
}

function populateCategoryModalSelect(selectedCatId = null) {
  const select = document.getElementById('budgetCategorySelect');
  if (!select) return;

  select.innerHTML = '';
  expenseCategories.forEach(cat => {
    const opt = document.createElement('option');
    opt.value = cat.id;
    opt.textContent = cat.name;
    if (selectedCatId && cat.id === selectedCatId) {
      opt.selected = true;
    }
    select.appendChild(opt);
  });
}

async function loadBudgets(month) {
  const tbody = document.getElementById('budgetsTableBody');
  tbody.innerHTML = `
    <tr>
      <td colspan="7" style="text-align: center; padding: 36px;">
        <span class="spinner"></span>
        <p style="margin-top: 8px; color: var(--text-muted); font-size: 0.85rem;">Loading budgets...</p>
      </td>
    </tr>
  `;

  try {
    const data = await api.getBudgets(month);
    currentBudgetData = data;
    updateOverviewStats(data);
    renderBudgetsTable(data.budgets);
  } catch (err) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--expense); padding: 30px;">
          Failed to load budgets: ${err.message}
        </td>
      </tr>
    `;
    showToast('Error loading budgets: ' + err.message, 'error');
  }
}

function updateOverviewStats(data) {
  document.getElementById('statTotalBudget').textContent = formatINR(data.total_budget);
  document.getElementById('statTotalSpent').textContent = formatINR(data.total_spent);
  document.getElementById('statTotalRemaining').textContent = formatINR(data.total_remaining);

  const overallEl = document.getElementById('statOverallPct');
  overallEl.textContent = `${data.overall_percentage}%`;
  
  if (data.overall_percentage > 100) {
    overallEl.style.color = 'var(--expense)';
  } else if (data.overall_percentage >= 70) {
    overallEl.style.color = 'var(--warning)';
  } else {
    overallEl.style.color = 'var(--income)';
  }
}

function renderBudgetsTable(budgets) {
  const tbody = document.getElementById('budgetsTableBody');

  if (!budgets || budgets.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="7" style="text-align: center; color: var(--text-muted); padding: 32px;">
          No expense categories found.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = budgets.map(b => {
    const hasLimit = b.limit_amount > 0;
    const pct = b.percentage;
    const barClass = pct > 100 ? 'over' : (pct >= 70 ? 'warning' : 'under');
    const widthPct = Math.min(pct, 100);

    let statusBadge = '<span class="badge" style="background: var(--surface-alt); color: var(--text-muted);">Unbudgeted</span>';
    if (hasLimit) {
      if (pct > 100) {
        statusBadge = '<span class="badge badge-expense">Over Budget</span>';
      } else if (pct >= 70) {
        statusBadge = '<span class="badge badge-warning">Near Limit</span>';
      } else {
        statusBadge = '<span class="badge badge-income">On Track</span>';
      }
    }

    return `
      <tr>
        <td>
          <div style="display: flex; align-items: center; gap: 10px;">
            <span class="cat-dot" style="background-color: ${b.category_color}; width: 10px; height: 10px;"></span>
            <span style="font-weight: 600;">${b.category_name}</span>
          </div>
        </td>
        <td style="text-align: right; font-weight: 600;" class="tabular-nums">
          ${hasLimit ? formatINR(b.limit_amount) : '<span style="color: var(--text-muted); font-weight: normal;">Not set</span>'}
        </td>
        <td style="text-align: right; font-weight: 600; color: var(--expense);" class="tabular-nums">
          ${formatINR(b.spent_amount)}
        </td>
        <td style="text-align: right; font-weight: 600; color: ${b.remaining_amount > 0 ? 'var(--income)' : 'var(--text-muted)'};" class="tabular-nums">
          ${hasLimit ? formatINR(b.remaining_amount) : '-'}
        </td>
        <td>
          ${hasLimit ? `
            <div style="display: flex; align-items: center; gap: 10px;">
              <div class="progress-container" style="flex: 1;">
                <div class="progress-bar ${barClass}" style="width: ${widthPct}%;"></div>
              </div>
              <span style="font-size: 0.8rem; font-weight: 600; min-width: 38px; text-align: right;" class="tabular-nums">
                ${pct}%
              </span>
            </div>
          ` : '<span style="font-size: 0.8rem; color: var(--text-muted);">No limit configured</span>'}
        </td>
        <td style="text-align: center;">
          ${statusBadge}
        </td>
        <td style="text-align: center;">
          <button class="btn btn-secondary btn-sm edit-budget-btn" 
                  data-catid="${b.category_id}" 
                  data-limit="${b.limit_amount}"
                  title="Configure budget">
            ${hasLimit ? 'Edit' : 'Set'}
          </button>
        </td>
      </tr>
    `;
  }).join('');

  // Row edit listeners
  document.querySelectorAll('.edit-budget-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const catId = parseInt(btn.getAttribute('data-catid'), 10);
      const limit = parseFloat(btn.getAttribute('data-limit')) || 0;
      openSetBudgetModal(catId, limit);
    });
  });
}

function openSetBudgetModal(categoryId = null, currentLimit = 0) {
  populateCategoryModalSelect(categoryId);
  document.getElementById('budgetLimitInput').value = currentLimit > 0 ? currentLimit : '';
  openModal('budgetModal');
}

function setupModalHandlers() {
  const setBudgetBtn = document.getElementById('setBudgetBtn');
  const closeBtn = document.getElementById('budgetModalCloseBtn');
  const cancelBtn = document.getElementById('budgetModalCancelBtn');
  const form = document.getElementById('budgetForm');

  if (setBudgetBtn) {
    setBudgetBtn.addEventListener('click', () => openSetBudgetModal());
  }

  if (closeBtn) closeBtn.addEventListener('click', () => closeModal('budgetModal'));
  if (cancelBtn) cancelBtn.addEventListener('click', () => closeModal('budgetModal'));

  if (form) {
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const submitBtn = document.getElementById('budgetModalSubmitBtn');
      submitBtn.disabled = true;

      const categoryId = parseInt(document.getElementById('budgetCategorySelect').value, 10);
      const limitAmount = parseFloat(document.getElementById('budgetLimitInput').value) || 0;

      try {
        await api.setBudget({
          category_id: categoryId,
          month: selectedMonth,
          limit_amount: limitAmount
        });

        showToast('Budget saved successfully!');
        closeModal('budgetModal');
        await loadBudgets(selectedMonth);
      } catch (err) {
        showToast('Failed to save budget: ' + err.message, 'error');
      } finally {
        submitBtn.disabled = false;
      }
    });
  }
}
