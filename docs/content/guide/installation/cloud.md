# Cloud Deployment (EC2 / Terraform)

This page covers running Vetta on a remote Linux instance. GPU instances (e.g., `g6.xlarge`) are recommended for faster
Whisper inference.

## Manual EC2 Setup

1. Launch an Ubuntu 24.04+ instance (at least 8 GB RAM, 30 GB disk).
2. SSH into the instance and clone the repository:
    ```bash
    git clone https://github.com/lnivva/vetta
    cd vetta
    ```
3. Run the init script to install all system dependencies (Rust, uv, protoc, ffmpeg, NVIDIA drivers):
   ```bash
   chmod +x infra/ec2/init.sh
   sudo ./infra/ec2/init.sh
   ```
4. Reboot the instance for NVIDIA drivers to take effect:
   ```bash
   sudo reboot
   ```
5. After reconnecting, verify the setup:
   ```bash
   rustc --version
   uv --version
   protoc --version
   ffmpeg -version
   nvidia-smi        # Should show your GPU if on a GPU instance
   ```

## Terraform

A reference Terraform module is provided in `infra/terraform/`. The module assumes you have already created a **VPC**
with a specifically tagged public subnet, a **security group**, and an **EC2 key pair**. It provisions the EC2 instance
and attaches the init script as user data.

The init script that runs on first boot handles system dependencies including NVIDIA drivers, Rust, uv, protoc, and
ffmpeg, so you can skip the manual Linux installation steps above.

### Prerequisites

| Resource       | Why                      | Notes                                                                   |
|----------------|--------------------------|-------------------------------------------------------------------------|
| VPC + Subnet   | Network for the instance | Public subnet tagged `<your-subnet-tag>` with internet gateway          |
| Security Group | Firewall rules           | Allow inbound SSH (port 22) from your IP at minimum                     |
| EC2 Key Pair   | SSH access               | Create in the AWS console or with `aws ec2 create-key-pair`             |
| AWS Profile    | Authentication           | A profile named `<your-aws-profile>` configured in your AWS credentials |

### Variables

| Variable         | Description                                | Example                        |
|------------------|--------------------------------------------|--------------------------------|
| `instance_type`  | EC2 instance type (NVIDIA GPU recommended) | `g6.xlarge`                    |
| `security_group` | Set of security group IDs to attach        | `["<your-security-group-id>"]` |
| `ec2_kp_name`    | Name of an existing EC2 key pair           | `<your-key-pair-name>`         |

### Deploy

```bash
cd infra/terraform
terraform init
terraform apply \
  -var='instance_type=g6.xlarge' \
  -var='security_group=["<your-security-group-id>"]' \
  -var='ec2_kp_name=<your-key-pair-name>'
```

Or create a `terraform.tfvars` file to avoid passing flags every time:

```hcl
# infra/terraform/terraform.tfvars

instance_type = "g6.xlarge"
security_group = ["<your-security-group-id>"]
ec2_kp_name   = "<your-key-pair-name>"
```

```bash
cd infra/terraform
terraform init
terraform apply
```

::: tip
The module does not output the public IP directly. After `terraform apply`, retrieve it with:

```bash
aws ec2 describe-instances \
  --filters "Name=tag:Name,Values=vetta-server-1" \
  --query "Reservations[].Instances[].PublicIpAddress" \
  --output text --profile <your-aws-profile>
```

Then SSH in:

```bash
ssh -i ~/.ssh/<your-key-pair-name>.pem ubuntu@<public-ip>
```

The init script may take several minutes to complete on first boot (driver installation, package downloads). You can
monitor progress with:

```bash
tail -f /var/log/cloud-init-output.log
```

Check Cloud Init status:

```bash
cloud-init status
```

:::

::: warning
`/etc/environment` is readable by all users on the instance. For production deployments, prefer injecting secrets
through **AWS Secrets Manager**, **SSM Parameter Store**, or your CI/CD pipeline rather than writing credentials to
disk.
:::