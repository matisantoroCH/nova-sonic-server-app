output "api_gateway_url" {
  description = "API Gateway URL"
  value       = "${aws_api_gateway_stage.main.invoke_url}"
}

output "orders_table_name" {
  description = "Orders DynamoDB table name"
  value       = aws_dynamodb_table.orders_table.name
}

output "appointments_table_name" {
  description = "Appointments DynamoDB table name"
  value       = aws_dynamodb_table.appointments_table.name
}

output "lambda_function" {
  description = "Lambda function name"
  value = aws_lambda_function.api.function_name
}

output "dynamodb_tables" {
  description = "DynamoDB table ARNs"
  value = {
    orders_table      = aws_dynamodb_table.orders_table.arn
    appointments_table = aws_dynamodb_table.appointments_table.arn
  }
}

output "iam_role_arn" {
  description = "IAM role ARN for Lambda functions"
  value       = aws_iam_role.lambda_role.arn
}

output "nova_sonic_ecs_cluster" {
  description = "Nova Sonic ECS cluster name"
  value       = aws_ecs_cluster.nova_sonic_cluster.name
}

output "nova_sonic_task_role_arn" {
  description = "Nova Sonic ECS task role ARN"
  value       = aws_iam_role.nova_sonic_task_role.arn
}

output "nova_sonic_service_name" {
  description = "Nova Sonic ECS service name"
  value       = aws_ecs_service.nova_sonic_service.name
} 