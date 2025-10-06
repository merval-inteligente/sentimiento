# AWS Configuration
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"  # us-east-1 (Norte de Virginia)
}

variable "vpc_id" {
  description = "VPC ID to use for the EC2 instance"
  type        = string
}

variable "subnet_id" {
  description = "Subnet ID to launch the instance in"
  type        = string
}

variable "security_group_id" {
  description = "Security Group ID to attach to the instance"
  type        = string
}

variable "key_name" {
  description = "SSH key pair name"
  type        = string
}

# Instance Configuration
variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.small"
}

variable "instance_name" {
  description = "Name tag for the EC2 instance"
  type        = string
  default     = "sentiment-api-server"
}

# Application Configuration - SENSITIVE
variable "mongodb_uri" {
  description = "MongoDB connection URI"
  type        = string
  sensitive   = true
}

variable "database_name" {
  description = "MongoDB database name"
  type        = string
  default     = "MervalDB"
  sensitive   = true
}

variable "db_port" {
  description = "Database port"
  type        = string
  default     = "27017"
  sensitive   = true
}

# Application Settings
variable "app_port" {
  description = "Port for the FastAPI application"
  type        = number
  default     = 8001
}

variable "github_repo" {
  description = "GitHub repository URL"
  type        = string
  default     = "https://github.com/merval-inteligente/sentimiento.git"
}
