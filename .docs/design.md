# Design: Personal Finance Tracker

## 1. Design Principles

1. **Clarity first**: money data must be readable at a glance.
2. **Simple and calm**: few colors, lots of white space.
3. **Consistent**: same buttons, spacing, and cards on every page.
4. **Responsive**: works on phone, tablet, and desktop.
5. **Accessible**: good contrast, labels on every input, keyboard friendly.

## 2. Color Palette

| Role | Color | Hex |
|---|---|---|
| Primary | Indigo | `#4F46E5` |
| Primary hover | Dark indigo | `#4338CA` |
| Income / positive | Green | `#16A34A` |
| Expense / negative | Red | `#DC2626` |
| Warning (budget near limit) | Amber | `#F59E0B` |
| Background | Light gray | `#F3F4F6` |
| Card | White | `#FFFFFF` |
| Text main | Slate | `#1F2937` |
| Text muted | Gray | `#6B7280` |
| Border | Light border | `#E5E7EB` |

Dark mode is optional for a later phase. Define colors as CSS variables so it is easy to add:

```css
:root {
  --primary: #4F46E5;
  --income: #16A34A;
  --expense: #DC2626;
  --warning: #F59E0B;
  --bg: #F3F4F6;
  --card: #FFFFFF;
  --text: #1F2937;
  --muted: #6B7280;
  --border: #E5E7EB;
}
```

## 3. Typography

- Font: `Inter`, fallback `system-ui, Arial, sans-serif`
- Base size: 16px
- Headings: H1 28px, H2 22px, H3 18px (bold)
- Money values: bold, tabular numbers (`font-variant-numeric: tabular-nums`)
- Currency: INR with `Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' })`

## 4. Spacing and Shape

- Spacing scale: 4, 8, 12, 16, 24, 32, 48 px
- Card radius: 12px, button radius: 8px
- Card shadow: `0 1px 3px rgba(0,0,0,0.1)`
- Max content width: 1200px, centered

## 5. Layout

```
+---------------------------------------------------+
| Top bar: Logo | Month selector                    |
+-----------+---------------------------------------+
| Sidebar   |  Page content                         |
| Dashboard |                                       |
| Transact. |                                       |
| Upload    |                                       |
| Budgets   |                                       |
| Reports   |                                       |
+-----------+---------------------------------------+
```

On screens under 768px the sidebar becomes a bottom navigation bar.

## 6. Pages and Wireframes

### 6.1 Dashboard (`index.html`)

```
[ Total Income ] [ Total Expense ] [ Savings ] [ Savings Rate % ]

[ Expense by Category (Doughnut) ]   [ Income vs Expense (Bar, 6 months) ]

[ Budget progress bars ]             [ Recent 5 transactions ]
```

### 6.2 Transactions (`transactions.html`)

- Top: filter row (date range, category, type, search box) and **+ Add Transaction** button.
- Table columns: Date, Description, Category, Type, Amount, Actions (edit, delete).
- Income amounts in green with `+`, expenses in red with `-`.
- Add/Edit opens a modal form.
- Pagination: 20 rows per page.

### 6.3 Upload Statement (`upload.html`)

Steps shown as a stepper:

1. **Upload**: drag-and-drop area, accepts CSV / XLSX.
2. **Preview**: table of parsed rows with an editable category dropdown per row, and highlighted duplicates.
3. **Confirm**: summary ("48 rows will be imported, 3 skipped") and an Import button.

### 6.4 Budgets (`budgets.html`)

- Month picker.
- One row per expense category: name, limit input, spent, progress bar.
- Bar colors: green under 70%, amber 70 to 100%, red over 100%.

### 6.5 Reports (`reports.html`)

- Month and year selector.
- Summary card, category breakdown table, monthly trend line chart.
- **Download Excel** button.

## 7. Components

| Component | Notes |
|---|---|
| Stat card | Label, big number, small trend text |
| Button | Primary (filled), Secondary (outline), Danger (red) |
| Modal | Centered, dark overlay, closes on Esc |
| Form input | Label above, error text in red below |
| Table | Zebra rows, sticky header, hover highlight |
| Toast | Top-right message for success or error, auto-hide in 3s |
| Progress bar | Used for budgets |
| Empty state | Friendly text and an action button when no data exists |

## 8. Charts (Chart.js)

| Chart | Type | Data |
|---|---|---|
| Expense by category | Doughnut | Sum per category for selected month |
| Income vs expense | Grouped bar | Last 6 months |
| Savings trend | Line | Monthly savings |

Use the category colors stored in the DB so each category looks the same everywhere.

## 9. Interaction Rules

- Show a loading spinner while any API call runs.
- Confirm before deleting ("Delete this transaction?").
- Show validation errors beside the field, not only as alerts.
- After add, edit, or delete, refresh the table and dashboard numbers without reloading the page.
- Disable the submit button while a request is in progress.

## 10. Responsive Breakpoints

| Name | Width | Behavior |
|---|---|---|
| Mobile | < 768px | Single column, bottom nav, tables scroll horizontally |
| Tablet | 768 to 1024px | Two column cards, collapsed sidebar |
| Desktop | > 1024px | Full sidebar, multi-column dashboard |

## 11. Accessibility Checklist

- Text contrast ratio at least 4.5:1
- Every input has a `<label>`
- Buttons use `<button>`, not clickable divs
- Do not rely on color alone: also use `+` / `-` signs and icons
- Visible focus outline on interactive elements
