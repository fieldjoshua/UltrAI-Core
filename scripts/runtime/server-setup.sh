#!/bin/bash
# Complete Ultra MVP Server Setup Script

echo "🚀 Ultra MVP Server Setup"
echo "========================"

# Update system
echo "📦 Updating system packages..."
apt update && apt upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com | sh

# Install Docker Compose
echo "🐳 Installing Docker Compose..."
apt-get install -y docker-compose-plugin

# Install other useful tools
echo "🛠️  Installing utilities..."
apt-get install -y git curl wget nano ufw

# Set up firewall
echo "🔥 Configuring firewall..."
ufw allow 22   # SSH
ufw allow 80   # HTTP
ufw allow 443  # HTTPS
ufw allow 8000 # API (temporary)
ufw --force enable

# Create application directory
echo "📁 Creating application directory..."
mkdir -p /opt/ultra
cd /opt/ultra

# Clone repository
echo "📥 Cloning repository..."
git clone https://github.com/fieldjoshua/Ultra.git
cd Ultra

# Make scripts executable
chmod +x deploy.sh

echo "✅ Server setup complete!"
echo ""
echo "Next steps:"
echo "1. Copy your .env.production file to /opt/ultra/Ultra/"
echo "2. Run: cd /opt/ultra/Ultra && ./deploy.sh"
echo "3. Configure your DNS to point to this server"
echo ""
echo "Your server IP: $(curl -s ifconfig.me)"