# Nova Sonic ECS IAM Role and Policies
# This file defines the IAM resources needed for Nova Sonic when deployed to ECS

# IAM Role for Nova Sonic ECS Task
resource "aws_iam_role" "nova_sonic_task_role" {
  name = "${var.project_name}-${var.stage}-nova-sonic-task-role"

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

  tags = {
    Name        = "${var.project_name}-${var.stage}-nova-sonic-task-role"
    Environment = var.stage
    Project     = var.project_name
  }
}

# IAM Policy for Nova Sonic permissions
resource "aws_iam_policy" "nova_sonic_policy" {
  name        = "${var.project_name}-${var.stage}-nova-sonic-policy"
  description = "Policy for Nova Sonic to access DynamoDB and Bedrock"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:UpdateItem",
          "dynamodb:DeleteItem",
          "dynamodb:Query",
          "dynamodb:Scan"
        ]
        Resource = [
          aws_dynamodb_table.orders.arn,
          "${aws_dynamodb_table.orders.arn}/index/*",
          aws_dynamodb_table.appointments.arn,
          "${aws_dynamodb_table.appointments.arn}/index/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel",
          "bedrock:InvokeModelWithResponseStream"
        ]
        Resource = [
          "arn:aws:bedrock:${var.aws_region}::foundation-model/amazon.nova-sonic-v1:0"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "sts:GetCallerIdentity"
        ]
        Resource = "*"
      }
    ]
  })
}

# Attach policy to role
resource "aws_iam_role_policy_attachment" "nova_sonic_policy_attachment" {
  role       = aws_iam_role.nova_sonic_task_role.name
  policy_arn = aws_iam_policy.nova_sonic_policy.arn
}

# IAM Role for ECS Task Execution (for pulling images, etc.)
resource "aws_iam_role" "nova_sonic_task_execution_role" {
  name = "${var.project_name}-${var.stage}-nova-sonic-execution-role"

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

  tags = {
    Name        = "${var.project_name}-${var.stage}-nova-sonic-execution-role"
    Environment = var.stage
    Project     = var.project_name
  }
}

# Attach AWS managed policy for ECS task execution
resource "aws_iam_role_policy_attachment" "nova_sonic_execution_policy_attachment" {
  role       = aws_iam_role.nova_sonic_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

# ECS Cluster for Nova Sonic
resource "aws_ecs_cluster" "nova_sonic_cluster" {
  name = "${var.project_name}-${var.stage}-nova-sonic-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }

  tags = {
    Name        = "${var.project_name}-${var.stage}-nova-sonic-cluster"
    Environment = var.stage
    Project     = var.project_name
  }
}

# ECS Task Definition for Nova Sonic
resource "aws_ecs_task_definition" "nova_sonic_task" {
  family                   = "${var.project_name}-${var.stage}-nova-sonic-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = aws_iam_role.nova_sonic_task_execution_role.arn
  task_role_arn            = aws_iam_role.nova_sonic_task_role.arn

  container_definitions = jsonencode([
    {
      name  = "nova-sonic"
      image = "nova-sonic:latest" # This will be updated with actual image

      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]

      environment = [
        {
          name  = "ORDERS_TABLE"
          value = aws_dynamodb_table.orders.name
        },
        {
          name  = "APPOINTMENTS_TABLE"
          value = aws_dynamodb_table.appointments.name
        },
        {
          name  = "AWS_DEFAULT_REGION"
          value = var.aws_region
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = "/ecs/${var.project_name}-${var.stage}-nova-sonic"
          awslogs-region        = var.aws_region
          awslogs-stream-prefix = "ecs"
        }
      }

      essential = true
    }
  ])

  tags = {
    Name        = "${var.project_name}-${var.stage}-nova-sonic-task"
    Environment = var.stage
    Project     = var.project_name
  }
}

# CloudWatch Log Group for Nova Sonic
resource "aws_cloudwatch_log_group" "nova_sonic_logs" {
  name              = "/ecs/${var.project_name}-${var.stage}-nova-sonic"
  retention_in_days = 7

  tags = {
    Name        = "${var.project_name}-${var.stage}-nova-sonic-logs"
    Environment = var.stage
    Project     = var.project_name
  }
}

# Security Group for Nova Sonic ECS Service
resource "aws_security_group" "nova_sonic_sg" {
  name        = "${var.project_name}-${var.stage}-nova-sonic-sg"
  description = "Security group for Nova Sonic ECS service"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "WebSocket from API Gateway"
    from_port   = 8080
    to_port     = 8080
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "${var.project_name}-${var.stage}-nova-sonic-sg"
    Environment = var.stage
    Project     = var.project_name
  }
}

# Data source for default VPC
data "aws_vpc" "default" {
  default = true
}

# Data source for default subnets
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ECS Service for Nova Sonic
resource "aws_ecs_service" "nova_sonic_service" {
  name            = "${var.project_name}-${var.stage}-nova-sonic-service"
  cluster         = aws_ecs_cluster.nova_sonic_cluster.id
  task_definition = aws_ecs_task_definition.nova_sonic_task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = data.aws_subnets.default.ids
    security_groups  = [aws_security_group.nova_sonic_sg.id]
    assign_public_ip = true
  }

  depends_on = [
    aws_ecs_cluster.nova_sonic_cluster,
    aws_ecs_task_definition.nova_sonic_task
  ]

  tags = {
    Name        = "${var.project_name}-${var.stage}-nova-sonic-service"
    Environment = var.stage
    Project     = var.project_name
  }
} 