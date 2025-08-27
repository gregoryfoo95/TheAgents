resource "random_password" "auth_db_password" {
  length  = 32
  special = true
}

resource "random_password" "property_db_password" {
  length  = 32
  special = true
}

resource "random_password" "stock_db_password" {
  length  = 32
  special = true
}

resource "aws_ssm_parameter" "auth_db_password" {
  name  = "/${var.project_name}/${var.environment}/auth-db-password"
  type  = "SecureString"
  value = random_password.auth_db_password.result

  tags = local.common_tags
}

resource "aws_ssm_parameter" "property_db_password" {
  name  = "/${var.project_name}/${var.environment}/property-db-password"
  type  = "SecureString"
  value = random_password.property_db_password.result

  tags = local.common_tags
}

resource "aws_ssm_parameter" "stock_db_password" {
  name  = "/${var.project_name}/${var.environment}/stock-db-password"
  type  = "SecureString"
  value = random_password.stock_db_password.result

  tags = local.common_tags
}

resource "aws_ssm_parameter" "jwt_secret" {
  name  = "/${var.project_name}/${var.environment}/jwt-secret"
  type  = "SecureString"
  value = "super-secret-jwt-key-change-in-production-${random_password.auth_db_password.result}"

  tags = local.common_tags
}

resource "aws_ssm_parameter" "openai_api_key" {
  name  = "/${var.project_name}/${var.environment}/openai-api-key"
  type  = "SecureString"
  value = "your-openai-api-key-here"

  tags = local.common_tags

  lifecycle {
    ignore_changes = [value]
  }
}

# Auth Database
resource "aws_db_instance" "auth" {
  identifier = "${var.project_name}-${var.environment}-auth-db"

  allocated_storage       = var.database_configs.auth_db.allocated_storage
  storage_type            = "gp2"
  storage_encrypted       = true
  engine                  = "postgres"
  engine_version          = var.database_configs.auth_db.engine_version
  instance_class          = var.database_configs.auth_db.instance_class
  db_name                 = "auth_db"
  username                = "auth_user"
  password                = random_password.auth_db_password.result
  parameter_group_name    = "default.postgres15"
  skip_final_snapshot     = true
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  performance_insights_enabled = false
  monitoring_interval         = 0

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-auth-db"
  })
}

# Property Database
resource "aws_db_instance" "property" {
  identifier = "${var.project_name}-${var.environment}-property-db"

  allocated_storage       = var.database_configs.property_db.allocated_storage
  storage_type            = "gp2"
  storage_encrypted       = true
  engine                  = "postgres"
  engine_version          = var.database_configs.property_db.engine_version
  instance_class          = var.database_configs.property_db.instance_class
  db_name                 = "property_db"
  username                = "property_user"
  password                = random_password.property_db_password.result
  parameter_group_name    = "default.postgres15"
  skip_final_snapshot     = true
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  performance_insights_enabled = false
  monitoring_interval         = 0

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-property-db"
  })
}

# Stock Database
resource "aws_db_instance" "stock" {
  identifier = "${var.project_name}-${var.environment}-stock-db"

  allocated_storage       = var.database_configs.stock_db.allocated_storage
  storage_type            = "gp2"
  storage_encrypted       = true
  engine                  = "postgres"
  engine_version          = var.database_configs.stock_db.engine_version
  instance_class          = var.database_configs.stock_db.instance_class
  db_name                 = "stock_ai_db"
  username                = "stock_user"
  password                = random_password.stock_db_password.result
  parameter_group_name    = "default.postgres15"
  skip_final_snapshot     = true
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name

  performance_insights_enabled = false
  monitoring_interval         = 0

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-stock-db"
  })
}

# ElastiCache Redis
resource "aws_elasticache_replication_group" "main" {
  replication_group_id       = "${var.project_name}-${var.environment}-redis"
  description                = "Redis cluster for ${var.project_name} ${var.environment}"
  
  node_type                  = var.redis_node_type
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.main.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  log_delivery_configuration {
    destination      = aws_cloudwatch_log_group.redis[0].name
    destination_type = "cloudwatch-logs"
    log_format       = "text"
    log_type         = "slow-log"
  }

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "redis" {
  count = var.enable_logs ? 1 : 0
  
  name              = "/elasticache/${var.project_name}-${var.environment}-redis"
  retention_in_days = 30

  tags = local.common_tags
}