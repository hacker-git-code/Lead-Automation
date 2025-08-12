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
   cp backend/.env.example backend/.env
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
   cp backend/.env.example backend/.env
   nano backend/.env  # Edit your environment variables
   ```

### 3. Domain Setup with Nginx

1. **Create a docker-compose.prod.yml file**
   ```yaml
   version: '3'
   services:
     backend:
       build: ./backend
       restart: always
       env_file: ./backend/.env
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
