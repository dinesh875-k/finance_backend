<h1>Finance Dashboard API</h1>

<p>
  A backend API for managing financial records with role-based access control,
  built for the Zorvyn Backend Intern assessment.
</p>

<h2>Project Summary</h2>
<p>
  This project is a backend-only finance dashboard system. It focuses on API design,
  financial record management, validation, access control, and summary analytics.
  The goal was to build a clean and maintainable backend that can later serve a frontend dashboard if needed.
</p>

<h2>Current Status</h2>
<p>Implemented and working:</p>
<ul>
  <li>User registration and login</li>
  <li>JWT-based authentication</li>
  <li>Role-based access control for Viewer, Analyst, and Admin</li>
  <li>Financial transaction CRUD</li>
  <li>Transaction filtering by category, type, and date range</li>
  <li>Dashboard summary APIs</li>
  <li>Category-wise analytics</li>
  <li>Monthly trends</li>
  <li>Swagger API documentation</li>
  <li>SQLite-based local persistence</li>
  <li>Seed script for local testing</li>
</ul>

<p>Planned next improvements:</p>
<ul>
  <li>Admin user-management endpoints</li>
  <li>Recent activity dashboard endpoint</li>
  <li>Environment-based configuration</li>
  <li>Better seed idempotency</li>
  <li>Tests</li>
</ul>

<h2>Tech Choices and Assumptions</h2>

<h3>FastAPI</h3>
<p>
  I used FastAPI because it is the Python backend framework I am most comfortable with,
  and it makes it easy to build structured APIs quickly.
</p>

<h3>SQLite</h3>
<p>
  I chose SQLite to keep setup simple for evaluation. The project can be cloned and run locally
  without Docker or separate database setup. Since SQLAlchemy is used, the database layer can be
  switched later with minimal changes.
</p>

<h3>JWT Authentication</h3>
<p>
  Authentication is handled with JWT access tokens. For this assessment, I kept the auth flow
  intentionally simple. In a production version, I would add refresh tokens and stronger
  token/session management.
</p>

<h3>Flexible Categories</h3>
<p>
  Transaction categories are stored as free text rather than a fixed enum. That keeps the API
  more practical for real finance use cases where categories may vary across users.
</p>

<h2>Assignment Mapping</h2>
<p>
  This project currently covers the following core areas from the assignment:
</p>
<ul>
  <li>User creation and role-based restriction</li>
  <li>Financial records CRUD</li>
  <li>Filtering by date, category, and type</li>
  <li>Dashboard summary APIs</li>
  <li>Access control enforcement by role</li>
  <li>Validation and error handling</li>
  <li>Persistent storage using SQLite</li>
</ul>

<p>
  The assignment also mentions examples like recent activity and user status management.
  Those are the next additions planned for this project.
</p>

<h2>Quick Start</h2>

<pre><code>git clone &lt;your-repo-url&gt;
cd finance_backend
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload</code></pre>

<p><strong>Swagger Docs:</strong> <code>http://127.0.0.1:8000/docs</code></p>

<h2>Seeded Test Credentials</h2>
<p>These are the credentials currently created by the seed script:</p>

<ul>
  <li>
    <strong>Admin</strong><br />
    Username: <code>admin</code><br />
    Password: <code>admin123</code>
  </li>
  <li>
    <strong>Analyst</strong><br />
    Username: <code>analyst1</code><br />
    Password: <code>123456</code>
  </li>
  <li>
    <strong>Viewer</strong><br />
    Username: <code>viewer1</code><br />
    Password: <code>123456</code>
  </li>
</ul>

<h2>Authentication in Swagger</h2>
<ol>
  <li>Open <code>/docs</code></li>
  <li>Click <strong>Authorize</strong></li>
  <li>Enter one of the seeded usernames and passwords</li>
  <li><code>client_id</code> and <code>client_secret</code> are not required</li>
</ol>

<h2>API Overview</h2>

<h3>Authentication</h3>
<ul>
  <li><code>POST /users/login</code> — Authenticate and receive JWT token</li>
  <li><code>POST /users/register</code> — Create a new user, admin only</li>
  <li><code>GET /users/me</code> — Fetch the current authenticated user's profile</li>
</ul>

