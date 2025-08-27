resource "aws_lb" "nlb" {
  name               = "${var.project_name}-${var.environment}-nlb"
  load_balancer_type = "network"
  scheme             = "internet-facing"
  subnets            = aws_subnet.public[*].id

  enable_deletion_protection = false
  enable_cross_zone_load_balancing = true

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-nlb"
  })
}

# Target Groups for each service
resource "aws_lb_target_group" "auth_service" {
  name     = "${var.project_name}-${var.environment}-auth-tg"
  port     = 8001
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id
  
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
    matcher             = "200"
    path                = "/auth/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 10
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-auth-tg"
  })
}

resource "aws_lb_target_group" "property_service" {
  name     = "${var.project_name}-${var.environment}-property-tg"
  port     = 8002
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id
  
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
    matcher             = "200"
    path                = "/properties/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 10
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-property-tg"
  })
}

resource "aws_lb_target_group" "stock_service" {
  name     = "${var.project_name}-${var.environment}-stock-tg"
  port     = 8002
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id
  
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
    matcher             = "200"
    path                = "/stock/health"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 10
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-stock-tg"
  })
}

resource "aws_lb_target_group" "frontend" {
  name     = "${var.project_name}-${var.environment}-frontend-tg"
  port     = 3000
  protocol = "TCP"
  vpc_id   = aws_vpc.main.id
  
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    interval            = 30
    matcher             = "200"
    path                = "/"
    port                = "traffic-port"
    protocol            = "HTTP"
    timeout             = 10
  }

  tags = merge(local.common_tags, {
    Name = "${var.project_name}-${var.environment}-frontend-tg"
  })
}

# NLB Listeners with host-based routing
resource "aws_lb_listener" "https" {
  count = var.certificate_arn != "" ? 1 : 0
  
  load_balancer_arn = aws_lb.nlb.arn
  port              = "443"
  protocol          = "TLS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }

  tags = local.common_tags
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.nlb.arn
  port              = "80"
  protocol          = "TCP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.frontend.arn
  }

  tags = local.common_tags
}

# Listener rules for host-based routing (requires ALB, will use Route 53 for NLB)
# Note: NLB doesn't support host-based routing, so we'll handle this with Route 53

# Route 53 hosted zone (optional - only if managing DNS)
resource "aws_route53_zone" "main" {
  count = var.domain_name != "" ? 1 : 0
  name  = var.domain_name

  tags = local.common_tags
}

# Route 53 records for service routing
resource "aws_route53_record" "auth" {
  count   = var.domain_name != "" ? 1 : 0
  zone_id = aws_route53_zone.main[0].zone_id
  name    = "auth.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.nlb.dns_name
    zone_id                = aws_lb.nlb.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "property" {
  count   = var.domain_name != "" ? 1 : 0
  zone_id = aws_route53_zone.main[0].zone_id
  name    = "property.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.nlb.dns_name
    zone_id                = aws_lb.nlb.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "stock" {
  count   = var.domain_name != "" ? 1 : 0
  zone_id = aws_route53_zone.main[0].zone_id
  name    = "stock.${var.domain_name}"
  type    = "A"

  alias {
    name                   = aws_lb.nlb.dns_name
    zone_id                = aws_lb.nlb.zone_id
    evaluate_target_health = true
  }
}

resource "aws_route53_record" "root" {
  count   = var.domain_name != "" ? 1 : 0
  zone_id = aws_route53_zone.main[0].zone_id
  name    = var.domain_name
  type    = "A"

  alias {
    name                   = aws_lb.nlb.dns_name
    zone_id                = aws_lb.nlb.zone_id
    evaluate_target_health = true
  }
}