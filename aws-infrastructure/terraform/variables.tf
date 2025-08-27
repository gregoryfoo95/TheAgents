variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  default     = "dev"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "theagents"
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones to use"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = "theagents.com"
}

variable "certificate_arn" {
  description = "ACM certificate ARN for SSL/TLS"
  type        = string
  default     = ""
}

variable "ecr_repository_urls" {
  description = "ECR repository URLs for container images"
  type = object({
    auth_service     = string
    property_service = string
    stock_service    = string
    api_gateway      = string
    frontend         = string
  })
  default = {
    auth_service     = ""
    property_service = ""
    stock_service    = ""
    api_gateway      = ""
    frontend         = ""
  }
}

variable "database_configs" {
  description = "Database configuration"
  type = object({
    auth_db = object({
      allocated_storage = number
      instance_class    = string
      engine_version    = string
    })
    property_db = object({
      allocated_storage = number
      instance_class    = string
      engine_version    = string
    })
    stock_db = object({
      allocated_storage = number
      instance_class    = string
      engine_version    = string
    })
  })
  default = {
    auth_db = {
      allocated_storage = 20
      instance_class    = "db.t3.micro"
      engine_version    = "15.4"
    }
    property_db = {
      allocated_storage = 20
      instance_class    = "db.t3.micro"
      engine_version    = "15.4"
    }
    stock_db = {
      allocated_storage = 20
      instance_class    = "db.t3.micro"
      engine_version    = "15.4"
    }
  }
}

variable "redis_node_type" {
  description = "ElastiCache Redis node type"
  type        = string
  default     = "cache.t3.micro"
}

variable "ecs_task_cpu" {
  description = "CPU units for ECS tasks"
  type        = number
  default     = 256
}

variable "ecs_task_memory" {
  description = "Memory for ECS tasks"
  type        = number
  default     = 512
}

variable "enable_logs" {
  description = "Enable CloudWatch logs"
  type        = bool
  default     = true
}