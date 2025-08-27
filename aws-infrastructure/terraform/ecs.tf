resource "aws_ecs_cluster" "main" {
  name = "${var.project_name}-${var.environment}-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = local.common_tags
}

resource "aws_ecs_cluster_capacity_providers" "main" {
  cluster_name = aws_ecs_cluster.main.name

  capacity_providers = ["FARGATE", "FARGATE_SPOT"]

  default_capacity_provider_strategy {
    base              = 1
    weight            = 100
    capacity_provider = "FARGATE"
  }
}

# IAM Role for ECS Tasks
resource "aws_iam_role" "ecs_task_execution_role" {
  name = "${var.project_name}-${var.environment}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role_policy" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task_role" {
  name = "${var.project_name}-${var.environment}-ecs-task-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })

  tags = local.common_tags
}

# CloudWatch Log Groups
resource "aws_cloudwatch_log_group" "auth_service" {
  count = var.enable_logs ? 1 : 0
  
  name              = "/ecs/${var.project_name}-${var.environment}-auth"
  retention_in_days = 30

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "property_service" {
  count = var.enable_logs ? 1 : 0
  
  name              = "/ecs/${var.project_name}-${var.environment}-property"
  retention_in_days = 30

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "stock_service" {
  count = var.enable_logs ? 1 : 0
  
  name              = "/ecs/${var.project_name}-${var.environment}-stock"
  retention_in_days = 30

  tags = local.common_tags
}

resource "aws_cloudwatch_log_group" "frontend" {
  count = var.enable_logs ? 1 : 0
  
  name              = "/ecs/${var.project_name}-${var.environment}-frontend"
  retention_in_days = 30

  tags = local.common_tags
}

# ECS Task Definitions
resource "aws_ecs_task_definition" "auth_service" {
  family                   = "${var.project_name}-${var.environment}-auth"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "auth-service"
      image = var.ecr_repository_urls.auth_service != "" ? var.ecr_repository_urls.auth_service : "nginx:latest"
      
      portMappings = [
        {
          containerPort = 8001
          hostPort      = 8001
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "AUTH_DATABASE_URL"
          value = "postgresql://${aws_db_instance.auth.username}:${random_password.auth_db_password.result}@${aws_db_instance.auth.endpoint}/${aws_db_instance.auth.db_name}"
        },
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_replication_group.main.primary_endpoint_address
        },
        {
          name  = "REDIS_PORT"
          value = "6379"
        },
        {
          name  = "DEBUG"
          value = "false"
        }
      ]

      secrets = [
        {
          name      = "JWT_SECRET_KEY"
          valueFrom = aws_ssm_parameter.jwt_secret.arn
        }
      ]

      logConfiguration = var.enable_logs ? {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.auth_service[0].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      } : null

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8001/auth/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = local.common_tags
}

resource "aws_ecs_task_definition" "property_service" {
  family                   = "${var.project_name}-${var.environment}-property"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "property-service"
      image = var.ecr_repository_urls.property_service != "" ? var.ecr_repository_urls.property_service : "nginx:latest"
      
      portMappings = [
        {
          containerPort = 8002
          hostPort      = 8002
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "PROPERTY_DATABASE_URL"
          value = "postgresql://${aws_db_instance.property.username}:${random_password.property_db_password.result}@${aws_db_instance.property.endpoint}/${aws_db_instance.property.db_name}"
        },
        {
          name  = "AUTH_SERVICE_URL"
          value = "http://auth.${var.domain_name}"
        },
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_replication_group.main.primary_endpoint_address
        },
        {
          name  = "DEBUG"
          value = "false"
        }
      ]

      logConfiguration = var.enable_logs ? {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.property_service[0].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      } : null

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8002/properties/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = local.common_tags
}

