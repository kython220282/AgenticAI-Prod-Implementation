# Multi-Region Deployment Guide
# ===============================

## Overview

This guide covers deploying Agentic AI across multiple regions for:
- High availability (HA)
- Disaster recovery (DR)
- Geographic distribution for reduced latency
- Compliance with data residency requirements

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Global Load Balancer                    │
│                    (CloudFlare / Route53)                    │
└───────────────┬──────────────────────┬─────────────────────┘
                │                      │
        ┌───────▼────────┐     ┌───────▼────────┐
        │   Region 1     │     │   Region 2     │
        │   (us-east-1)  │     │   (eu-west-1)  │
        └────────────────┘     └────────────────┘
                │                      │
        ┌───────▼────────┐     ┌───────▼────────┐
        │  K8s Cluster   │     │  K8s Cluster   │
        │  - API Pods    │     │  - API Pods    │
        │  - Workers     │     │  - Workers     │
        │  - Database    │◄────┼──► Database    │
        │  - Redis       │     │  - Redis       │
        └────────────────┘     └────────────────┘
```

## Prerequisites

1. **Multiple Kubernetes Clusters**
   - Cluster in each region
   - Consistent versions
   - Network connectivity between regions

2. **Global DNS**
   - Route53, CloudFlare, or similar
   - Health check capability
   - Geo-routing support

3. **Database Replication**
   - PostgreSQL with streaming replication
   - Or managed service (RDS, Cloud SQL)

## Step 1: Set Up Regional Clusters

### Region 1 (Primary): us-east-1

```bash
# Configure kubectl for us-east-1
export KUBECONFIG=~/.kube/config-us-east-1

# Deploy to us-east-1
kubectl create namespace agenticai
kubectl label namespace agenticai region=us-east-1 tier=primary

# Apply all manifests
kubectl apply -f k8s/ -R
```

### Region 2 (Secondary): eu-west-1

```bash
# Configure kubectl for eu-west-1
export KUBECONFIG=~/.kube/config-eu-west-1

# Deploy to eu-west-1
kubectl create namespace agenticai
kubectl label namespace agenticai region=eu-west-1 tier=secondary

# Apply all manifests
kubectl apply -f k8s/ -R
```

## Step 2: Configure Database Replication

### PostgreSQL Streaming Replication

**Primary (us-east-1):**

```yaml
# k8s/statefulsets/postgres-primary.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-primary
  namespace: agenticai
spec:
  serviceName: postgres
  replicas: 1
  template:
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_DB
          value: agenticai_db
        - name: POSTGRES_REPLICATION_MODE
          value: master
        - name: POSTGRES_REPLICATION_USER
          valueFrom:
            secretKeyRef:
              name: postgres-replication
              key: username
        - name: POSTGRES_REPLICATION_PASSWORD
          valueFrom:
            secretKeyRef:
              name: postgres-replication
              key: password
```

**Replica (eu-west-1):**

```yaml
# k8s/statefulsets/postgres-replica.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres-replica
  namespace: agenticai
spec:
  serviceName: postgres
  replicas: 1
  template:
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        env:
        - name: POSTGRES_REPLICATION_MODE
          value: slave
        - name: POSTGRES_MASTER_HOST
          value: postgres.agenticai.us-east-1.example.com
        - name: POSTGRES_MASTER_PORT
          value: "5432"
```

### Managed Database Option

**AWS RDS Multi-Region:**

```bash
# Create primary in us-east-1
aws rds create-db-instance \
  --db-instance-identifier agenticai-db-primary \
  --region us-east-1 \
  --engine postgres \
  --engine-version 15.3 \
  --db-instance-class db.r6g.xlarge \
  --allocated-storage 100 \
  --multi-az

# Create read replica in eu-west-1
aws rds create-db-instance-read-replica \
  --db-instance-identifier agenticai-db-replica \
  --region eu-west-1 \
  --source-db-instance-identifier arn:aws:rds:us-east-1:ACCOUNT:db:agenticai-db-primary
```

## Step 3: Configure Redis Replication

### Redis Cluster Mode

```yaml
# k8s/statefulsets/redis-cluster.yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: redis
  namespace: agenticai
