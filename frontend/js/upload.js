import { api, formatINR, formatDate, showToast, setupShell } from './api.js';

let selectedFile = null;
let parsedResponse = null;
let categoriesList = [];

document.addEventListener('DOMContentLoaded', () => {
  setupShell();
  setupDropzone();
  setupActionListeners();
});

function setupDropzone() {
  const dropzone = document.getElementById('dropzone');
  const fileInput = document.getElementById('fileInput');
  const browseBtn = document.getElementById('browseBtn');

  if (!dropzone || !fileInput) return;

  browseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    fileInput.click();
  });

  dropzone.addEventListener('click', () => fileInput.click());

  dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
  });

  dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
  });

  dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (e.target.files && e.target.files.length > 0) {
      handleFileSelected(e.target.files[0]);
    }
  });
}

function handleFileSelected(file) {
  const validExts = ['.csv', '.xlsx', '.xls'];
  const name = file.name.toLowerCase();
  const isValid = validExts.some(ext => name.endsWith(ext));

  if (!isValid) {
    showToast('Invalid file format. Please select a .csv, .xlsx, or .xls file.', 'error');
    return;
  }

  if (file.size > 5 * 1024 * 1024) {
    showToast('File size exceeds the 5 MB limit.', 'error');
    return;
  }

  selectedFile = file;
  document.getElementById('selectedFileName').textContent = file.name;
  document.getElementById('selectedFileSize').textContent = formatFileSize(file.size);
  document.getElementById('fileUploadStatus').style.display = 'flex';
}

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' bytes';
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / 1048576).toFixed(1) + ' MB';
}

function setupActionListeners() {
  const uploadProcessBtn = document.getElementById('uploadProcessBtn');
  const confirmImportBtn = document.getElementById('confirmImportBtn');
  const cancelPreviewBtn = document.getElementById('cancelPreviewBtn');
  const importAnotherBtn = document.getElementById('importAnotherBtn');
  const selectAllCheckbox = document.getElementById('selectAllCheckbox');

  if (uploadProcessBtn) {
    uploadProcessBtn.addEventListener('click', async () => {
      if (!selectedFile) return;

      uploadProcessBtn.disabled = true;
      uploadProcessBtn.innerHTML = '<span class="spinner" style="width: 16px; height: 16px;"></span> Parsing...';

      try {
        parsedResponse = await api.uploadStatement(selectedFile);
        categoriesList = parsedResponse.categories || [];
        showStep2Preview(parsedResponse);
      } catch (err) {
        showToast('Parse error: ' + err.message, 'error');
      } finally {
        uploadProcessBtn.disabled = false;
        uploadProcessBtn.innerHTML = '<span>Parse Statement</span>';
      }
    });
  }

  if (cancelPreviewBtn) {
    cancelPreviewBtn.addEventListener('click', resetToStep1);
  }

  if (importAnotherBtn) {
    importAnotherBtn.addEventListener('click', resetToStep1);
  }

  if (selectAllCheckbox) {
    selectAllCheckbox.addEventListener('change', (e) => {
      const isChecked = e.target.checked;
      document.querySelectorAll('.row-include-checkbox').forEach(cb => {
        cb.checked = isChecked;
      });
      updateConfirmButtonCount();
    });
  }

  if (confirmImportBtn) {
    confirmImportBtn.addEventListener('click', async () => {
      const rows = [];
      const trs = document.querySelectorAll('#previewTableBody tr');

      trs.forEach(tr => {
        const cb = tr.querySelector('.row-include-checkbox');
        if (!cb || !cb.checked) return;

        const rowIdx = parseInt(tr.getAttribute('data-index'), 10);
        const originalRow = parsedResponse.rows[rowIdx];
        const catSelect = tr.querySelector('.row-category-select');

        rows.push({
          date: originalRow.date,
          description: originalRow.description,
          amount: originalRow.amount,
          type: originalRow.type,
          category_id: parseInt(catSelect.value, 10),
          skip: false
        });
      });

      if (rows.length === 0) {
        showToast('Please select at least one transaction to import.', 'warning');
        return;
      }

      confirmImportBtn.disabled = true;
      confirmImportBtn.innerHTML = '<span class="spinner" style="width: 16px; height: 16px;"></span> Importing...';

      try {
        const res = await api.confirmStatement({
          filename: parsedResponse.filename,
          transactions: rows
        });

        showStep3Success(res);
      } catch (err) {
        showToast('Import failed: ' + err.message, 'error');
      } finally {
        confirmImportBtn.disabled = false;
        confirmImportBtn.innerHTML = '<span>Confirm & Import</span>';
      }
    });
  }
}

