<h1>Finance Dashboard API</h1>

<p>
  A backend API for managing financial records with role-based access control.
</p>

<h2>Project Summary</h2>
<p>
  This project is a backend-only finance dashboard system. It focuses on API design,
  financial record management, validation, access control, and summary analytics.
  The goal was to build a clean and maintainable backend that can later serve a frontend dashboard if needed.
</p>

<h2>Current Status</h2>
<ul>
  <li>Database seeding is working.</li>
  <li>JWT login is working from Swagger UI.</li>
  <li>Role-based access control is working for Admin, Analyst, and Viewer roles.</li>
  <li>Financial transaction CRUD and filtering are implemented.</li>
  <li>Dashboard summary, category breakdown, monthly trends, and recent activity endpoints are implemented.</li>
  <li>Admin user-management endpoints for listing users, updating roles, and activating/deactivating users are implemented.</li>
  <li>This project is backend-only. It exposes API endpoints and Swagger docs, not a frontend dashboard page.</li>
</ul>

<h2>Tech Choices and Assumptions</h2>
<ul>
  <li>
    <strong>FastAPI</strong> — I used FastAPI because it is the Python backend framework I am most comfortable with,
    and it lets me build APIs quickly without sacrificing structure.
  </li>
  <li>
    <strong>SQLite</strong> — I used SQLite to keep setup simple. The project can be cloned and run locally
    without Docker or an external database. Since the app uses SQLAlchemy, switching to PostgreSQL later would mainly
    involve changing the connection URL.
  </li>
  <li>
    <strong>JWT Authentication</strong> — Authentication uses JWT access tokens. For this assessment,
    I kept the flow simple and practical. In a production version, I would extend this with refresh tokens and better token lifecycle handling.
  </li>
  <li>
    <strong>Flexible Categories</strong> — Transaction categories are stored as free text instead of a strict enum,
    because finance tools usually need flexibility for user-defined categories.
  </li>
</ul>

<h2>Mapping</h2>
<ul>
  <li>User creation and role-based restriction</li>
  <li>User listing, role updates, and active/inactive status management</li>
  <li>Financial records CRUD</li>
  <li>Filtering by date, category, and type</li>
  <li>Dashboard summary APIs</li>
  <li>Category-wise totals</li>
  <li>Monthly trends</li>
  <li>Recent activity</li>
  <li>Validation and error handling</li>
  <li>Persistent storage using SQLite</li>
</ul>

<h2>Quick Start</h2>

<pre><code>git clone &lt;https://github.com/dinesh875-k/finance_backend.git&gt;
cd finance_backend
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload</code></pre>

<p><strong>Swagger Docs:</strong> <code>http://127.0.0.1:8000/docs</code></p>

<h2>Seeded Test Credentials</h2>

<table>
  <thead>
    <tr>
      <th>Role</th>
      <th>Username</th>
      <th>Password</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Admin</td>
      <td>admin</td>
      <td>admin123</td>
    </tr>
    <tr>
      <td>Analyst</td>
      <td>analyst1</td>
      <td>123456</td>
    </tr>
    <tr>
      <td>Viewer</td>
      <td>viewer1</td>
      <td>123456</td>
    </tr>
  </tbody>
</table>

<h2>Authentication in Swagger</h2>
<ul>
  <li>Open <code>/docs</code>.</li>
  <li>Click <strong>Authorize</strong>.</li>
  <li>Login with one of the seeded usernames and passwords above.</li>
  <li><code>client_id</code> and <code>client_secret</code> are not required.</li>
</ul>

<h2>API Overview</h2>

<h3>Authentication</h3>
<ul>
  <li><code>POST /users/login</code> — Authenticate and get JWT token</li>
  <li><code>POST /users/register</code> — Create a new user (Admin only)</li>
  <li><code>GET /users/me</code> — View the authenticated user's profile</li>
</ul>

<h3>User Management</h3>
<ul>
  <li><code>GET /users/</code> — List all users (Admin only)</li>
  <li><code>PATCH /users/{user_id}/role</code> — Update a user's role (Admin only)</li>
  <li><code>PATCH /users/{user_id}/status</code> — Activate or deactivate a user (Admin only)</li>
</ul>

<h3>Transactions</h3>
<ul>
  <li><code>POST /transactions/</code> — Create a transaction (Admin only)</li>
  <li><code>GET /transactions/</code> — List transactions with filters:
    <code>category</code>, <code>type</code>, <code>start_date</code>, <code>end_date</code>,
    <code>limit</code>, <code>offset</code>
  </li>
  <li><code>GET /transactions/{id}</code> — Get a single transaction</li>
  <li><code>PUT /transactions/{id}</code> — Update a transaction (Admin only)</li>
  <li><code>DELETE /transactions/{id}</code> — Delete a transaction (Admin only)</li>
</ul>

<h3>Dashboard</h3>
<ul>
  <li><code>GET /dashboard/summary</code> — Total income, total expenses, net balance, and transaction count</li>
  <li><code>GET /dashboard/category-breakdown</code> — Category-wise totals (Analyst, Admin)</li>
  <li><code>GET /dashboard/monthly-trends</code> — Monthly income vs expense totals (Analyst, Admin)</li>
  <li><code>GET /dashboard/recent-activity</code> — Most recent transactions, with configurable limit (Analyst, Admin)</li>
</ul>

<h2>Role Permissions</h2>

<table>
  <thead>
    <tr>
      <th>Action</th>
      <th>Viewer</th>
      <th>Analyst</th>
      <th>Admin</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>View own profile</td>
      <td>Yes</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>View transactions</td>
      <td>Yes</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>View summary</td>
      <td>Yes</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>View category breakdown</td>
      <td>No</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>View monthly trends</td>
      <td>No</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>View recent activity</td>
      <td>No</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>Create transactions</td>
      <td>No</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>Update transactions</td>
      <td>No</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>Delete transactions</td>
      <td>No</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>Manage users</td>
      <td>No</td>
      <td>No</td>
      <td>Yes</td>
    </tr>
  </tbody>
</table>

<h2>Validation Rules</h2>
<ul>
  <li><code>amount</code> must be greater than zero.</li>
  <li><code>type</code> must be either <code>income</code> or <code>expense</code>.</li>
  <li>Invalid payloads return <code>422 Unprocessable Entity</code>.</li>
  <li>Bad login or invalid token returns <code>401 Unauthorized</code>.</li>
  <li>Authenticated but unauthorized role access returns <code>403 Forbidden</code>.</li>
  <li>Inactive accounts are blocked from protected endpoints.</li>
  <li>Missing records return <code>404 Not Found</code>.</li>
  <li>Duplicate username or email returns <code>409 Conflict</code>.</li>
</ul>

<h2>Notes</h2>
<ul>
  <li>This project does not include a frontend dashboard UI.</li>
  <li>The dashboard endpoints return JSON data.</li>
  <li>Swagger is the easiest way to test login, access control, and endpoint behavior.</li>
  <li>SQLite is used for local simplicity and evaluation convenience.</li>
</ul>

<h2>What I Would Improve With More Time</h2>
<ul>
  <li>Move secret key and config into environment variables.</li>
  <li>Add refresh tokens.</li>
  <li>Add soft delete support.</li>
  <li>Add unit tests with pytest.</li>
  <li>Add rate limiting on the login endpoint.</li>
  <li>Add a minimal frontend or template-based dashboard.</li>
</ul>

<h2>Repository Notes</h2>
<p>
  This repository is intended to demonstrate backend design, access control, API structure,
  and business logic clearly rather than build a production-ready finance platform.
  The implementation favors simplicity, readability, and direct evaluation.
</p>