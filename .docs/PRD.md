# PRD: Personal Finance Tracker

**Version:** 1.0 (MVP)
**Status:** Draft
**Owner:** Project builder

---

## 1. Problem Statement

Most people do not know where their money goes. Bank statements are long and hard to read, and manual notes or spreadsheets are tedious. People need one simple place to record spending, see clear summaries, and stay within a budget.

## 2. Goal

Build a simple website that lets a person record income and expenses, import bank statements, see visual summaries, set monthly budgets, and export reports to Excel.

### Success Criteria

- A user can add a transaction in under 15 seconds.
- A user can import a 100-row statement in under 2 minutes, including review.
- The dashboard clearly shows income, expense, and savings for any month.
- The Excel export opens correctly in Excel and Google Sheets.
- The app runs locally without errors on a fresh setup following the README.

## 3. Target User

**Primary:** Students, salaried individuals, and freelancers in India who want to understand their monthly spending, with no accounting knowledge.

**User needs:**
- Easy data entry
- Clear charts instead of raw numbers
- Warnings before overspending
- Data stays private on their own computer

## 4. Scope

### In Scope (MVP)

1. Add, edit, delete, and search transactions
2. Default and custom categories
3. Dashboard with summary cards and charts
4. Bank statement upload (CSV and Excel) with preview and auto-categorization
5. Monthly category budgets with progress indicators
6. Monthly reports and Excel export
7. Responsive design for phone and desktop

### Out of Scope (MVP)

- User accounts and login
- PDF statement parsing
- Direct bank connection or UPI sync
- Multi-currency
- Investment tracking
- Mobile native app
- Cloud hosting

## 5. Features and Requirements

### F1: Transaction Management

| ID | Requirement | Priority |
|---|---|---|
| F1.1 | Add a transaction with date, description, amount, type, category | Must |
| F1.2 | Edit and delete a transaction with confirmation | Must |
| F1.3 | List transactions in a table with pagination | Must |
| F1.4 | Filter by date range, category, type; search by description | Should |
| F1.5 | Validate input (positive amount, valid date, required fields) | Must |

**Acceptance:** Given valid data, when the user submits the form, then the transaction appears in the table and the dashboard totals update without a page reload.

### F2: Categories

| ID | Requirement | Priority |
|---|---|---|
| F2.1 | Provide default categories (Food, Rent, Travel, Shopping, Bills, Health, Entertainment, Salary, Other) | Must |
| F2.2 | User can add a custom category with a color | Should |

### F3: Dashboard

| ID | Requirement | Priority |
|---|---|---|
| F3.1 | Cards: total income, total expense, savings, savings rate | Must |
| F3.2 | Doughnut chart of expenses by category | Must |
| F3.3 | Bar chart of income vs expense for the last 6 months | Should |
| F3.4 | Recent transactions list and budget warnings | Should |
| F3.5 | Month selector | Must |

### F4: Bank Statement Import

| ID | Requirement | Priority |
|---|---|---|
| F4.1 | Upload `.csv`, `.xlsx`, `.xls` up to 5 MB | Must |
| F4.2 | Detect and map columns: date, description, debit, credit | Must |
| F4.3 | Auto-suggest category using keywords (e.g. "Swiggy" -> Food) | Should |
| F4.4 | Show preview; allow category edits before saving | Must |
| F4.5 | Detect and skip duplicates | Should |
| F4.6 | Show clear errors for unreadable or wrong-format files | Must |

**Acceptance:** Given a valid statement, when the user confirms the preview, then all non-duplicate rows are saved and a count is shown.

### F5: Budgets

| ID | Requirement | Priority |
|---|---|---|
| F5.1 | Set a monthly limit per expense category | Must |
| F5.2 | Show spent vs limit with a progress bar | Must |
| F5.3 | Color states: green under 70%, amber 70 to 100%, red over 100% | Should |

### F6: Reports and Export

| ID | Requirement | Priority |
|---|---|---|
| F6.1 | Monthly summary with category breakdown | Must |
| F6.2 | Export `.xlsx` with Summary and Transactions sheets | Must |
| F6.3 | Monthly trend chart | Could |

## 6. Non-Functional Requirements

| Area | Requirement |
|---|---|
| Performance | Pages load in under 2 seconds; API responses under 500 ms for 10,000 rows |
| Usability | A beginner can use it without instructions |
| Responsiveness | Works from 360px to 1920px width |
| Security | Server-side validation, safe file handling, no secrets in code |
| Privacy | Data stored locally in SQLite; nothing sent to third parties |
| Compatibility | Latest Chrome, Edge, Firefox, Safari |
| Maintainability | Follows `rules.md`; modular folder structure |

## 7. User Stories

1. As a user, I want to add my daily expenses quickly so I do not forget them.
2. As a user, I want to upload my bank statement so I do not type everything manually.
3. As a user, I want to see a chart of where my money goes so I can cut unnecessary spending.
4. As a user, I want to set a budget for food so I get warned when I overspend.
5. As a user, I want to download my monthly report in Excel so I can share or keep it.

## 8. User Flow

```
Open app -> Dashboard
   |-- Add Transaction -> Form -> Save -> Dashboard updates
   |-- Upload Statement -> Preview -> Fix categories -> Confirm -> Transactions saved
   |-- Budgets -> Set limits -> See progress
   |-- Reports -> Pick month -> View -> Download Excel
```

## 9. Assumptions and Constraints

- Single user on a local machine.
- Builder is a beginner, so simplicity beats advanced features.
- Bank statements differ by bank; the parser starts with common column names and grows.
- Currency is INR only.

## 10. Risks and Mitigation

| Risk | Impact | Mitigation |
|---|---|---|
| Statement formats vary by bank | Import fails | Flexible column mapping, clear error messages, sample files per bank |
| Wrong auto-categories | Bad reports | Preview step and editable categories |
| Beginner gets stuck | Project stalls | Small steps, `memory.md` log, error help |
| Data loss | Users lose history | Simple DB backup and Excel export |
| Duplicate imports | Inflated totals | Duplicate detection on date, description, amount |

## 11. Milestones

| Milestone | Steps | Outcome |
|---|---|---|
| M1: Foundation | 1 to 5 | Environment, Flask server, base UI |
| M2: Core | 6 to 8 | Database, transactions, dashboard |
| M3: Import | 9 | Statement upload working |
| M4: Planning | 10 to 11 | Budgets and Excel export |
| M5: Release | 12 | Tested, documented MVP |

## 12. Future Roadmap

- Login and multi-user support
- PDF statement parsing
- Recurring transactions and bill reminders
- Savings goals
- Cloud deployment
- Dark mode and mobile app (PWA)

## 13. Related Documents

- `architecture.md`: technical structure
- `design.md`: UI and visual design
- `rules.md`: coding and working rules
- `task.md`: step-by-step checklist
- `memory.md`: progress and decisions log
