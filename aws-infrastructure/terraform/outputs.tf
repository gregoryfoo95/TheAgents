output "vpc_id" {
  description = "ID of the VPC"
  value       = aws_vpc.main.id
}

output "vpc_cidr_block" {
  description = "CIDR block of the VPC"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "IDs of the public subnets"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "IDs of the private subnets"
  value       = aws_subnet.private[*].id
}

output "database_subnet_ids" {
  description = "IDs of the database subnets"
  value       = aws_subnet.database[*].id
}

output "nlb_dns_name" {
  description = "DNS name of the Network Load Balancer"
  value       = aws_lb.nlb.dns_name
}

output "nlb_zone_id" {
  description = "Zone ID of the Network Load Balancer"
  value       = aws_lb.nlb.zone_id
}

output "nlb_arn" {
  description = "ARN of the Network Load Balancer"
  value       = aws_lb.nlb.arn
}

output "ecs_cluster_name" {
  description = "Name of the ECS cluster"
  value       = aws_ecs_cluster.main.name
}

output "ecs_cluster_id" {
  description = "ID of the ECS cluster"
  value       = aws_ecs_cluster.main.id
}

output "auth_db_endpoint" {
  description = "RDS auth database endpoint"
  value       = aws_db_instance.auth.endpoint
  sensitive   = true
}

output "property_db_endpoint" {
  description = "RDS property database endpoint"
  value       = aws_db_instance.property.endpoint
  sensitive   = true
}

output "stock_db_endpoint" {
  description = "RDS stock database endpoint"
  value       = aws_db_instance.stock.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_replication_group.main.primary_endpoint_address
  sensitive   = true
}

output "target_group_arns" {
  description = "ARNs of the target groups"
  value = {
    auth_service     = aws_lb_target_group.auth_service.arn
    property_service = aws_lb_target_group.property_service.arn
    stock_service    = aws_lb_target_group.stock_service.arn
    frontend         = aws_lb_target_group.frontend.arn
  }
}

output "route53_zone_id" {
  description = "Route53 hosted zone ID"
  value       = var.domain_name != "" ? aws_route53_zone.main[0].zone_id : null
}

output "route53_name_servers" {
  description = "Route53 name servers"
  value       = var.domain_name != "" ? aws_route53_zone.main[0].name_servers : null
}

output "security_group_ids" {
  description = "Security group IDs"
  value = {
    nlb        = aws_security_group.nlb.id
    ecs_tasks  = aws_security_group.ecs_tasks.id
    rds        = aws_security_group.rds.id
    redis      = aws_security_group.redis.id
  }
}

output "ssm_parameter_arns" {
  description = "SSM parameter ARNs for secrets"
  value = {
    jwt_secret_key    = aws_ssm_parameter.jwt_secret.arn
    openai_api_key    = aws_ssm_parameter.openai_api_key.arn
    auth_db_password     = aws_ssm_parameter.auth_db_password.arn
    property_db_password = aws_ssm_parameter.property_db_password.arn
    stock_db_password    = aws_ssm_parameter.stock_db_password.arn
  }
  sensitive = true
}