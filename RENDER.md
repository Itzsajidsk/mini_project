Deploying your Flask app to Render

This guide covers two options to deploy your Flask app to Render.com:
- Option A (recommended): Deploy using Docker (we include a Dockerfile).
- Option B: Deploy using Render's Python environment (no Docker).

Pre-reqs
- A Render account (https://render.com)
- Your project pushed to a GitHub/GitLab repo
- A running MySQL database accessible from Render (you can use Render's managed Postgres but this app uses MySQL; Render's managed MySQL is in beta — alternatively use ClearDB, PlanetScale, or an external MySQL instance)

Environment variables
Set these in the Render service settings (Environment -> Environment Variables):
- MYSQL_HOST (e.g. your-db-host)
- MYSQL_USER (e.g. root)
- MYSQL_PASSWORD
- MYSQL_DB (flames_login)
- SECRET_KEY (a long random string)

Option A — Docker (recommended)
1. Make sure your repository contains the Dockerfile in the project root (this repo includes one).
2. In Render, create a new Web Service and choose "Docker" as the environment.
3. Connect the repo and select the branch.
4. Configure the Service:
   - Name: flames-login (or whatever you prefer)
   - Region: pick one
   - Plan: Free/Starter/Pro depending on needs
   - Environment: Docker
   - Set Environment Variables (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, SECRET_KEY)
5. Click Create and wait for the build. Render will build the Docker image and run the container.
6. Open the live URL and test.

Option B — Native Python (no Docker)
1. Create a Web Service on Render and select the repo/branch.
2. Set the Start Command to:
   gunicorn -b 0.0.0.0:$PORT app:app
3. Under Environment, set the required environment variables (MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, SECRET_KEY).
4. Set Build Command (if required): pip install -r requirements.txt
5. Create the Service.

Database notes
- The app depends on MySQL. Ensure the Render service can reach the MySQL host and port.
- If you use an external MySQL provider, whitelist Render's outbound IPs or use a managed DB in the same cloud region.

Testing and verifying
- Deploy and open the web URL.
- Register a user, login, and try the FLAMES flow.
- Verify rows by connecting to the DB and running:
  SELECT id, username, name1, name2, created_at FROM relationships ORDER BY id DESC LIMIT 20;

Troubleshooting
- If mysqlclient installation fails in Docker: the Dockerfile installs libmysqlclient-dev; you can also switch to PyMySQL and change the code to use it.
- If you need me to switch the project to use PyMySQL (pure-Python) to avoid compiling native libs on Render, tell me and I will update `app.py` and `requirements.txt` accordingly.

Questions?
Reply and I can:
- Add Render-specific health checks or a Procfile
- Switch to PyMySQL for easier deployment
- Add a small script to create the `flames_login` DB automatically (not recommended for production)