resource "aws_ecs_task_definition" "stock_service" {
  family                   = "${var.project_name}-${var.environment}-stock"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "stock-service"
      image = var.ecr_repository_urls.stock_service != "" ? var.ecr_repository_urls.stock_service : "nginx:latest"
      
      portMappings = [
        {
          containerPort = 8002
          hostPort      = 8002
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "STOCK_DATABASE_URL"
          value = "postgresql://${aws_db_instance.stock.username}:${random_password.stock_db_password.result}@${aws_db_instance.stock.endpoint}/${aws_db_instance.stock.db_name}"
        },
        {
          name  = "AUTH_SERVICE_URL"
          value = "http://auth.${var.domain_name}"
        },
        {
          name  = "REDIS_HOST"
          value = aws_elasticache_replication_group.main.primary_endpoint_address
        },
        {
          name  = "DEBUG"
          value = "false"
        }
      ]

      secrets = [
        {
          name      = "OPENAI_API_KEY"
          valueFrom = aws_ssm_parameter.openai_api_key.arn
        }
      ]

      logConfiguration = var.enable_logs ? {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.stock_service[0].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      } : null

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:8002/stock/health || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = local.common_tags
}

resource "aws_ecs_task_definition" "frontend" {
  family                   = "${var.project_name}-${var.environment}-frontend"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = var.ecs_task_cpu
  memory                   = var.ecs_task_memory
  execution_role_arn       = aws_iam_role.ecs_task_execution_role.arn
  task_role_arn           = aws_iam_role.ecs_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "frontend"
      image = var.ecr_repository_urls.frontend != "" ? var.ecr_repository_urls.frontend : "nginx:latest"
      
      portMappings = [
        {
          containerPort = 3000
          hostPort      = 3000
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "REACT_APP_API_URL"
          value = "https://${var.domain_name}"
        },
        {
          name  = "REACT_APP_AUTH_SERVICE_URL"
          value = "https://auth.${var.domain_name}"
        },
        {
          name  = "REACT_APP_PROPERTY_SERVICE_URL"
          value = "https://property.${var.domain_name}"
        },
        {
          name  = "REACT_APP_STOCK_SERVICE_URL"
          value = "https://stock.${var.domain_name}"
        }
      ]

      logConfiguration = var.enable_logs ? {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.frontend[0].name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "ecs"
        }
      } : null

      healthCheck = {
        command     = ["CMD-SHELL", "curl -f http://localhost:3000 || exit 1"]
        interval    = 30
        timeout     = 5
        retries     = 3
        startPeriod = 60
      }
    }
  ])

  tags = local.common_tags
}

# ECS Services
resource "aws_ecs_service" "auth_service" {
  name            = "${var.project_name}-${var.environment}-auth"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.auth_service.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets         = aws_subnet.private[*].id
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.auth_service.arn
    container_name   = "auth-service"
    container_port   = 8001
  }

  depends_on = [aws_lb_listener.http]

  tags = local.common_tags
}

resource "aws_ecs_service" "property_service" {
  name            = "${var.project_name}-${var.environment}-property"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.property_service.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets         = aws_subnet.private[*].id
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.property_service.arn
    container_name   = "property-service"
    container_port   = 8002
  }

  depends_on = [aws_lb_listener.http]

  tags = local.common_tags
}

resource "aws_ecs_service" "stock_service" {
  name            = "${var.project_name}-${var.environment}-stock"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.stock_service.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets         = aws_subnet.private[*].id
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.stock_service.arn
    container_name   = "stock-service"
    container_port   = 8002
  }

  depends_on = [aws_lb_listener.http]

  tags = local.common_tags
}

resource "aws_ecs_service" "frontend" {
  name            = "${var.project_name}-${var.environment}-frontend"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.frontend.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    security_groups  = [aws_security_group.ecs_tasks.id]
    subnets         = aws_subnet.private[*].id
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.frontend.arn
    container_name   = "frontend"
    container_port   = 3000
  }

  depends_on = [aws_lb_listener.http]

  tags = local.common_tags
}