#!/bin/bash

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
ENVIRONMENT="dev"
AWS_REGION="us-east-1"
PROJECT_NAME="theagents"
TERRAFORM_DIR="../terraform"
DOCKER_COMPOSE_FILE="../docker-compose.yml"

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    local deps=("aws" "terraform" "docker" "jq")
    local missing_deps=()
    
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing_deps+=("$dep")
        fi
    done
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        print_error "Missing dependencies: ${missing_deps[*]}"
        print_error "Please install the missing dependencies and try again."
        exit 1
    fi
    
    print_status "All dependencies are installed."
}

# Function to check AWS credentials
check_aws_credentials() {
    print_status "Checking AWS credentials..."
    
    if ! aws sts get-caller-identity &> /dev/null; then
        print_error "AWS credentials not configured or invalid."
        print_error "Please run 'aws configure' or set AWS credentials."
        exit 1
    fi
    
    local aws_account_id=$(aws sts get-caller-identity --query Account --output text)
    print_status "Using AWS Account: $aws_account_id"
}

# Function to create ECR repositories
create_ecr_repositories() {
    print_status "Creating ECR repositories..."
    
    local repositories=(
        "${PROJECT_NAME}-auth-service"
        "${PROJECT_NAME}-property-service"
        "${PROJECT_NAME}-stock-service"
        "${PROJECT_NAME}-api-gateway"
        "${PROJECT_NAME}-frontend"
    )
    
    for repo in "${repositories[@]}"; do
        if aws ecr describe-repositories --repository-names "$repo" --region "$AWS_REGION" &> /dev/null; then
            print_status "ECR repository '$repo' already exists."
        else
            print_status "Creating ECR repository: $repo"
            aws ecr create-repository \
                --repository-name "$repo" \
                --region "$AWS_REGION" \
                --image-scanning-configuration scanOnPush=true \
                --encryption-configuration encryptionType=AES256
        fi
    done
}

# Function to build and push Docker images
build_and_push_images() {
    print_status "Building and pushing Docker images..."
    
    local aws_account_id=$(aws sts get-caller-identity --query Account --output text)
    local ecr_base_url="${aws_account_id}.dkr.ecr.${AWS_REGION}.amazonaws.com"
    
    # Login to ECR
    print_status "Logging in to ECR..."
    aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$ecr_base_url"
    
    # Build and push each service
    local services=("auth-service" "property-service" "stock-ai-service" "api-gateway" "frontend")
    
    for service in "${services[@]}"; do
        local service_name="${service}"
        if [ "$service" == "stock-ai-service" ]; then
            service_name="stock-service"
        fi
        
        local image_tag="${ecr_base_url}/${PROJECT_NAME}-${service_name}:latest"
        
        print_status "Building image for $service..."
        docker build -t "$image_tag" "../$service"
        
        print_status "Pushing image for $service..."
        docker push "$image_tag"
    done
}

# Function to initialize and apply Terraform
deploy_infrastructure() {
    print_status "Deploying infrastructure with Terraform..."
    
    cd "$TERRAFORM_DIR"
    
    # Initialize Terraform
    print_status "Initializing Terraform..."
    terraform init
    
    # Validate Terraform configuration
    print_status "Validating Terraform configuration..."
    terraform validate
    
    # Plan Terraform deployment
    print_status "Planning Terraform deployment..."
    terraform plan -var="environment=$ENVIRONMENT" -var="aws_region=$AWS_REGION" -var="project_name=$PROJECT_NAME"
    
    # Ask for confirmation
    read -p "Do you want to apply these changes? (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_status "Applying Terraform configuration..."
        terraform apply -var="environment=$ENVIRONMENT" -var="aws_region=$AWS_REGION" -var="project_name=$PROJECT_NAME" -auto-approve
    else
        print_warning "Terraform apply cancelled."
        exit 0
    fi
    
    cd - > /dev/null
}

# Function to update service configurations
update_services() {
    print_status "Services deployed successfully!"
    print_status "You can check the status with:"
    echo "  aws ecs list-services --cluster ${PROJECT_NAME}-${ENVIRONMENT}-cluster --region ${AWS_REGION}"
    echo "  aws ecs describe-services --cluster ${PROJECT_NAME}-${ENVIRONMENT}-cluster --services <service-name> --region ${AWS_REGION}"
}

