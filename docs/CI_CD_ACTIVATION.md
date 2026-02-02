# CI/CD Activation Guide

This guide explains how to activate and configure CI/CD workflows for your AgenticAI project.

## 🚦 Current Status

- ✅ **CI Pipeline**: Running in template mode (non-blocking)
- ⚠️ **Deployment**: Disabled (manual only)

## 📋 Quick Start Checklist

### Phase 1: Activate CI Pipeline (Required)

**Time Required:** 1-2 hours

- [ ] **Install dependencies locally**
  ```bash
  python -m venv venv
  source venv/bin/activate  # Windows: venv\Scripts\activate
  pip install -r requirements.txt
  ```

- [ ] **Fix code formatting**
  ```bash
  pip install black isort flake8
  black src/ tests/
  isort src/ tests/
  flake8 src/ tests/ --max-line-length=100
  ```

- [ ] **Fix type issues**
  ```bash
  pip install mypy
  mypy src/ --ignore-missing-imports
  # Fix errors or add # type: ignore comments
  ```

- [ ] **Verify tests pass**
  ```bash
  pip install pytest pytest-asyncio
  pytest tests/ -v
  ```

- [ ] **Remove CI soft-fail mode**
  - Edit `.github/workflows/ci.yml`
  - Search for `continue-on-error: true`
  - Remove or set to `false` for critical steps
  - Commit changes

- [ ] **Verify CI passes on GitHub**
  - Push changes
  - Check Actions tab
  - Ensure all checks pass

### Phase 2: Activate Deployment (Optional)

**Time Required:** 2-4 hours (with infrastructure setup)

#### Step 1: Infrastructure Setup

- [ ] **Provision production server**
  - AWS EC2, DigitalOcean, Linode, etc.
  - Minimum: 4GB RAM, 2 CPU cores
  - Ubuntu 22.04 LTS recommended

- [ ] **Install Docker on server**
  ```bash
  curl -fsSL https://get.docker.com -o get-docker.sh
  sudo sh get-docker.sh
  sudo usermod -aG docker $USER
  sudo apt install docker-compose-plugin
  ```

- [ ] **Clone repository to server**
  ```bash
  sudo mkdir -p /opt/agenticai
  sudo chown $USER:$USER /opt/agenticai
  cd /opt/agenticai
  git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .
  ```

- [ ] **Configure environment**
  ```bash
  cp .env.example .env
  nano .env  # Add your API keys and secrets
  ```

- [ ] **Set up domain and SSL**
  - Point DNS A record to server IP
  - Install certbot: `sudo apt install certbot`
  - Get certificate: `certbot --nginx -d yourdomain.com`

#### Step 2: SSH Configuration

- [ ] **Generate SSH key pair**
  ```bash
  # On your local machine
  ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/github_deploy
  ```

- [ ] **Add public key to server**
  ```bash
  # Copy public key
  cat ~/.ssh/github_deploy.pub
  
  # On server, add to authorized_keys
  mkdir -p ~/.ssh
  echo "PASTE_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
  chmod 600 ~/.ssh/authorized_keys
  chmod 700 ~/.ssh
  ```

- [ ] **Test SSH connection**
  ```bash
  ssh -i ~/.ssh/github_deploy user@your-server.com
  ```

#### Step 3: GitHub Secrets

Go to: **Repository → Settings → Secrets and variables → Actions → New repository secret**

- [ ] **Add PRODUCTION_HOST**
  - Name: `PRODUCTION_HOST`
  - Value: `your-server.com` or IP address

- [ ] **Add PRODUCTION_USER**
  - Name: `PRODUCTION_USER`
  - Value: Your SSH username (e.g., `ubuntu`, `deploy`)

- [ ] **Add PRODUCTION_SSH_KEY**
  - Name: `PRODUCTION_SSH_KEY`
  - Value: Contents of `~/.ssh/github_deploy` (private key)
  ```bash
  cat ~/.ssh/github_deploy
  # Copy entire output including headers
  ```

#### Step 4: Update Workflow Configuration

- [ ] **Edit `.github/workflows/deploy.yml`**
  - Line 115, 138: Replace `agenticai.example.com` with your domain
  - Line 86, 112: Update `/opt/agenticai` if using different path
  - Verify `docker-compose.yml` matches your setup

- [ ] **Test manual deployment**
  - Go to: Actions → Deploy to Production → Run workflow
  - Select environment: `staging` or `production`
  - Monitor deployment progress
  - Check: `https://yourdomain.com/health`

#### Step 5: Enable Auto-Deployment

- [ ] **Uncomment auto-deploy trigger**
  - Edit `.github/workflows/deploy.yml`
  - Find lines 81-85 (push trigger section)
  - Uncomment the `push:` section
  - Commit and push

