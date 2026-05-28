# 🔄 Omega Prime CI/CD Pipeline - Complete Guide

## 📋 Table of Contents

1. [Overview](#overview)
2. [Pipeline Stages](#pipeline-stages)
3. [Setup Instructions](#setup-instructions)
4. [Deployment Workflow](#deployment-workflow)
5. [Troubleshooting](#troubleshooting)
6. [Best Practices](#best-practices)

---

## 🌟 Overview

The Omega Prime CI/CD pipeline is a comprehensive, production-ready automation system that handles:

- ✅ Code quality checks
- ✅ Security scanning
- ✅ Automated testing
- ✅ Docker image building
- ✅ Multi-environment deployment
- ✅ Release management

### Pipeline Diagram

```
┌─────────────┐
│   Push/PR   │
└──────┬──────┘
       │
       ├─────────────────────────────────────┐
       │                                     │
┌──────▼──────────┐                ┌────────▼────────┐
│ Code Quality    │                │ Build & Test    │
│ - StyleCop      │                │ - Unit Tests    │
│ - Security Scan │                │ - Coverage      │
│ - Secret Check  │                │ - Multi-OS      │
└──────┬──────────┘                └────────┬────────┘
       │                                     │
       └─────────────┬───────────────────────┘
                     │
              ┌──────▼──────────┐
              │ Docker Build    │
              │ - Multi-arch    │
              │ - Push to GHCR  │
              │ - Trivy Scan    │
              └──────┬──────────┘
                     │
         ┌───────────┼───────────┐
         │                       │
  ┌──────▼──────┐       ┌───────▼────────┐
  │Integration  │       │ Performance    │
  │   Tests     │       │    Tests       │
  └──────┬──────┘       └───────┬────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼────────────┐
         │   Deploy Staging       │
         │   (develop branch)     │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │  Deploy Production     │
         │   (tags only)          │
         └───────────┬────────────┘
                     │
         ┌───────────▼────────────┐
         │   Create Release       │
         │   (GitHub Release)     │
         └────────────────────────┘
```

---

## 🔧 Pipeline Stages

### Stage 1: Code Quality & Security (5-10 min)

**Triggers:** Every push and PR

**Actions:**
- ✅ Code style analysis (StyleCop)
- ✅ Dependency vulnerability scan
- ✅ Secret scanning (TruffleHog)
- ✅ CodeQL analysis

**Artifacts:**
- `security-scan-results` - Vulnerability report

### Stage 2: Build & Test (10-15 min)

**Triggers:** Every push and PR

**Actions:**
- ✅ Build on Ubuntu, Windows, macOS
- ✅ Run unit tests with coverage
- ✅ Upload coverage to Codecov
- ✅ Comment coverage on PRs

**Artifacts:**
- `test-results-{os}` - Test reports
- Code coverage reports

### Stage 3: Docker Build (5-10 min)

**Triggers:** Push to main/develop, tags

**Actions:**
- ✅ Build multi-architecture images (amd64, arm64)
- ✅ Push to GitHub Container Registry
- ✅ Scan for vulnerabilities (Trivy)
- ✅ Upload SARIF to GitHub Security

**Artifacts:**
- Docker images in GHCR
- `trivy-results.sarif`

### Stage 4: Integration Tests (10-15 min)

**Triggers:** After Docker build

**Actions:**
- ✅ Spin up PostgreSQL and Redis
- ✅ Run integration tests
- ✅ Verify database connections

**Artifacts:**
- `integration-test-results`

### Stage 5: Performance Tests (8-10 min)

**Triggers:** Push to main branch

**Actions:**
- ✅ Load testing with k6
- ✅ Verify response times
- ✅ Check error rates

**Artifacts:**
- `performance-test-results.json`

### Stage 6: Deploy Staging (5 min)

**Triggers:** Push to develop branch

**Actions:**
- ✅ Deploy to Kubernetes staging
- ✅ Verify deployment
- ✅ Run smoke tests

**Environment:** `staging`

### Stage 7: Deploy Production (10 min)

**Triggers:** Push tags (v*.*.*)

**Actions:**
- ✅ Create database backup
- ✅ Deploy to Kubernetes production
- ✅ Run smoke tests
- ✅ Send Slack notification

**Environment:** `production`

### Stage 8: Create Release (2 min)

**Triggers:** After production deployment

**Actions:**
- ✅ Generate changelog
- ✅ Create GitHub release
- ✅ Attach release notes

---

## 🚀 Setup Instructions

### Step 1: Fork/Clone Repository

```bash
git clone https://github.com/your-org/omega-prime.git
cd omega-prime
```

### Step 2: Configure GitHub Secrets

See [GITHUB_SECRETS_SETUP.md](GITHUB_SECRETS_SETUP.md) for detailed instructions.

**Required secrets:**
```bash
gh secret set OMEGA_SECRET_KEY_TEST
gh secret set AWS_ACCESS_KEY_ID       # Optional (for AWS deployment)
gh secret set AWS_SECRET_ACCESS_KEY   # Optional (for AWS deployment)
gh secret set SLACK_WEBHOOK           # Optional (for notifications)
```

### Step 3: Enable GitHub Actions

1. Go to **Settings** → **Actions** → **General**
2. Set "Actions permissions" to "Allow all actions and reusable workflows"
3. Save

### Step 4: Configure Environments

#### Create Staging Environment

```bash
# Via GitHub CLI
gh api repos/{owner}/{repo}/environments/staging --method PUT

# Via UI: Settings → Environments → New environment
```

Settings:
- Name: `staging`
- URL: `https://staging.omega-prime.example.com`
- Branch restrictions: `develop`

#### Create Production Environment

```bash
gh api repos/{owner}/{repo}/environments/production --method PUT
```

Settings:
- Name: `production`
- URL: `https://omega-prime.example.com`
- Required reviewers: Add yourself
- Branch restrictions: Tags only (`refs/tags/v*`)

### Step 5: Enable Branch Protection

```bash
# Protect main branch
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks[strict]=true \
  --field required_status_checks[contexts][]=build-and-test \
  --field required_status_checks[contexts][]=code-quality \
  --field required_pull_request_reviews[required_approving_review_count]=1
```

---

## 🔄 Deployment Workflow

### Development Flow

```bash
# 1. Create feature branch
git checkout -b feature/new-feature

# 2. Make changes and commit
git add .
git commit -m "feat: add new feature"

# 3. Push and create PR
git push origin feature/new-feature
gh pr create --title "Add new feature" --body "Description"

# 4. Wait for CI checks ✅
# 5. Merge to develop (auto-deploy to staging)
gh pr merge --squash

# 6. Test in staging
curl https://staging.omega-prime.example.com/health
```

### Release Flow

```bash
# 1. Create release branch from develop
git checkout develop
git pull
git checkout -b release/v2.1.0

# 2. Update version numbers
# Edit version in .csproj, README, etc.

# 3. Commit and push
git commit -am "chore: bump version to 2.1.0"
git push origin release/v2.1.0

# 4. Create PR to main
gh pr create --base main --title "Release v2.1.0"

# 5. After approval, merge to main
gh pr merge --merge

# 6. Create tag
git checkout main
git pull
git tag -a v2.1.0 -m "Release v2.1.0"
git push origin v2.1.0

# 7. CI/CD auto-deploys to production 🚀
```

### Hotfix Flow

```bash
# 1. Create hotfix from main
git checkout main
git checkout -b hotfix/critical-bug

# 2. Fix the bug
git commit -am "fix: critical security issue"

# 3. Create PR to main
gh pr create --base main --title "Hotfix: Critical bug"

# 4. After approval, merge and tag
gh pr merge --merge
git tag -a v2.0.1 -m "Hotfix v2.0.1"
git push origin v2.0.1

# 5. Merge back to develop
git checkout develop
git merge main
git push
```

---

## 🐛 Troubleshooting

### Issue: Pipeline Fails at "Code Quality"

**Symptom:**
```
Error: Vulnerable packages found!
```

**Solution:**
```bash
# Update vulnerable packages
dotnet list package --vulnerable
dotnet add package <PackageName> --version <LatestVersion>
```

### Issue: Docker Build Fails

**Symptom:**
```
Error: failed to solve: failed to resolve source metadata
```

**Solution:**
```bash
# Test build locally
docker build -t omega-test .

# Check Dockerfile syntax
docker build --check .
```

### Issue: Deployment to Kubernetes Fails

**Symptom:**
```
Error: Unable to connect to the server
```

**Solution:**
```bash
# Verify kubectl configuration
kubectl cluster-info

# Check AWS credentials
aws sts get-caller-identity

# Verify EKS cluster exists
aws eks describe-cluster --name omega-prod-cluster
```

### Issue: Tests Fail in CI but Pass Locally

**Symptom:**
```
Test failed: Connection timeout
```

**Solution:**
```bash
# Check for timing issues
# Add retries in tests
[Fact(Timeout = 5000)]

# Use TestContainers for dependencies
# Check environment variable differences
```

---

## 💡 Best Practices

### 1. Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new feature
fix: resolve bug
docs: update documentation
chore: update dependencies
test: add missing tests
refactor: restructure code
perf: improve performance
```

### 2. Pull Requests

- Keep PRs small and focused
- Write descriptive titles
- Include tests for new features
- Update documentation
- Request reviews from team members

### 3. Testing

```bash
# Always run tests locally before pushing
dotnet test

# Check code coverage
dotnet test /p:CollectCoverage=true

# Run integration tests
dotnet test --filter "Category=Integration"
```

### 4. Security

```bash
# Scan for vulnerabilities before committing
dotnet list package --vulnerable

# Never commit secrets
git secrets --scan

# Use .gitignore properly
echo ".env" >> .gitignore
```

### 5. Version Management

Use [Semantic Versioning](https://semver.org/):

- **MAJOR** (v1.0.0 → v2.0.0): Breaking changes
- **MINOR** (v1.0.0 → v1.1.0): New features
- **PATCH** (v1.0.0 → v1.0.1): Bug fixes

---

## 📊 Monitoring Pipeline Health

### View Pipeline Status

```bash
# Check recent runs
gh run list --limit 10

# View specific run
gh run view <run-id>

# Watch run in progress
gh run watch <run-id>
```

### Pipeline Metrics

Track these metrics:
- Build success rate: Target >95%
- Average build time: Target <20 min
- Test coverage: Target >80%
- Deployment frequency: Target 2-5x/week
- Mean time to recovery: Target <1 hour

---

## 🔗 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [.NET Testing Best Practices](https://learn.microsoft.com/en-us/dotnet/core/testing/)

---

## 📞 Support

For issues with the CI/CD pipeline:
1. Check [Troubleshooting](#troubleshooting) section
2. Review [GitHub Actions logs](https://github.com/your-org/omega-prime/actions)
3. Create an issue using bug report template
4. Contact DevOps team
