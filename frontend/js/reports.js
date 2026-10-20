import { api, formatINR, showToast, initMonthPicker, setupShell } from './api.js';
import { renderTrendLineChart } from './charts.js';

let selectedMonth = '';

document.addEventListener('DOMContentLoaded', async () => {
  setupShell();

  selectedMonth = initMonthPicker('reportsMonthSelect', (newMonth) => {
    selectedMonth = newMonth;
    loadReportData(newMonth);
  });

  setupExportHandler();
  await loadReportData(selectedMonth);
});

async function loadReportData(month) {
  try {
    const [summary, trend] = await Promise.all([
      api.getSummary(month),
      api.getTrend(6, month)
    ]);

    updateKPIs(summary);
    renderTrendLineChart('savingsTrendChart', trend);
    renderCategoryReportTable(summary.categories);
  } catch (err) {
    showToast('Failed to load report: ' + err.message, 'error');
  }
}

function updateKPIs(summary) {
  document.getElementById('repIncome').textContent = formatINR(summary.total_income);
  document.getElementById('repExpense').textContent = formatINR(summary.total_expense);

  const savingsEl = document.getElementById('repSavings');
  savingsEl.textContent = formatINR(summary.savings);
  savingsEl.style.color = summary.savings >= 0 ? 'var(--income)' : 'var(--expense)';

  const rateEl = document.getElementById('repSavingsRate');
  rateEl.textContent = `${summary.savings_rate}%`;
  rateEl.style.color = summary.savings_rate >= 20 ? 'var(--income)' : (summary.savings_rate > 0 ? 'var(--warning)' : 'var(--expense)');
}

function renderCategoryReportTable(categories) {
  const tbody = document.getElementById('reportCategoryTableBody');

  if (!categories || categories.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="text-align: center; color: var(--text-muted); padding: 32px;">
          No expense records for this month.
        </td>
      </tr>
    `;
    return;
  }

  tbody.innerHTML = categories.map(cat => {
    const budgetPct = cat.budget_limit > 0 ? `${cat.budget_percentage}%` : '-';
    let budgetPctBadge = budgetPct;
    if (cat.budget_limit > 0) {
      const cls = cat.budget_percentage > 100 ? 'badge-expense' : (cat.budget_percentage >= 70 ? 'badge-warning' : 'badge-income');
      budgetPctBadge = `<span class="badge ${cls}">${cat.budget_percentage}%</span>`;
    }

    return `
      <tr>
        <td>
          <div style="display: flex; align-items: center; gap: 10px;">
            <span class="cat-dot" style="background-color: ${cat.category_color};"></span>
            <span style="font-weight: 600;">${cat.category_name}</span>
          </div>
        </td>
        <td style="text-align: right; color: var(--text-muted);" class="tabular-nums">
          ${cat.budget_limit > 0 ? formatINR(cat.budget_limit) : '-'}
        </td>
        <td style="text-align: right; font-weight: 700; color: var(--expense);" class="tabular-nums">
          ${formatINR(cat.spent)}
        </td>
        <td style="text-align: right;">
          ${budgetPctBadge}
        </td>
        <td style="text-align: right; font-weight: 600;" class="tabular-nums">
          ${cat.percentage_of_total}%
        </td>
        <td style="text-align: center;" class="tabular-nums">
          ${cat.count}
        </td>
      </tr>
    `;
  }).join('');
}

function setupExportHandler() {
  const downloadBtn = document.getElementById('downloadExcelBtn');
  if (!downloadBtn) return;

  downloadBtn.addEventListener('click', () => {
    showToast('Preparing Excel workbook for download...', 'success');
    const exportUrl = api.getExportUrl(selectedMonth);
    
    // Create temporary invisible link to trigger download
    const link = document.createElement('a');
    link.href = exportUrl;
    link.setAttribute('download', `finance_report_${selectedMonth}.xlsx`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  });
}
