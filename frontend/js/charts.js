/**
 * Chart.js Integration for Personal Finance Tracker
 */

import { formatINR } from './api.js';

let doughnutChartInstance = null;
let trendBarChartInstance = null;
let trendLineChartInstance = null;

export function renderCategoryDoughnut(canvasId, categories) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  const validCategories = (categories || []).filter(c => Number(c.spent) > 0);

  if (doughnutChartInstance) {
    doughnutChartInstance.destroy();
  }

  const ctx = canvas.getContext('2d');

  if (validCategories.length === 0) {
    // Show placeholder in empty chart
    doughnutChartInstance = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['No Expenses Recorded'],
        datasets: [{
          data: [1],
          backgroundColor: ['#E2E8F0'],
          borderWidth: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        },
        cutout: '72%'
      }
    });
    return;
  }

  const labels = validCategories.map(c => c.category_name);
  const data = validCategories.map(c => c.spent);
  const colors = validCategories.map(c => c.category_color || '#4F46E5');

  doughnutChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: labels,
      datasets: [{
        data: data,
        backgroundColor: colors,
        hoverOffset: 6,
        borderWidth: 2,
        borderColor: '#FFFFFF'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom',
          labels: {
            boxWidth: 12,
            padding: 14,
            font: { family: 'Inter', size: 12, weight: '500' }
          }
        },
        tooltip: {
          callbacks: {
            label: (item) => {
              const label = item.label || '';
              const val = formatINR(item.raw);
              return ` ${label}: ${val}`;
            }
          }
        }
      },
      cutout: '68%'
    }
  });
}

export function renderTrendBarChart(canvasId, trendData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  if (trendBarChartInstance) {
    trendBarChartInstance.destroy();
  }

  const ctx = canvas.getContext('2d');
  const items = trendData || [];
  const labels = items.map(d => d.label);
  const incomeData = items.map(d => d.income);
  const expenseData = items.map(d => d.expense);

  trendBarChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: labels,
      datasets: [
        {
          label: 'Income',
          data: incomeData,
          backgroundColor: '#16A34A',
          borderRadius: 6,
          barPercentage: 0.65,
          categoryPercentage: 0.7
        },
        {
          label: 'Expenses',
          data: expenseData,
          backgroundColor: '#DC2626',
          borderRadius: 6,
          barPercentage: 0.65,
          categoryPercentage: 0.7
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
          align: 'end',
          labels: {
            boxWidth: 12,
            padding: 14,
            font: { family: 'Inter', size: 12, weight: '500' }
          }
        },
        tooltip: {
          callbacks: {
            label: (item) => ` ${item.dataset.label}: ${formatINR(item.raw)}`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 11 } }
        },
        y: {
          grid: { color: '#F1F5F9' },
          ticks: {
            font: { family: 'Inter', size: 11 },
            callback: (val) => '₹' + (val >= 1000 ? (val / 1000).toFixed(0) + 'k' : val)
          }
        }
      }
    }
  });
}

export function renderTrendLineChart(canvasId, trendData) {
  const canvas = document.getElementById(canvasId);
  if (!canvas) return;

  if (trendLineChartInstance) {
    trendLineChartInstance.destroy();
  }

  const ctx = canvas.getContext('2d');
  const items = trendData || [];
  const labels = items.map(d => d.label);
  const savingsData = items.map(d => d.savings);

  trendLineChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: labels,
      datasets: [{
        label: 'Net Savings',
        data: savingsData,
        borderColor: '#4F46E5',
        backgroundColor: 'rgba(79, 70, 229, 0.08)',
        fill: true,
        tension: 0.35,
        borderWidth: 2.5,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: '#4F46E5'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            label: (item) => ` Savings: ${formatINR(item.raw)}`
          }
        }
      },
      scales: {
        x: {
          grid: { display: false },
          ticks: { font: { family: 'Inter', size: 11 } }
        },
        y: {
          grid: { color: '#F1F5F9' },
          ticks: {
            font: { family: 'Inter', size: 11 },
            callback: (val) => '₹' + (val >= 1000 ? (val / 1000).toFixed(0) + 'k' : val)
          }
        }
      }
    }
  });
}
