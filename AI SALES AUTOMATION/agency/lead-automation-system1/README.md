# Lead Automation System

A comprehensive system for automating lead generation, outreach, and sales processes.

## Table of Contents
- [Features](#features)
- [Technical Stack](#technical-stack)
- [Local Setup](#local-setup)
- [Domain Deployment](#domain-deployment)
- [Supabase Integration](#supabase-integration)
- [Admin Dashboard](#admin-dashboard)
- [Maintenance & Updates](#maintenance--updates)

## Features

### 1. Lead Generation from Apollo.io
- Search and enrich leads from Apollo.io API
- Target business owners in U.S. (digital agencies, coaches, SaaS founders)
- Target business owners in India (startups, small businesses, agencies)
- Filter based on industry, revenue, and location
- Store results in Google Sheets (no API required)

### 2. Automated Email Outreach
- Connect Gmail for India leads and Outlook for U.S. leads
- Send personalized emails with the lead's first name & business type
- Follow up every 3 days (max 4 times)
- Stop emails when the lead replies or books a call

### 3. Lead Engagement Handling
- Options for sending call links or email responses
- Send Calendly link automatically when requested
- Track lead status in Google Sheets

### 4. Payment Processing
- Dynamic pricing based on lead location
  - U.S.: $2,500 - $5,000
  - India: ₹40,000 - ₹1,50,000
- Integrated payment gateways
  - Stripe for U.S. leads
  - Razorpay for India leads
- Flexible payment options

### 5. Analytics and Tracking
- Track email open rates, replies, and call bookings
- Visualize sales funnel performance
- Get suggestions to improve conversions

## Technical Stack

- **Frontend**: HTML, CSS, JavaScript (with Bootstrap and Chart.js)
- **Backend**: Python with Flask
- **Database**: Supabase (PostgreSQL)
- **Authentication**: Supabase Auth
- **Storage**: Google Sheets (for leads) and Supabase (for users/settings)
- **Email**: SMTP integration with Gmail and Outlook
- **Payments**: Stripe and Razorpay APIs
- **Deployment**: Docker with Nginx

## Local Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lead-automation-system.git
   cd lead-automation-system
   ```

2. **Set up environment variables**
   Copy the `.env.example` file to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

3. **Using Docker (recommended)**
   ```bash
   docker-compose up --build
   ```
   This will start both the backend and frontend services.

4. **Manual setup (alternative)**

   Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   python app.py
   ```

   Frontend:
   ```bash
   cd frontend
   python -m http.server 8000  # Or any static file server
   ```

5. **Access the application**
   - Open your browser and navigate to http://localhost:8000
   - The admin panel will be available at http://localhost:8000/admin (after creating an admin account)

## Domain Deployment

### 1. Server Requirements
- A VPS with at least 2GB RAM (e.g., DigitalOcean, AWS, Linode)
- Ubuntu 20.04 or later
- Docker and Docker Compose installed
- A domain name pointing to your server

### 2. Server Setup

1. **SSH into your server**
   ```bash
   ssh user@your-server-ip
   ```

2. **Install Docker and Docker Compose**
   ```bash
   # Update packages
   sudo apt update && sudo apt upgrade -y

   # Install Docker
   curl -fsSL https://get.docker.com -o get-docker.sh
   sudo sh get-docker.sh

   # Add your user to docker group
   sudo usermod -aG docker $USER

   # Install Docker Compose
   sudo apt install docker-compose -y
   ```

3. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/lead-automation-system.git
   cd lead-automation-system
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   nano .env  # Edit your environment variables
   ```

### 3. Domain Setup with Nginx

1. **Create a docker-compose.prod.yml file**
   ```yaml
   version: '3'
   services:
     backend:
       build: ./backend
       restart: always
       env_file: .env
       networks:
         - app-network

     frontend:
       build: ./frontend
       restart: always
       networks:
         - app-network

     nginx:
       image: nginx:latest
       ports:
         - "80:80"
         - "443:443"
       volumes:
         - ./nginx/conf:/etc/nginx/conf.d
         - ./certbot/conf:/etc/letsencrypt
         - ./certbot/www:/var/www/certbot
       networks:
         - app-network
       depends_on:
         - backend
         - frontend

     certbot:
       image: certbot/certbot
       volumes:
         - ./certbot/conf:/etc/letsencrypt
         - ./certbot/www:/var/www/certbot
       entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"

   networks:
     app-network:
   ```

2. **Create Nginx configuration**
   ```bash
   mkdir -p nginx/conf
   ```

   Create a file `nginx/conf/app.conf`:
   ```
   server {
       listen 80;
       server_name yourdomain.com www.yourdomain.com;

       location /.well-known/acme-challenge/ {
           root /var/www/certbot;
       }

       location / {
           return 301 https://$host$request_uri;
       }
   }

   server {
       listen 443 ssl;
       server_name yourdomain.com www.yourdomain.com;

       ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
       ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

       location / {
           proxy_pass http://frontend;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }

       location /api {
           proxy_pass http://backend:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Initialize SSL certificates**
   ```bash
   mkdir -p certbot/conf certbot/www

   # Start nginx
   docker-compose -f docker-compose.prod.yml up -d nginx

   # Get SSL certificate
   docker-compose -f docker-compose.prod.yml run --rm certbot certonly --webroot --webroot-path=/var/www/certbot --email your-email@example.com --agree-tos --no-eff-email -d yourdomain.com -d www.yourdomain.com

   # Restart nginx to load the certificates
   docker-compose -f docker-compose.prod.yml restart nginx
   ```

4. **Start the full application**
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```

### 4. Setting Up Continuous Deployment (Optional)

1. **Create a deployment script**
   Create a file named `deploy.sh`:
   ```bash
   #!/bin/bash

   # Pull latest changes
   git pull

   # Rebuild and restart containers
   docker-compose -f docker-compose.prod.yml down
   docker-compose -f docker-compose.prod.yml up -d --build

   echo "Deployment completed!"
   ```

   Make it executable:
   ```bash
   chmod +x deploy.sh
   ```

2. **Set up a webhook for automatic deployment**
   You can use tools like [webhook](https://github.com/adnanh/webhook) to trigger the deployment script when you push to your repository.

## Supabase Integration

### 1. Setting Up Supabase

1. **Create a Supabase account**
   - Go to [Supabase](https://supabase.com) and sign up
   - Create a new project

2. **Configure your database**

   Create the following tables:

   **Users Table**
   ```sql
   CREATE TABLE users (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     email TEXT UNIQUE NOT NULL,
     full_name TEXT,
     role TEXT DEFAULT 'user',
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     last_login TIMESTAMP WITH TIME ZONE
   );
   ```

   **Settings Table**
   ```sql
   CREATE TABLE settings (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     user_id UUID REFERENCES users(id),
     setting_key TEXT NOT NULL,
     setting_value TEXT,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     UNIQUE(user_id, setting_key)
   );
   ```

   **API Keys Table**
   ```sql
   CREATE TABLE api_keys (
     id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
     user_id UUID REFERENCES users(id),
     service_name TEXT NOT NULL,
     api_key TEXT NOT NULL,
     is_active BOOLEAN DEFAULT TRUE,
     created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
     UNIQUE(user_id, service_name)
   );
   ```

3. **Enable authentication**
   - Go to Authentication > Settings
   - Enable Email Auth

4. **Get your API keys**
   - Go to Project Settings > API
   - Copy the URL and anon key to your `.env` file:
   ```
   SUPABASE_URL=https://your-project-ref.supabase.co
   SUPABASE_KEY=your-anon-key
   ```

### 2. Integrating Supabase with Backend

1. **Install Supabase client**
   Add to `requirements.txt`:
   ```
   supabase==1.0.3
   ```

2. **Initialize Supabase in your app**
   ```python
   import os
   from supabase import create_client, Client

   supabase_url = os.environ.get("SUPABASE_URL")
   supabase_key = os.environ.get("SUPABASE_KEY")
   supabase: Client = create_client(supabase_url, supabase_key)
   ```

3. **Create authentication routes**
   ```python
   @app.route('/api/auth/signup', methods=['POST'])
   def signup():
       data = request.json
       email = data.get('email')
       password = data.get('password')
       full_name = data.get('full_name')

       try:
           # Register user with Supabase Auth
           auth_response = supabase.auth.sign_up({
               "email": email,
               "password": password
           })

           # Add user to our users table
           user_id = auth_response.user.id
           supabase.table('users').insert({
               "id": user_id,
               "email": email,
               "full_name": full_name,
               "role": "user"
           }).execute()

           return jsonify({"success": True, "message": "User registered successfully"})
       except Exception as e:
           return jsonify({"success": False, "error": str(e)}), 500

   @app.route('/api/auth/login', methods=['POST'])
   def login():
       data = request.json
       email = data.get('email')
       password = data.get('password')

       try:
           # Login with Supabase Auth
           auth_response = supabase.auth.sign_in_with_password({
               "email": email,
               "password": password
           })

           # Update last login
           user_id = auth_response.user.id
           supabase.table('users').update({
               "last_login": "now()"
           }).eq("id", user_id).execute()

           return jsonify({
               "success": True,
               "token": auth_response.session.access_token,
               "user": {
                   "id": auth_response.user.id,
                   "email": auth_response.user.email,
                   "role": get_user_role(user_id)
               }
           })
       except Exception as e:
           return jsonify({"success": False, "error": str(e)}), 401
   ```

### 3. Creating Login/Signup UI

Add these files to your frontend:

1. **login.html**
2. **signup.html**
3. **js/auth.js**

## Admin Dashboard

### 1. Admin Pages Structure

Create the following admin pages:

1. **Admin Dashboard**
   - Overview of system metrics
   - User management
   - System status

2. **Lead Management**
   - View all leads across users
   - Filter and search functionality
   - Export capabilities

3. **Email Templates**
   - Create and edit email templates
   - Test email sending

4. **Payment Settings**
   - Configure payment gateways
   - Set pricing tiers

5. **System Updates**
   - Deploy new versions
   - View logs
   - Restart services

### 2. Implementing Admin Access Control

1. **Create middleware to check admin role**
   ```python
   def admin_required(f):
       @wraps(f)
       def decorated_function(*args, **kwargs):
           token = request.headers.get('Authorization', '').replace('Bearer ', '')
           if not token:
               return jsonify({"success": False, "error": "Authentication required"}), 401

           try:
               # Verify token with Supabase
               user = supabase.auth.get_user(token)

               # Check if user is admin
               user_data = supabase.table('users').select('role').eq('id', user.id).execute()
               if not user_data.data or user_data.data[0]['role'] != 'admin':
                   return jsonify({"success": False, "error": "Admin access required"}), 403

               return f(*args, **kwargs)
           except Exception as e:
               return jsonify({"success": False, "error": str(e)}), 401
       return decorated_function
   ```

2. **Add admin-only routes**
   ```python
   @app.route('/api/admin/users', methods=['GET'])
   @admin_required
   def get_users():
       try:
           users = supabase.table('users').select('*').execute()
           return jsonify({"success": True, "data": users.data})
       except Exception as e:
           return jsonify({"success": False, "error": str(e)}), 500
   ```

### 3. Implementing Version Deployment from Admin

1. **Create a deployment endpoint**
   ```python
   @app.route('/api/admin/deploy', methods=['POST'])
   @admin_required
   def deploy_new_version():
       try:
           # Run the deployment script
           process = subprocess.Popen(['./deploy.sh'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
           stdout, stderr = process.communicate()

           if process.returncode != 0:
               return jsonify({"success": False, "error": stderr.decode()}), 500

           return jsonify({
               "success": True,
               "message": "Deployment successful",
               "details": stdout.decode()
           })
       except Exception as e:
           return jsonify({"success": False, "error": str(e)}), 500
   ```

## Maintenance & Updates

### Regular Maintenance Tasks

1. **Database Backups**
   ```bash
   # Run from your server
   cd lead-automation-system
   ./scripts/backup_database.sh
   ```

2. **Log Rotation**
   ```bash
   # Configure logrotate
   sudo nano /etc/logrotate.d/lead-automation
   ```

   Add:
   ```
   /var/log/lead-automation/*.log {
     daily
     missingok
     rotate 14
     compress
     delaycompress
     notifempty
     create 640 root adm
   }
   ```

3. **Certificate Renewal**
   SSL certificates from Let's Encrypt will auto-renew through the certbot service in docker-compose.

### Updating the System

1. **Minor Updates (No Database Changes)**
   ```bash
   cd lead-automation-system
   git pull
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

2. **Major Updates (With Database Changes)**
   ```bash
   # Backup first
   ./scripts/backup_database.sh

   # Update
   git pull

   # Run migrations if needed
   docker-compose -f docker-compose.prod.yml exec backend python manage.py db upgrade

   # Restart
   docker-compose -f docker-compose.prod.yml up -d --build
   ```

## Troubleshooting

### Common Issues and Solutions

1. **API Connection Issues**
   - Check your API keys in the .env file
   - Verify network connectivity from your server

2. **Email Sending Failures**
   - Make sure SMTP credentials are correct
   - For Gmail, ensure you're using an App Password

3. **Payment Processing Issues**
   - Verify API keys for Stripe/Razorpay
   - Check webhook configurations

4. **Database Connection Problems**
   - Confirm Supabase credentials
   - Check if there are any rate limits or connection issues

5. **Docker Deployment Issues**
   - Inspect logs: `docker-compose -f docker-compose.prod.yml logs`
   - Check Docker service status: `systemctl status docker`

## Support and Resources

For additional help, contact:
- support@yourcompany.com
- Join our community on [Discord](#)

Documentation resources:
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Supabase Documentation](https://supabase.com/docs)
- [Docker Documentation](https://docs.docker.com/)