# Function to show deployment information
show_deployment_info() {
    print_status "Getting deployment information..."
    
    cd "$TERRAFORM_DIR"
    
    local nlb_dns=$(terraform output -raw nlb_dns_name 2>/dev/null || echo "Not available")
    local cluster_name=$(terraform output -raw ecs_cluster_name 2>/dev/null || echo "Not available")
    
    cd - > /dev/null
    
    echo ""
    echo "==================================="
    echo "    DEPLOYMENT COMPLETE"
    echo "==================================="
    echo ""
    echo "Network Load Balancer DNS: $nlb_dns"
    echo "ECS Cluster Name: $cluster_name"
    echo "Environment: $ENVIRONMENT"
    echo "Region: $AWS_REGION"
    echo ""
    echo "Next steps:"
    echo "1. Update your DNS records to point to the NLB"
    echo "2. Update SSL certificate ARN in terraform.tfvars if needed"
    echo "3. Monitor services in AWS ECS console"
    echo ""
}

# Function to clean up resources
cleanup() {
    print_warning "Cleaning up AWS resources..."
    
    cd "$TERRAFORM_DIR"
    
    read -p "Are you sure you want to destroy all resources? This cannot be undone. (yes/no): " -r
    if [[ $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        print_status "Destroying infrastructure..."
        terraform destroy -var="environment=$ENVIRONMENT" -var="aws_region=$AWS_REGION" -var="project_name=$PROJECT_NAME" -auto-approve
        
        # Delete ECR repositories
        print_status "Deleting ECR repositories..."
        local repositories=(
            "${PROJECT_NAME}-auth-service"
            "${PROJECT_NAME}-property-service"
            "${PROJECT_NAME}-stock-service"
            "${PROJECT_NAME}-api-gateway"
            "${PROJECT_NAME}-frontend"
        )
        
        for repo in "${repositories[@]}"; do
            if aws ecr describe-repositories --repository-names "$repo" --region "$AWS_REGION" &> /dev/null; then
                print_status "Deleting ECR repository: $repo"
                aws ecr delete-repository --repository-name "$repo" --region "$AWS_REGION" --force
            fi
        done
        
        print_status "Cleanup complete!"
    else
        print_warning "Cleanup cancelled."
    fi
    
    cd - > /dev/null
}

# Help function
show_help() {
    echo "Usage: $0 [OPTIONS] [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  deploy    Deploy the complete infrastructure (default)"
    echo "  cleanup   Destroy all AWS resources"
    echo "  ecr       Create ECR repositories only"
    echo "  build     Build and push Docker images only"
    echo "  info      Show deployment information"
    echo "  help      Show this help message"
    echo ""
    echo "Options:"
    echo "  -e, --environment   Environment name (default: dev)"
    echo "  -r, --region       AWS region (default: us-east-1)"
    echo "  -p, --project      Project name (default: theagents)"
    echo ""
    echo "Examples:"
    echo "  $0 deploy"
    echo "  $0 --environment prod --region us-west-2 deploy"
    echo "  $0 cleanup"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--environment)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -r|--region)
            AWS_REGION="$2"
            shift 2
            ;;
        -p|--project)
            PROJECT_NAME="$2"
            shift 2
            ;;
        deploy|cleanup|ecr|build|info|help)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Default command
COMMAND="${COMMAND:-deploy}"

# Main execution
case $COMMAND in
    deploy)
        check_dependencies
        check_aws_credentials
        create_ecr_repositories
        build_and_push_images
        deploy_infrastructure
        update_services
        show_deployment_info
        ;;
    cleanup)
        check_dependencies
        check_aws_credentials
        cleanup
        ;;
    ecr)
        check_dependencies
        check_aws_credentials
        create_ecr_repositories
        ;;
    build)
        check_dependencies
        check_aws_credentials
        build_and_push_images
        ;;
    info)
        show_deployment_info
        ;;
    help)
        show_help
        ;;
    *)
        print_error "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac