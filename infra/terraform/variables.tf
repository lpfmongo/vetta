variable "security_group" {
  default     = []
  description = "Vetta Server Security Group"
  nullable    = false
  type        = set(string)
}

variable "instance_type" {
  default     = ""
  description = "Vetta Server EC2 Instance Type (Nvidia GPU enabled)"
  nullable    = false
}

variable "ec2_kp_name" {
  default     = ""
  description = "EC2 key pair name"
  nullable    = false
}