spec:
  serviceName: redis
  replicas: 6  # 3 masters, 3 replicas
  template:
    spec:
      containers:
      - name: redis
        image: redis:7-alpine
        command:
          - redis-server
          - --cluster-enabled
          - "yes"
          - --cluster-config-file
          - /data/nodes.conf
          - --cluster-node-timeout
          - "5000"
          - --appendonly
          - "yes"
```

### Initialize Redis Cluster

```bash
# Get pod IPs
REDIS_NODES=$(kubectl get pods -l app=redis -o jsonpath='{range.items[*]}{.status.podIP}:6379 {end}')

# Create cluster
kubectl exec -it redis-0 -- redis-cli --cluster create $REDIS_NODES --cluster-replicas 1
```

## Step 4: Configure Global Load Balancer

### AWS Route53 with Health Checks

```yaml
# route53-config.yaml
Resources:
  HealthCheckUSEast1:
    Type: AWS::Route53::HealthCheck
    Properties:
      Type: HTTPS
      ResourcePath: /health/ready
      FullyQualifiedDomainName: api-us-east-1.agenticai.example.com
      Port: 443
      RequestInterval: 30
      FailureThreshold: 3

  HealthCheckEUWest1:
    Type: AWS::Route53::HealthCheck
    Properties:
      Type: HTTPS
      ResourcePath: /health/ready
      FullyQualifiedDomainName: api-eu-west-1.agenticai.example.com
      Port: 443
      RequestInterval: 30
      FailureThreshold: 3

  RecordSet:
    Type: AWS::Route53::RecordSet
    Properties:
      HostedZoneName: agenticai.example.com.
      Name: api.agenticai.example.com
      Type: A
      SetIdentifier: us-east-1
      GeoLocation:
        ContinentCode: NA
      HealthCheckId: !Ref HealthCheckUSEast1
      AliasTarget:
        HostedZoneId: Z1234567890ABC
        DNSName: api-us-east-1.agenticai.example.com
        EvaluateTargetHealth: true
```

### CloudFlare Load Balancer

```bash
# Create pools
curl -X POST "https://api.cloudflare.com/client/v4/accounts/ACCOUNT_ID/load_balancers/pools" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "us-east-1-pool",
    "origins": [{
      "name": "us-east-1",
      "address": "api-us-east-1.agenticai.example.com",
      "enabled": true
    }],
    "monitor": "health-check-id"
  }'

# Create load balancer
curl -X POST "https://api.cloudflare.com/client/v4/zones/ZONE_ID/load_balancers" \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "name": "api.agenticai.example.com",
    "default_pools": ["us-east-1-pool", "eu-west-1-pool"],
    "steering_policy": "geo",
    "region_pools": {
      "WNAM": ["us-east-1-pool"],
      "WEU": ["eu-west-1-pool"]
    }
  }'
```

## Step 5: Configure Cross-Region Networking

### VPC Peering (AWS)

```bash
# Create peering connection
aws ec2 create-vpc-peering-connection \
  --vpc-id vpc-us-east-1 \
  --peer-vpc-id vpc-eu-west-1 \
  --peer-region eu-west-1

# Accept peering connection
aws ec2 accept-vpc-peering-connection \
  --vpc-peering-connection-id pcx-123456 \
  --region eu-west-1

# Update route tables
aws ec2 create-route \
  --route-table-id rtb-us-east-1 \
  --destination-cidr-block 10.1.0.0/16 \
  --vpc-peering-connection-id pcx-123456
```

### GKE Multi-Cluster Mesh

```bash
# Register clusters to fleet
gcloud container fleet memberships register us-east-1-cluster \
  --gke-cluster us-east1/agenticai-cluster \
  --enable-workload-identity

gcloud container fleet memberships register eu-west-1-cluster \
  --gke-cluster europe-west1/agenticai-cluster \
  --enable-workload-identity

