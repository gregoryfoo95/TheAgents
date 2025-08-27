# AWS NLB Infrastructure for TheAgents

This directory contains the Terraform configuration and deployment scripts for deploying TheAgents microservice architecture on AWS using a Network Load Balancer (NLB) for optimal latency.

## Architecture Overview

The infrastructure includes:

- **Network Load Balancer (NLB)** - Layer 4 load balancing for minimal latency
- **ECS Fargate** - Container orchestration for microservices
- **RDS PostgreSQL** - Separate databases for each service
- **ElastiCache Redis** - Shared caching layer
- **Route 53** - DNS routing for subdomain-based service access
- **VPC with Multi-AZ** - High availability networking

## Performance Benefits

- **~40-60ms latency reduction** compared to API Gateway
- **Layer 4 TCP routing** without HTTP parsing overhead
- **Direct service connections** eliminating proxy bottlenecks
- **Better connection pooling** for database connections

## Prerequisites

Before deploying, ensure you have:

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0 installed
3. **Docker** for building container images
4. **jq** for JSON processing

## Quick Start

### 1. Configure Variables

Copy the example variables file:

```bash
cp terraform/terraform.tfvars.example terraform/terraform.tfvars
```

Edit `terraform/terraform.tfvars` with your values:

```hcl
aws_region     = "us-east-1"
environment    = "dev"
project_name   = "theagents"
domain_name    = "yourdomain.com"
certificate_arn = "arn:aws:acm:us-east-1:123456789012:certificate/..."
```

### 2. Deploy Infrastructure

Use the automated deployment script:

```bash
cd aws-infrastructure/scripts
./deploy.sh deploy
```

Or deploy manually:

```bash
# Create ECR repositories
./deploy.sh ecr

# Build and push images
./deploy.sh build

# Deploy infrastructure
cd ../terraform
terraform init
terraform plan
terraform apply
```

### 3. Access Services

After deployment, services will be available at:

- **Frontend**: `https://yourdomain.com`
- **Auth Service**: `https://auth.yourdomain.com`
- **Property Service**: `https://property.yourdomain.com`
- **Stock Service**: `https://stock.yourdomain.com`

## Service Routing

The NLB routes traffic based on DNS subdomains:

```
Internet → Route 53 → NLB → Target Groups → ECS Services
```

Each service runs on ECS Fargate with:
- **2 instances** for high availability
- **Health checks** on service endpoints
- **Auto-scaling** based on CPU/memory usage
- **CloudWatch logging** enabled

## Database Architecture

- **Auth DB**: PostgreSQL for user authentication
- **Property DB**: PostgreSQL for property data
- **Stock DB**: PostgreSQL for stock analysis data
- **Redis**: Shared cache for session management

All databases use:
- **Encryption at rest** and in transit
- **Multi-AZ deployment** for high availability
- **Automated backups** with 7-day retention
- **Private subnets** for security

## Monitoring & Logging

- **CloudWatch Logs** for application logs
- **ECS Container Insights** for performance metrics
- **RDS Performance Insights** for database monitoring
- **NLB Access Logs** for traffic analysis

## Security Features

- **VPC with private subnets** for services
- **Security groups** with least-privilege access
- **RDS in private subnets** with restricted access
- **Secrets management** via AWS SSM Parameter Store
- **SSL/TLS termination** at NLB level

## Cost Optimization

- **Fargate Spot** capacity for cost savings
- **t3.micro instances** for databases (adjustable)
- **GP2 storage** for databases
- **7-day backup retention** for RDS

## Deployment Commands

```bash
# Full deployment
./deploy.sh deploy

# Deploy to different environment
./deploy.sh --environment prod --region us-west-2 deploy

# Build and push images only
./deploy.sh build

# Create ECR repositories only
./deploy.sh ecr

# Show deployment info
./deploy.sh info

# Clean up all resources
./deploy.sh cleanup
```

## Customization

### Scaling Configuration

Edit `terraform/variables.tf` to adjust:

```hcl
# ECS Task resources
ecs_task_cpu    = 512  # Increase for more CPU
ecs_task_memory = 1024 # Increase for more memory

# Database instance classes
database_configs = {
  auth_db = {
    instance_class = "db.t3.small"  # Upgrade for better performance
  }
}
```

### Environment-Specific Configurations

Create separate `.tfvars` files:

```bash
# Development
terraform/dev.tfvars

# Staging  
terraform/staging.tfvars

# Production
terraform/prod.tfvars
```

### Adding Services

To add new microservices:

1. Add target group in `nlb.tf`
2. Add ECS service in `ecs.tf` 
3. Add Route 53 record for routing
4. Update security groups as needed

## Troubleshooting

### Common Issues

1. **ECR Permission Denied**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ecr-url>
   ```

2. **Service Not Healthy**
   - Check CloudWatch logs for service errors
   - Verify health check endpoints return 200
   - Check security group rules

3. **Database Connection Issues**
   - Verify database credentials in SSM Parameter Store
   - Check security group rules for database access
   - Ensure services are in correct subnets

### Useful Commands

```bash
# Check service status
aws ecs describe-services --cluster theagents-dev-cluster --services theagents-dev-auth

# View service logs
aws logs tail /ecs/theagents-dev-auth --follow

# Check NLB targets
aws elbv2 describe-target-health --target-group-arn <target-group-arn>
```

## Migration from API Gateway

To migrate from your current API Gateway setup:

1. Deploy this NLB infrastructure in parallel
2. Test services via NLB endpoints
3. Update DNS to point to NLB
4. Keep API Gateway for development/testing
5. Monitor performance improvements

## Support

For issues or questions:
1. Check CloudWatch logs for service errors
2. Review Terraform outputs for resource information
3. Use AWS Console to inspect ECS services and NLB health