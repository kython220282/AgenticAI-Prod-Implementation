#!/bin/bash

# ==========================================
# Kubernetes Deployment Script
# ==========================================

set -e

NAMESPACE="agenticai"
KUBECONFIG="${KUBECONFIG:-$HOME/.kube/config}"

echo "🚀 Deploying Agentic AI to Kubernetes..."

# Check kubectl
if ! command -v kubectl &> /dev/null; then
    echo "❌ kubectl not found. Please install kubectl first."
    exit 1
fi

# Check cluster connection
echo "📡 Checking cluster connection..."
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ Cannot connect to Kubernetes cluster"
    exit 1
fi

echo "✅ Connected to cluster"

# Create namespace
echo "📦 Creating namespace: $NAMESPACE"
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# Label namespace
kubectl label namespace $NAMESPACE name=$NAMESPACE --overwrite

# Apply RBAC
echo "👤 Applying RBAC configuration..."
kubectl apply -f k8s/rbac/

# Apply ConfigMaps and Secrets
echo "⚙️  Applying configuration..."
kubectl apply -f k8s/config/configmap.yaml

echo "⚠️  NOTE: Please update k8s/config/secrets.yaml with actual secrets before applying!"
read -p "Have you updated secrets.yaml? (yes/no): " secrets_updated
if [ "$secrets_updated" = "yes" ]; then
    kubectl apply -f k8s/config/secrets.yaml
else
    echo "⚠️  Skipping secrets deployment. Please apply manually after updating."
fi

# Apply storage
echo "💾 Creating persistent volumes..."
kubectl apply -f k8s/storage/

# Deploy databases
echo "🗄️  Deploying PostgreSQL and Redis..."
kubectl apply -f k8s/statefulsets/

# Wait for databases
echo "⏳ Waiting for databases to be ready..."
kubectl wait --for=condition=ready pod -l app=postgres -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=ready pod -l app=redis -n $NAMESPACE --timeout=300s

# Run database migrations
echo "📝 Running database migrations..."
kubectl run migrations-$(date +%s) \
    --namespace=$NAMESPACE \
    --image=ghcr.io/your-org/agenticai:latest \
    --rm -it --restart=Never \
    --command -- alembic upgrade head

# Deploy application
echo "🚀 Deploying API and Workers..."
kubectl apply -f k8s/deployments/

# Apply network policies
echo "🔒 Applying network policies..."
kubectl apply -f k8s/network/

# Apply autoscaling
echo "📈 Configuring autoscaling..."
kubectl apply -f k8s/autoscaling/

# Apply ingress
echo "🌐 Configuring ingress..."
kubectl apply -f k8s/ingress/

# Wait for deployment
echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available deployment/agenticai-api -n $NAMESPACE --timeout=300s
kubectl wait --for=condition=available deployment/agenticai-worker -n $NAMESPACE --timeout=300s

# Display status
echo ""
echo "=========================================="
echo "✅ Deployment completed!"
echo "=========================================="
echo ""

# Get service info
echo "📊 Deployment Status:"
kubectl get deployments -n $NAMESPACE
echo ""

echo "🔍 Pods:"
kubectl get pods -n $NAMESPACE
echo ""

echo "🌐 Services:"
kubectl get services -n $NAMESPACE
echo ""

echo "🔗 Ingress:"
kubectl get ingress -n $NAMESPACE
echo ""

# Display ingress URL
INGRESS_HOST=$(kubectl get ingress agenticai-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}')
echo "🎉 Application URL: https://$INGRESS_HOST"
echo ""

echo "📋 Useful commands:"
echo "  View logs:        kubectl logs -f -l app=agenticai,component=api -n $NAMESPACE"
echo "  Shell into pod:   kubectl exec -it deployment/agenticai-api -n $NAMESPACE -- /bin/bash"
echo "  Port forward:     kubectl port-forward svc/agenticai-api 8000:8000 -n $NAMESPACE"
echo "  Scale deployment: kubectl scale deployment/agenticai-api --replicas=5 -n $NAMESPACE"
echo "  Check HPA:        kubectl get hpa -n $NAMESPACE"
echo ""
