Here is the content of the Sprint 3 documentation for you to copy:

Sprint 3: Search, Network Visualization & User Profiles
1. Sprint Goal
Outcome-Focused Goal: Enable users to search companies using advanced filters, view detailed profiles with financial and network indicators, and export structured data as timestamped reports, with all endpoints integrated into the frontend and at least one validated report format.

2. Board Improvements & Policies
Based on feedback from the previous review.

Hierarchy Restructuring
Parent vs. Child: We have moved away from a "flat" list. Technical tasks are now Sub-tasks nested inside User Stories.

Status Hygiene: A User Story is only moved to "IN REVIEW" when all its sub-tasks are complete and the feature is ready for QA. If development is still ongoing for any sub-task, the Story remains "IN PROGRESS".

Task Formulation: Generic tasks like "Tests" have been replaced with specific sub-tasks (e.g., "Write Unit Tests for Auth Service").

3. User Stories & Execution Plan
BZR-47: User Login & Session Management
Story: As a user, I want to log in to the application so that I can access my saved companies and preferences. Priority: High (User Profile Epic)

Description: Implement the full authentication flow using our OIDC provider (Keycloak/Auth0). The user needs a login screen, a signup screen, and a persistent session state.

Acceptance Criteria (AC):

[ ] User can navigate to /login and see email/password fields.

[ ] Successful login redirects to the Dashboard.

[ ] Invalid credentials show a specific error message ("Invalid email or password").

[ ] Session persists on page refresh (token storage in cookies/local storage).

[ ] "Logout" button clears the session and redirects to the Home page.

Sub-tasks (Technical Implementation):

[FE] Implement Login Screen UI (Inputs, Button, Error states).

[FE] Implement Signup Screen UI with validation.

[BE] Connect Backend to OIDC provider (Keycloak/Auth0 config).

[BE] Create specific Endpoint /auth/me to return current user identity.

[TEST] Write Unit tests for auth token validation logic.

BZR-34: Network Graph Visualization
Story: As a user, I want to see a visual graph of company links so that I can understand the ownership structure and risk. Priority: High (Network & Graph Epic)

Description: A visual rendering of the graph database data. The central node is the queried company, with edges connecting to shareholders and subsidiaries.

Acceptance Criteria (AC):

[ ] Graph renders with the target company in the center (Seed Node).

[ ] At least 1 level of "hops" (neighbors) is visible initially.

[ ] Different edge types (e.g., "Ownership", "Partnership") are visually distinct (color or line style).

[ ] Clicking a node shows a tooltip with the company name.

Sub-tasks (Technical Implementation):

[BE] Create Graph Service endpoint: GET /graph/{companyId}?depth=1.

[FE] Integrate Visualization Library (e.g., D3.js, Cytoscape, or Recharts).

[FE] Implement Canvas rendering component.

[FE] Add "Legend" UI to explain edge colors.

[TEST] Verify graph data structure response matches frontend expectations.

BZR-36: Change Alerts System
Story: As a user, I want to be alerted when changes appear in a saved company so that I can react to risks immediately. Priority: Medium (User Profile Epic)

Description: The system needs to detect changes in the data (e.g., new bankruptcy filing, change of CEO) and flag this to the user.

Acceptance Criteria (AC):

[ ] User can toggle a "Watch" button on a specific company profile.

[ ] When data ingestion updates a "Watched" company, a system flag is created.

[ ] Dashboard shows a list of "Recent Alerts" for the user.

Sub-tasks (Technical Implementation):

[BE] Create database table/collection UserWatchlist.

[BE] Implement logic to compare new data ingest vs. old data (Diffing logic).

[FE] Add "Bell" icon/toggle on Company Profile header.

[FE] Create "Alerts" widget on the User Dashboard.

[TEST] Integration test: Simulate data update -> Verify alert created.

BZR-37: Share Company Profile
Story: As a user, I want to share a specific company view with a colleague so that we can collaborate on analysis. Priority: Medium (Company Overview Epic)

Description: Users need a way to send a deep link to a specific company's data or report that works for other authenticated users.

Acceptance Criteria (AC):

[ ] "Share" button exists on the Company Profile.

[ ] Clicking share copies a URL to the clipboard (e.g., app.com/company/123).

[ ] If the receiving user is not logged in, they are redirected to Login, then back to the company page.

Sub-tasks (Technical Implementation):

[FE] Implement "Copy to Clipboard" functionality.

[BE] Ensure URL routing handles specific IDs correctly /companies/{id}.

[FE] Add Toast notification ("Link copied!").

[TEST] Test URL redirection flow for unauthenticated users.

BZR-101: Clean and Normalize Firmenbuch Data
Story: As a developer/data engineer, I want to polish the imported Firmenbuch data so that users do not see encoding errors or bad formatting. Priority: Medium (Data Quality)

Description: The raw data from the register currently has encoding errors (e.g., broken umlauts like 'Ã¼' instead of 'ü') and inconsistent address formats that clutter the UI.

Acceptance Criteria (AC):

[ ] All company names in the DB are UTF-8 encoded correctly.

[ ] Addresses are split into distinct fields: Street, City, Zip (where possible).

[ ] No "Null" strings visible in the frontend address block.

Sub-tasks (Technical Implementation):

[DATA] Write regex script to fix common encoding artifacts.

[DATA] Implement address parsing logic (Street/City separation).

[MIGRATION] Run update script on existing database records.

[TEST] Validate sample set of companies with special characters.