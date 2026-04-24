output "public_ip" {
  description = "Public IP address of the Vetta EC2 instance"
  value       = aws_eip.vetta_eip.public_ip
}
