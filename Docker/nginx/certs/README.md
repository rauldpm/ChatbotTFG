### Place here the following files generated with certbot and letsencrypt

- fullchain.pem
- privkey.pem

### How to generate the pem files:

#### Install certbot/letsencrypt

- sudo apt install software-properties-common
- sudo add-apt-repository ppa:certbot/certbot
- sudo apt-get update
- sudo apt-get install python-certbot-nginx

If the apt install commands does not work, install certbot from this GitHub repository:

- https://github.com/vinyll/certbot-install#how-to-install

#### Install nginx

- sudo apt instal nginx
- sudo systemctl start nginx

#### Configure nginx to create the pem files

Edit the nginx default available site /etc/nginx/sites-available/default:

  server_name example.com www.example.com;

Reload nginx:

- sudo systemctl reload nginx

Generate certificates

- sudo certbot --nginx -d yourdomain -d www.yourdomain