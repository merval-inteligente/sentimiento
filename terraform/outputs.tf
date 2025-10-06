output "instance_id" {
  description = "ID of the EC2 instance"
  value       = aws_instance.sentiment_api.id
}

output "instance_public_ip" {
  description = "Public IP address of the EC2 instance"
  value       = aws_instance.sentiment_api.public_ip
}

output "instance_public_dns" {
  description = "Public DNS name of the EC2 instance"
  value       = aws_instance.sentiment_api.public_dns
}

output "api_url" {
  description = "URL to access the API"
  value       = "http://${aws_instance.sentiment_api.public_ip}:${var.app_port}"
}

output "api_docs_url" {
  description = "URL to access the API documentation (Swagger UI)"
  value       = "http://${aws_instance.sentiment_api.public_ip}:${var.app_port}/docs"
}

output "ssh_command" {
  description = "SSH command to connect to the instance"
  value       = "ssh -i ~/.ssh/${var.key_name}.pem ec2-user@${aws_instance.sentiment_api.public_ip}"
}
