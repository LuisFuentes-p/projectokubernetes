# GitHub Actions Docker Hub Setup Guide

## Required Secrets

Add these secrets to your GitHub repository:

### 1. `DOCKERHUB_USERNAME`
Your Docker Hub username (the account you'll use to push images).

### 2. `DOCKERHUB_TOKEN`
A Docker Hub Personal Access Token (NOT your password).

---

## Step-by-Step Setup

### Step 1: Create a Docker Hub Personal Access Token

1. Go to [Docker Hub](https://hub.docker.com/) and sign in
2. Click your **Profile icon** → **Account Settings** → **Security**
3. Click **New Access Token**
4. Name it: `github-actions` (or similar)
5. Set permissions: `Read, Write, Delete` (to push and manage images)
6. Click **Generate**
7. **Copy the token** (you won't see it again!)

### Step 2: Add Secrets to GitHub

1. Go to your GitHub repository
2. **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

**Add secret #1:**
- Name: `DOCKERHUB_USERNAME`
- Value: Your Docker Hub username (e.g., `your-docker-username`)

**Add secret #2:**
- Name: `DOCKERHUB_TOKEN`
- Value: The token you copied from Docker Hub

---

## How the Workflow Works

**Triggers:**
- Pushes to `main` or `develop` branches (only if service files changed)
- Pull requests to `main` or `develop` (builds but doesn't push)

**What it does:**
1. Checks out your code
2. Sets up Docker Buildx for efficient multi-platform builds
3. Logs in to Docker Hub (only on push)
4. Builds each microservice image in parallel
5. Tags images with:
   - Branch name (e.g., `main`, `develop`)
   - Git SHA (short commit hash)
   - `latest` (only for main branch)
6. Pushes to Docker Hub (only on main branch push)

**Image naming:**
- `docker.io/your-docker-username/transaction-processor:main`
- `docker.io/your-docker-username/transaction-consumer:develop`
- `docker.io/your-docker-username/dashboard:latest` (on main branch only)
- etc.

---

## Update Kubernetes Manifests for Docker Hub

After the workflow runs, update your k8s manifests to pull from Docker Hub:

```yaml
image: your-docker-username/transaction-processor:latest
imagePullPolicy: IfNotPresent  # or Always for remote registry
```

Update these files:
- `k8s/base/dashboard-deployment.yaml`
- `k8s/base/processor-deployment.yaml`
- `k8s/base/db-consumer.yaml`
- `k8s/base/pricing-consumer.yaml`
- `k8s/base/pricing-deployment.yaml`
- `k8s/base/producer.yaml`

Example:
```yaml
spec:
  containers:
  - name: processor
    image: your-docker-username/transaction-processor:latest
    imagePullPolicy: Always  # Always pull latest from Docker Hub
```

---

## Troubleshooting

**Images not pushing?**
- Verify `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` are set correctly
- Check GitHub Actions logs for authentication errors

**Builds failing?**
- Ensure all Dockerfiles are in the correct paths
- Check that `requirements.txt` files exist and are valid

**Using a private Docker Hub registry?**
- Add `imagePullSecrets` to your k8s manifests:
```yaml
spec:
  imagePullSecrets:
  - name: dockerhub-secret
```

Then create the secret in k8s:
```bash
kubectl create secret docker-registry dockerhub-secret \
  --docker-server=docker.io \
  --docker-username=your-docker-username \
  --docker-password=your-docker-token \
  -n trading-system
```

---

## Optional: Customize the Workflow

Edit `.github/workflows/build-push-images.yml` to:
- Change branch triggers
- Add different tag strategies
- Enable multi-platform builds (ARM64 for Apple Silicon, etc.)
- Add image scanning or testing steps