function showStep2Preview(data) {
  document.getElementById('step1Section').style.display = 'none';
  document.getElementById('step2Section').style.display = 'block';
  document.getElementById('step3Section').style.display = 'none';

  // Stepper updates
  document.getElementById('stepIndicator1').className = 'step-item completed';
  document.getElementById('stepIndicator2').className = 'step-item active';
  document.getElementById('stepIndicator3').className = 'step-item';

  // Counters
  document.getElementById('previewTotalCount').textContent = data.total_rows;
  document.getElementById('previewNewCount').textContent = data.new_count;
  document.getElementById('previewDupCount').textContent = data.duplicate_count;

  const tbody = document.getElementById('previewTableBody');
  tbody.innerHTML = data.rows.map((r, idx) => {
    const isDup = r.is_duplicate;
    const isIncome = r.type === 'income';

    const categoryOptions = categoriesList.map(cat => {
      const selected = cat.id === r.category_id ? 'selected' : '';
      return `<option value="${cat.id}" ${selected}>${cat.name}</option>`;
    }).join('');

    return `
      <tr class="${isDup ? 'highlight-duplicate' : ''}" data-index="${idx}">
        <td style="text-align: center;">
          <input type="checkbox" class="row-include-checkbox" ${isDup ? '' : 'checked'}>
        </td>
        <td style="white-space: nowrap; font-size: 0.825rem; color: var(--text-muted);">
          ${formatDate(r.date)}
        </td>
        <td>
          <span style="font-weight: 600;">${r.description}</span>
        </td>
        <td>
          <span class="badge ${isIncome ? 'badge-income' : 'badge-expense'}">
            ${r.type}
          </span>
        </td>
        <td style="text-align: right; font-weight: 700; ${isIncome ? 'color: var(--income);' : 'color: var(--expense);'}" class="tabular-nums">
          ${isIncome ? '+' : '-'}${formatINR(r.amount)}
        </td>
        <td>
          <select class="form-select row-category-select" style="padding: 4px 8px; font-size: 0.825rem;">
            ${categoryOptions}
          </select>
        </td>
        <td style="text-align: center;">
          ${isDup 
            ? '<span class="badge badge-warning">Duplicate</span>' 
            : '<span class="badge badge-income">New</span>'}
        </td>
      </tr>
    `;
  }).join('');

  // Attach checkbox change listener
  document.querySelectorAll('.row-include-checkbox').forEach(cb => {
    cb.addEventListener('change', updateConfirmButtonCount);
  });

  updateConfirmButtonCount();
}

function updateConfirmButtonCount() {
  const checkedCount = document.querySelectorAll('.row-include-checkbox:checked').length;
  const btn = document.getElementById('confirmImportBtn');
  if (btn) {
    btn.innerHTML = `<span>Confirm & Import (${checkedCount} Transactions)</span>`;
    btn.disabled = checkedCount === 0;
  }
}

function showStep3Success(result) {
  document.getElementById('step1Section').style.display = 'none';
  document.getElementById('step2Section').style.display = 'none';
  document.getElementById('step3Section').style.display = 'block';

  document.getElementById('stepIndicator1').className = 'step-item completed';
  document.getElementById('stepIndicator2').className = 'step-item completed';
  document.getElementById('stepIndicator3').className = 'step-item completed';

  document.getElementById('successSummaryMessage').textContent = result.message;
  showToast(result.message, 'success');
}

function resetToStep1() {
  selectedFile = null;
  parsedResponse = null;
  document.getElementById('fileInput').value = '';
  document.getElementById('fileUploadStatus').style.display = 'none';

  document.getElementById('step1Section').style.display = 'block';
  document.getElementById('step2Section').style.display = 'none';
  document.getElementById('step3Section').style.display = 'none';

  document.getElementById('stepIndicator1').className = 'step-item active';
  document.getElementById('stepIndicator2').className = 'step-item';
  document.getElementById('stepIndicator3').className = 'step-item';
}