# Enable multi-cluster services
gcloud container fleet multi-cluster-services enable
```

## Step 6: Deploy with Helm (Multi-Region)

```bash
# Install in us-east-1
helm install agenticai ./helm/agenticai \
  --namespace agenticai \
  --set global.region=us-east-1 \
  --set postgresql.primary=true \
  --set redis.cluster.enabled=true \
  --kubeconfig ~/.kube/config-us-east-1

# Install in eu-west-1
helm install agenticai ./helm/agenticai \
  --namespace agenticai \
  --set global.region=eu-west-1 \
  --set postgresql.primary=false \
  --set postgresql.replication.enabled=true \
  --set redis.cluster.enabled=true \
  --kubeconfig ~/.kube/config-eu-west-1
```

## Step 7: Monitoring and Observability

### Federated Prometheus

```yaml
# prometheus-federation.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      external_labels:
        cluster: global
    
    scrape_configs:
    - job_name: 'federate-us-east-1'
      scrape_interval: 15s
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
          - '{job="kubernetes-pods"}'
      static_configs:
        - targets:
          - 'prometheus.us-east-1.example.com:9090'
    
    - job_name: 'federate-eu-west-1'
      scrape_interval: 15s
      honor_labels: true
      metrics_path: '/federate'
      params:
        'match[]':
          - '{job="kubernetes-pods"}'
      static_configs:
        - targets:
          - 'prometheus.eu-west-1.example.com:9090'
```

### Centralized Logging

```bash
# Deploy Loki in each region, aggregate to central instance
helm install loki grafana/loki-stack \
  --namespace logging \
  --set promtail.enabled=true \
  --set loki.persistence.enabled=true \
  --set loki.config.limits_config.retention_period=30d
```

## Step 8: Disaster Recovery Plan

### Automated Failover

```yaml
# k8s/dr/failover-controller.yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: health-check-failover
  namespace: agenticai
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: failover
            image: alpine/curl
            command:
            - /bin/sh
            - -c
            - |
              if ! curl -f https://api-us-east-1.agenticai.example.com/health/ready; then
                # Promote replica to primary
                kubectl exec -it postgres-replica-0 -- pg_ctl promote
                # Update DNS to point to eu-west-1
                # aws route53 change-resource-record-sets ...
              fi
```

### Manual Failover Process

1. **Promote replica database:**
   ```bash
   kubectl exec -it postgres-replica-0 -n agenticai -- pg_ctl promote
   ```

2. **Update DNS:**
   ```bash
   aws route53 change-resource-record-sets \
     --hosted-zone-id Z123456 \
     --change-batch file://failover-dns.json
   ```

3. **Scale up workers in secondary region:**
   ```bash
   kubectl scale deployment agenticai-worker --replicas=10 -n agenticai
   ```

4. **Verify services:**
   ```bash
   curl https://api.agenticai.example.com/health/ready
   ```

## Testing

### Load Testing from Multiple Regions

```bash
# From us-east-1
k6 run --vus 100 --duration 5m tests/load-test.js

# From eu-west-1
k6 run --vus 100 --duration 5m tests/load-test.js

# Check routing
for i in {1..100}; do
  curl -s https://api.agenticai.example.com/health | jq -r '.region'
done | sort | uniq -c
```

### Failover Testing

```bash
# Simulate region failure
kubectl scale deployment agenticai-api --replicas=0 -n agenticai

# Monitor traffic shifting
watch -n 1 'curl -s https://api.agenticai.example.com/health | jq -r .region'
```

## Cost Optimization

1. **Use spot instances for workers in non-primary regions**
2. **Scale down during off-peak hours**
3. **Use regional data transfer optimization**
4. **Implement caching to reduce cross-region DB queries**

## Compliance Considerations

- **GDPR**: Keep EU data in EU region
- **Data residency**: Configure database rules per region
- **Audit logging**: Enable CloudTrail/Cloud Audit Logs in all regions

## Monitoring Checklist

- [ ] Cross-region latency < 100ms
- [ ] Replication lag < 1s
- [ ] Failover time < 5 minutes
- [ ] Global uptime > 99.99%
- [ ] Regional health checks passing
- [ ] Database synchronization healthy
- [ ] Cross-region traffic balanced
