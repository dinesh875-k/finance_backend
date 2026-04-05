<h1>Finance Dashboard API</h1>

<p>
  A backend API for managing financial records with role-based access control,
  built as part of the Zorvyn Backend Intern assessment.
</p>

<h2>Project Status</h2>
<ul>
  <li>Database seeding is working.</li>
  <li>JWT login is working from Swagger UI.</li>
  <li>Role-based access control is working for Admin, Analyst, and Viewer roles.</li>
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
    <strong>JWT Authentication</strong> — Authentication uses JWT access tokens. For this assignment,
    I kept the flow simple and practical. In a production version, I would extend this with refresh tokens and better token lifecycle handling.
  </li>
  <li>
    <strong>Flexible Categories</strong> — Transaction categories are stored as free text instead of a strict enum,
    because finance tools usually need flexibility for user-defined categories.
  </li>
</ul>

<h2>Quick Start</h2>

<pre><code>git clone &lt;your-repo-url&gt;
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

<h2>How Authentication Works in Swagger</h2>
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
  <li>A <code>422 Unprocessable Entity</code> response means the request body failed validation, not that authentication failed.</li>
  <li>A <code>401 Unauthorized</code> response means login or token authentication failed.</li>
  <li>A <code>403 Forbidden</code> response means the user is authenticated but does not have permission for that action.</li>
</ul>

<h2>Notes</h2>
<ul>
  <li>This project does not include a frontend dashboard UI.</li>
  <li>The dashboard endpoints return JSON data through the API.</li>
  <li>Swagger is the easiest way to test authentication and role-based access for this project.</li>
</ul>

<h2>What I Would Improve With More Time</h2>
<ul>
  <li>Add refresh tokens for a more complete authentication flow.</li>
  <li>Use soft delete instead of hard delete.</li>
  <li>Add unit tests with pytest.</li>
  <li>Add rate limiting to the login endpoint.</li>
  <li>Use environment-based configuration for development, staging, and production.</li>
  <li>Add a small frontend or template-based dashboard page for visual reporting.</li>
</ul>