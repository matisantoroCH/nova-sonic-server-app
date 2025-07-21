#!/bin/bash

# Setup Terraform Backend Infrastructure
# This script creates the S3 bucket and DynamoDB table needed for Terraform state management

set -e

echo "🚀 Setting up Terraform Backend Infrastructure..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not configured. Please run 'aws configure' first.${NC}"
    exit 1
fi

echo -e "${YELLOW}📋 Creating S3 bucket and DynamoDB table for Terraform state...${NC}"

# Create backend infrastructure
cd terraform

# Temporarily comment out the backend configuration
echo -e "${YELLOW}📝 Temporarily commenting out backend configuration...${NC}"
cp backend.tf backend.tf.bak
cat > backend.tf << 'EOF'
# Backend temporarily disabled for setup
# terraform {
#   backend "s3" {
#     bucket         = "nova-sonic-terraform-state"
#     key            = "demo/terraform.tfstate"
#     region         = "us-east-1"
#     use_lockfile   = true
#     encrypt        = true
#   }
# }
EOF

# Initialize Terraform
echo -e "${YELLOW}🔧 Initializing Terraform...${NC}"
terraform init

# Plan the backend setup
echo -e "${YELLOW}📋 Planning backend infrastructure...${NC}"
terraform plan -target=aws_s3_bucket.terraform_state

# Apply backend infrastructure
echo -e "${YELLOW}🚀 Creating backend infrastructure...${NC}"
terraform apply -target=aws_s3_bucket.terraform_state --auto-approve

# Restore backend configuration
echo -e "${YELLOW}📝 Restoring backend configuration...${NC}"
cp backend.tf.bak backend.tf

# Initialize with backend
echo -e "${YELLOW}🔧 Initializing Terraform with backend...${NC}"
terraform init -migrate-state

# Remove backend setup file
echo -e "${YELLOW}🧹 Cleaning up backend setup file...${NC}"
rm -f backend-setup.tf

echo -e "${GREEN}✅ Backend infrastructure setup complete!${NC}"
echo -e "${GREEN}📦 S3 Bucket: nova-sonic-terraform-state${NC}"
echo -e "${GREEN}🔒 State Locking: S3 Lockfile (use_lockfile = true)${NC}"
echo -e "${GREEN}🗂️  State Key: demo/terraform.tfstate${NC}"
echo ""
echo -e "${YELLOW}💡 You can now run:${NC}"
echo -e "${YELLOW}   npm run deploy:demo${NC}" 