- [ ] **Verify auto-deployment works**
  - Make a small change (e.g., update README)
  - Push to main branch
  - Watch Actions tab for automatic deployment
  - Verify application updated: `curl https://yourdomain.com/health`

## 🔧 Configuration Files

### CI Pipeline Configuration
- **File:** `.github/workflows/ci.yml`
- **Purpose:** Automated testing, linting, security scans
- **Triggers:** Every push and pull request

### Deployment Pipeline Configuration
- **File:** `.github/workflows/deploy.yml`
- **Purpose:** Automated production deployment
- **Triggers:** Manual (default) or auto on main branch push

## 🎯 Recommended Workflow

### Development Flow
```
1. Create feature branch
2. Make changes locally
3. Run tests: pytest tests/
4. Push to branch
5. CI runs automatically (non-blocking)
6. Create pull request
7. CI runs on PR
8. Merge to main
9. (If enabled) Auto-deploy to production
```

### Deployment Stages
```
Local Dev → CI Tests → Manual Deploy (test) → Auto Deploy (enable)
```

## 📊 CI/CD Status Badges

Add to your README.md:

```markdown
![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/ci.yml/badge.svg)
![Deployment](https://github.com/YOUR_USERNAME/YOUR_REPO/actions/workflows/deploy.yml/badge.svg)
```

## 🚨 Troubleshooting

### CI Failures

**Problem:** Tests fail on GitHub but pass locally
- **Solution:** Check Python version matches (3.10+)
- **Solution:** Ensure all dependencies in requirements.txt
- **Solution:** Check for environment-specific code

**Problem:** Black/Flake8 formatting errors
- **Solution:** Run locally: `black src/ tests/ && isort src/ tests/`
- **Solution:** Commit formatted code

**Problem:** MyPy type errors
- **Solution:** Add type hints or `# type: ignore` comments
- **Solution:** Install missing type stubs: `pip install types-*`

### Deployment Failures

**Problem:** SSH connection refused
- **Solution:** Check server firewall allows port 22
- **Solution:** Verify SSH key has correct permissions
- **Solution:** Test SSH manually: `ssh -i key user@host`

**Problem:** Docker build fails
- **Solution:** Test build locally: `docker-compose build`
- **Solution:** Check .env file has required variables
- **Solution:** Review build logs: `docker-compose logs`

**Problem:** Health check fails after deployment
- **Solution:** Check application logs: `docker-compose logs api`
- **Solution:** Verify database migrations: `docker-compose exec api alembic current`
- **Solution:** Check .env configuration

**Problem:** Rollback needed
- **Solution:** SSH to server
- **Solution:** Run: `cd /opt/agenticai && ./scripts/rollback.sh`

## 📚 Additional Resources

- **Full Deployment Guide:** [docs/DEPLOYMENT.md](DEPLOYMENT.md)
- **Getting Started:** [docs/GETTING_STARTED.md](GETTING_STARTED.md)
- **Phase 1 - Production Essentials:** [docs/PHASE1_COMPLETE.md](PHASE1_COMPLETE.md)
- **Phase 2 - CI/CD Infrastructure:** [docs/PHASE2_COMPLETE.md](PHASE2_COMPLETE.md)
- **Phase 3 - Kubernetes & Enterprise:** [docs/PHASE3_COMPLETE.md](PHASE3_COMPLETE.md)

## 🎓 Learning Path

1. **Beginner:** Start with CI activation (Phase 1)
2. **Intermediate:** Set up basic deployment (manual)
3. **Advanced:** Enable auto-deployment and monitoring
4. **Expert:** Move to Kubernetes (Phase 3)

## ⚡ Quick Commands Reference

```bash
# Local Development
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v

# Code Quality
black src/ tests/
isort src/ tests/
flake8 src/ tests/
mypy src/

# Docker Local
docker-compose up -d
docker-compose logs -f api
docker-compose down

# Server Deployment (SSH)
ssh user@server
cd /opt/agenticai
git pull
docker-compose up -d
./scripts/backup.sh  # Before updates
./scripts/rollback.sh  # If needed
```

## ✅ Success Criteria

### CI Pipeline Active
- [ ] All tests pass on GitHub Actions
- [ ] Code formatting checks pass
- [ ] Security scans complete
- [ ] Docker image builds successfully

### Deployment Pipeline Active
- [ ] Manual deployment works
- [ ] Health checks pass
- [ ] Rollback procedure tested
- [ ] Auto-deployment enabled (optional)

---

**Need Help?** Check the [troubleshooting section](#-troubleshooting) or review detailed guides in the `docs/` folder.
