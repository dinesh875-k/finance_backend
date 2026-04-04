<h1>Finance Dashboard API</h1>

<p>
  A backend API for managing financial records with role-based access control,
  built as part of the Zorvyn Backend Intern assessment.
</p>

<h2>Tech Choices and Assumptions</h2>
<ul>
  <li>
    <strong>FastAPI</strong> — I used FastAPI because it is the Python backend framework I work with most often.
    It let me build the project quickly while keeping the structure clean and easy to review.
  </li>
  <li>
    <strong>SQLite</strong> — I chose SQLite so the project can be cloned and run without any extra database setup.
    Since the app uses SQLAlchemy, switching to PostgreSQL later only requires changing the database URL.
  </li>
  <li>
    <strong>JWT Authentication</strong> — Authentication is handled with JWT tokens that expire after 30 minutes.
    For a production version, I would extend this with refresh tokens and stronger session handling.
  </li>
  <li>
    <strong>Free-text Categories</strong> — Categories are intentionally flexible instead of being limited to a fixed enum.
    That keeps the API closer to how finance tools are usually used in practice.
  </li>
</ul>

<h2>Quick Start</h2>

<pre><code>git clone &lt;your-repo-url&gt;
cd finance-backend
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload</code></pre>

<p><strong>API Docs:</strong> <code>http://127.0.0.1:8000/docs</code></p>

<h2>Test Credentials</h2>

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
      <td>analyst</td>
      <td>analyst123</td>
    </tr>
    <tr>
      <td>Viewer</td>
      <td>viewer</td>
      <td>viewer123</td>
    </tr>
  </tbody>
</table>

<h2>API Overview</h2>

<h3>Authentication</h3>
<ul>
  <li><code>POST /users/login</code> — Get JWT token</li>
  <li><code>POST /users/register</code> — Create user (Admin only)</li>
  <li><code>GET /users/me</code> — View own profile</li>
</ul>

<h3>Transactions</h3>
<ul>
  <li><code>POST /transactions/</code> — Create record (Admin only)</li>
  <li><code>GET /transactions/</code> — List records with filters:
    <code>category</code>, <code>type</code>, <code>start_date</code>, <code>end_date</code>,
    <code>limit</code>, <code>offset</code>
  </li>
  <li><code>GET /transactions/{id}</code> — Get single record</li>
  <li><code>PUT /transactions/{id}</code> — Update record (Admin only)</li>
  <li><code>DELETE /transactions/{id}</code> — Delete record (Admin only)</li>
</ul>

<h3>Dashboard</h3>
<ul>
  <li><code>GET /dashboard/summary</code> — Total income, expenses, and net balance</li>
  <li><code>GET /dashboard/category-breakdown</code> — Category-wise totals (Analyst, Admin)</li>
  <li><code>GET /dashboard/monthly-trends</code> — Monthly income vs expense (Analyst, Admin)</li>
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
      <td>View summary</td>
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
      <td>Category breakdown</td>
      <td>No</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>Monthly trends</td>
      <td>No</td>
      <td>Yes</td>
      <td>Yes</td>
    </tr>
    <tr>
      <td>Create/Edit/Delete</td>
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

<h2>What I Would Add With More Time</h2>
<ul>
  <li>Refresh tokens for a better authentication flow</li>
  <li>Soft delete instead of hard delete</li>
  <li>Unit tests with pytest</li>
  <li>Rate limiting on the login endpoint</li>
  <li>Environment-based configuration for dev, staging, and production</li>
</ul>
