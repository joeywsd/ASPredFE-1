# ASPred, Antibody Specificity Predictor. Web Front-end only.

ASPred (Antibody Specificity Predictor) is an innovative computational strategy developed to predict antigen-specific B-cell receptors (BCRs)

## Features

- User registration with email verification
- reCAPTCHA protection for registration
- One sequence submission per day limit
- Sequence validation (amino acids only, max 130 length)
- Results tracking and viewing

## Development Setup

1. Create a conda environment:
```bash
conda create -n aspred python=3.11
conda activate aspred
```

2. Install dependencies and Configuring database and paths:
```bash
pip install -r requirements.txt
conda install -c conda-forge mysql-connector-python
curl -LsSf https://astral.sh/uv/install.sh | sh

# mySQL server part
# Install mysql (from website for windows)
# Change env.example to .env
# Configure database in .env to match aspredwrapper.py's database_config
# Configure database in new file settings_local.py to match aspredwrapper.py's database_config
# Do not change aspredwrapper.py's aspredwrapper database_config
# Make sure to load environment variables from the correct environment file in aspredwrapper.py
# i.e. load_dotenv(dotenv_path="../local.env") for local development
# Change paths as necessary for the models in aspredwrapper.py
```

3. Apply migrations and add models:
```bash
python manage.py makemigrations --settings=labsite.settings_local
python manage.py migrate --settings=labsite.settings_local
# Configure protein_models.json.example with prediction_models
python manage.py add_or_update_prediction_models --settings=labsite.settings_local
```

4. Run development server:
```bash
python manage.py runserver --settings=labsite.settings_local
```

5. Run wrapper:
```bash
uv run aspredwrapper.py
```
6. To send email notifications:
```bash
python manage.py send_notifications --settings=labsite.settings_local
```

## Production Deployment

1. Clone the repository to your production server

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `env.prod.example`:
```bash
cp env.prod.example .env
```

4. Edit the `.env` file with your production settings:
- Generate a new Django secret key
- Configure your MySQL database credentials
- Set up your email backend credentials
- Add your reCAPTCHA keys (get them from Google reCAPTCHA)

5. Create required directories:
```bash
mkdir logs
mkdir staticfiles
```

6. Collect static files:
```bash
python manage.py collectstatic --settings=labsite.settings_prod
```

7. Apply migrations:
```bash
python manage.py migrate --settings=labsite.settings_prod
```

8. Set up Gunicorn:
Create a systemd service file (e.g., `/etc/systemd/system/labsite.service`):
```ini
[Unit]
Description=Laboratory Sequence Analyzer
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/your/project
Environment="PATH=/path/to/your/virtualenv/bin"
EnvironmentFile=/path/to/your/project/.env
ExecStart=/path/to/your/virtualenv/bin/gunicorn --workers 3 --bind unix:/run/labsite.sock labsite.wsgi:application

[Install]
WantedBy=multi-user.target
```

9. Set up Nginx:
Create a Nginx configuration file (e.g., `/etc/nginx/sites-available/labsite`):
```nginx
server {
    listen 80;
    server_name yourwebsite.com www.yourwebsite.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourwebsite.com www.yourwebsite.com;

    ssl_certificate /path/to/your/certificate.pem;
    ssl_certificate_key /path/to/your/private.key;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /path/to/your/project;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/run/labsite.sock;
    }
}
```

10. Start services:
```bash
sudo systemctl start labsite
sudo systemctl enable labsite
sudo systemctl restart nginx
```

## Security Notes

- Always use HTTPS in production
- Keep your `.env` file secure and never commit it to version control
- Regularly update dependencies
- Monitor logs for any security issues
- Back up your database regularly