<h3>Transactions</h3>
<ul>
  <li><code>POST /transactions/</code> — Create a transaction, admin only</li>
  <li><code>GET /transactions/</code> — List transactions with filters</li>
  <li><code>GET /transactions/{id}</code> — Get one transaction by id</li>
  <li><code>PUT /transactions/{id}</code> — Update a transaction, admin only</li>
  <li><code>DELETE /transactions/{id}</code> — Delete a transaction, admin only</li>
</ul>

<p>Supported filters on transaction listing:</p>
<ul>
  <li><code>category</code></li>
  <li><code>type</code></li>
  <li><code>start_date</code></li>
  <li><code>end_date</code></li>
  <li><code>limit</code></li>
  <li><code>offset</code></li>
</ul>

<h3>Dashboard</h3>
<ul>
  <li><code>GET /dashboard/summary</code> — Total income, total expenses, net balance, transaction count</li>
  <li><code>GET /dashboard/category-breakdown</code> — Category totals, analyst and admin only</li>
  <li><code>GET /dashboard/monthly-trends</code> — Monthly totals grouped by type, analyst and admin only</li>
</ul>

<h2>Role Permissions</h2>

<h3>Viewer</h3>
<p>Can:</p>
<ul>
  <li>View own profile</li>
  <li>View transactions</li>
  <li>View dashboard summary</li>
</ul>
<p>Cannot:</p>
<ul>
  <li>Create transactions</li>
  <li>Update transactions</li>
  <li>Delete transactions</li>
  <li>Access category breakdown</li>
  <li>Access monthly trends</li>
  <li>Manage users</li>
</ul>

<h3>Analyst</h3>
<p>Can:</p>
<ul>
  <li>View own profile</li>
  <li>View transactions</li>
  <li>View dashboard summary</li>
  <li>View category breakdown</li>
  <li>View monthly trends</li>
</ul>
<p>Cannot:</p>
<ul>
  <li>Create transactions</li>
  <li>Update transactions</li>
  <li>Delete transactions</li>
  <li>Manage users</li>
</ul>

<h3>Admin</h3>
<p>Can:</p>
<ul>
  <li>Access all user endpoints</li>
  <li>Create, update, and delete transactions</li>
  <li>Access all dashboard endpoints</li>
  <li>Create users</li>
</ul>

<h2>Validation Rules</h2>
<ul>
  <li><code>amount</code> must be greater than zero</li>
  <li><code>type</code> must be either <code>income</code> or <code>expense</code></li>
  <li>Invalid payloads return <code>422 Unprocessable Entity</code></li>
  <li>Bad login or invalid token returns <code>401 Unauthorized</code></li>
  <li>Authenticated but unauthorized role access returns <code>403 Forbidden</code></li>
  <li>Missing records return <code>404 Not Found</code></li>
  <li>Duplicate username or email returns <code>409 Conflict</code></li>
</ul>

<h2>Notes</h2>
<ul>
  <li>This project does not include a frontend dashboard UI</li>
  <li>The dashboard endpoints return JSON data</li>
  <li>Swagger is the easiest way to test login, access control, and endpoint behavior</li>
  <li>SQLite is used for local simplicity and evaluation convenience</li>
</ul>

<h2>Known Gaps / Next Additions</h2>
<p>To align more closely with the assignment, the next items to add are:</p>
<ul>
  <li><code>GET /users/</code> for admin user listing</li>
  <li>User role update endpoint</li>
  <li>Activate/deactivate user endpoint</li>
  <li><code>GET /dashboard/recent-activity</code></li>
</ul>

<h2>What I Would Improve With More Time</h2>
<ul>
  <li>Move secret key and config into environment variables</li>
  <li>Add refresh tokens</li>
  <li>Add soft delete support</li>
  <li>Make the seed script fully idempotent</li>
  <li>Add unit tests with pytest</li>
  <li>Add rate limiting on the login endpoint</li>
  <li>Add stronger email validation</li>
  <li>Add a minimal frontend or template-based dashboard</li>
</ul>

<h2>Repository Notes</h2>
<p>
  This repository is intended to demonstrate backend design, access control, API structure,
  and business logic clearly rather than build a production-ready finance platform.
  The implementation favors simplicity, readability, and direct evaluation.
</p>