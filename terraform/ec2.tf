# Get the latest Amazon Linux 2023 AMI
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# User data script to setup the application
locals {
  user_data = <<-EOF
#!/bin/bash
set -e

# Log everything
exec > >(tee /var/log/user-data.log)
exec 2>&1

echo "Starting deployment at $(date)"

# Update system
echo "Updating system..."
yum update -y

# Install Python 3.11 and development tools
echo "Installing Python 3.11 and dependencies..."
yum install -y python3.11 python3.11-pip git gcc python3.11-devel

# Create app directory
echo "Creating application directory..."
mkdir -p /opt/sentiment-api
cd /opt/sentiment-api

# Clone the repository
echo "Cloning repository..."
git clone ${var.github_repo} .

# Create virtual environment
echo "Creating virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file with sensitive variables
echo "Creating .env file..."
cat > /opt/sentiment-api/.env << 'ENVEOF'
MONGODB_URI=${var.mongodb_uri}
DATABASE_NAME=${var.database_name}
DB_PORT=${var.db_port}
ENVEOF

# Set proper permissions
chmod 600 /opt/sentiment-api/.env

# Create systemd service file
echo "Creating systemd service..."
cat > /etc/systemd/system/sentiment-api.service << 'SERVICEEOF'
[Unit]
Description=Sentiment Market API
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/opt/sentiment-api
Environment="PATH=/opt/sentiment-api/venv/bin"
ExecStart=/opt/sentiment-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port ${var.app_port}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
SERVICEEOF

# Change ownership to ec2-user
echo "Setting permissions..."
chown -R ec2-user:ec2-user /opt/sentiment-api

# Reload systemd, enable and start service
echo "Starting service..."
systemctl daemon-reload
systemctl enable sentiment-api
systemctl start sentiment-api

# Wait for service to start
sleep 10

# Check service status
echo "Service status:"
systemctl status sentiment-api

echo "Deployment completed successfully at $(date)!"
EOF
}

# EC2 Instance
resource "aws_instance" "sentiment_api" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  
  subnet_id              = var.subnet_id
  vpc_security_group_ids = [var.security_group_id]
  key_name              = var.key_name
  
  user_data = local.user_data
  
  # Ensure we replace the instance if user_data changes
  user_data_replace_on_change = true
  
  root_block_device {
    volume_size = 30
    volume_type = "gp3"
    encrypted   = true
    
    tags = {
      Name = "${var.instance_name}-root-volume"
    }
  }
  
  tags = {
    Name        = var.instance_name
    Environment = "production"
    Application = "sentiment-api"
    ManagedBy   = "Terraform"
  }
  
  lifecycle {
    create_before_destroy = true
  }
}

# CloudWatch Log Group for the application
resource "aws_cloudwatch_log_group" "sentiment_api" {
  name              = "/aws/ec2/${var.instance_name}"
  retention_in_days = 7
  
  tags = {
    Name        = "${var.instance_name}-logs"
    Environment = "production"
    Application = "sentiment-api"
  }
}
