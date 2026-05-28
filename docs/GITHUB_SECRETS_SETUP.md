# 🔐 GitHub Secrets Configuration Guide

This guide explains all required secrets for the CI/CD pipeline.

## 📋 Required Secrets

### 🔑 Authentication & Security

#### `OMEGA_SECRET_KEY_TEST`
**Purpose:** Secret key for integration tests  
**Generate:**
```bash
openssl rand -base64 32
```
**Example:** `YourTestSecretKey123ABC...`

---

### ☁️ AWS Deployment (Optional - for EKS deployment)

#### `AWS_ACCESS_KEY_ID`
**Purpose:** AWS IAM access key  
**Get from:** AWS IAM Console → Users → Security Credentials  
**Example:** `AKIAIOSFODNN7EXAMPLE`

#### `AWS_SECRET_ACCESS_KEY`
**Purpose:** AWS IAM secret key  
**Get from:** AWS IAM Console (generated with access key)  
**Example:** `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

**Required IAM Permissions:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters",
        "eks:UpdateClusterConfig"
      ],
      "Resource": "*"
    }
  ]
}
```

---

### 📢 Notifications (Optional)

#### `SLACK_WEBHOOK`
**Purpose:** Send deployment notifications to Slack  
**Setup:**
1. Go to Slack → Apps → Incoming Webhooks
2. Create new webhook
3. Copy webhook URL

**Example:** `https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXX`

---

## 🚀 How to Add Secrets

### Via GitHub UI

1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter secret name and value
5. Click **Add secret**

### Via GitHub CLI

```bash
# Install GitHub CLI
brew install gh  # macOS
# or
sudo apt install gh  # Ubuntu

# Login
gh auth login

# Add secrets
gh secret set OMEGA_SECRET_KEY_TEST
gh secret set AWS_ACCESS_KEY_ID
gh secret set AWS_SECRET_ACCESS_KEY
gh secret set SLACK_WEBHOOK
```

---

## 🔍 Verify Secrets

Check if secrets are configured:

```bash
gh secret list
```

Expected output:
```
OMEGA_SECRET_KEY_TEST    Updated 2025-11-30
AWS_ACCESS_KEY_ID        Updated 2025-11-30
AWS_SECRET_ACCESS_KEY    Updated 2025-11-30
SLACK_WEBHOOK            Updated 2025-11-30
```

---

## 🌍 Environment-Specific Secrets

### Staging Environment

Go to: **Settings** → **Environments** → **staging**

Add these secrets:
- `OMEGA_DB_CONNECTION` - Staging database connection string
- `REDIS_URL` - Staging Redis URL

### Production Environment

Go to: **Settings** → **Environments** → **production**

Add these secrets:
- `OMEGA_DB_CONNECTION` - Production database connection string
- `REDIS_URL` - Production Redis URL

**⚠️ Important:** Enable **Required reviewers** for production!

---

## 🔒 Security Best Practices

1. **Rotate secrets regularly** (every 90 days)
2. **Never commit secrets** to git
3. **Use different secrets** for each environment
4. **Limit secret access** to necessary workflows only
5. **Enable branch protection** for main/production branches
6. **Use environment secrets** for sensitive production data
7. **Monitor secret usage** in Actions logs

---

## 📊 Secret Rotation Schedule

| Secret | Rotation Period | Next Rotation |
|--------|----------------|---------------|
| OMEGA_SECRET_KEY_TEST | 90 days | 2026-03-01 |
| AWS_ACCESS_KEY_ID | 180 days | 2026-06-01 |
| SLACK_WEBHOOK | Never (unless compromised) | N/A |

---

## 🆘 Troubleshooting

### Secret not found error

```
Error: Secret OMEGA_SECRET_KEY_TEST not found
```

**Solution:** Add the secret via GitHub UI or CLI

### Invalid AWS credentials

```
Error: The security token included in the request is invalid
```

**Solution:** 
1. Verify IAM user has correct permissions
2. Check access key is active
3. Regenerate access key if needed

### Slack notification not working

```
Error: Slack webhook failed with status 404
```

**Solution:**
1. Verify webhook URL is correct
2. Check webhook is not disabled in Slack
3. Regenerate webhook if needed

---

## 📝 Notes

- **GITHUB_TOKEN** is automatically provided by GitHub Actions
- No need to create it manually
- It has limited permissions by default
- Increase permissions in workflow file if needed:

```yaml
permissions:
  contents: write
  packages: write
  security-events: write
```
