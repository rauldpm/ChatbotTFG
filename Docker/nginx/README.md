
Instalar certbot/letsencrypt

sudo apt install software-properties-common
sudo add-apt-repository ppa:certbot/certbot
sudo apt-get update
sudo apt-get install python-certbot-nginx

https://github.com/vinyll/certbot-install#how-to-install

sudo nano /etc/nginx/sites-available/default
  server_name example.com www.example.com;
sudo systemctl reload nginx

sudo certbot --nginx -d example.com -d www.example.com