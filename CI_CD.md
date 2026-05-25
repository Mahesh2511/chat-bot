# CI/CD Pipeline Guide

Complete guide to set up, run, and troubleshoot the GitHub Actions CI/CD pipeline for deploying this chatbot to AWS EC2.

---

## Overview

Two separate workflow files handle CI and CD independently:

```
Manual trigger
      ↓
 .github/workflows/ci.yml   — Continuous Integration
  • Checkout code
  • Install Python dependencies
  • Build Docker image
  • Push to Docker Hub (pawarmahesh2511/chatbot-app:<sha>)
      ↓  (auto-triggers on CI success via workflow_run)
 .github/workflows/cd.yml   — Continuous Deployment
  • Copy docker-compose.yml to EC2 via SCP
  • SSH into EC2
  • Generate .env from GitHub Secrets
  • docker pull <image>
  • docker-compose down && up -d
  • Health check (10 retries, 15s initial wait)
```

---

## Prerequisites

### 1. AWS EC2 Instance

- **OS**: Ubuntu Server LTS or Amazon Linux 2023
- **Minimum disk**: 20 GB (CUDA libraries from sentence-transformers are ~3-4 GB)
- **Ports open** (Security Group inbound rules):
  - Port `22` — SSH
  - Port `8000` — Application

### 2. Docker installed on EC2

```bash
# Amazon Linux 2023
sudo yum install -y docker
sudo systemctl enable docker
sudo systemctl start docker
sudo usermod -aG docker ec2-user
# Log out and back in for group change to take effect

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 3. Docker Hub Account

Create a free account at hub.docker.com and generate an access token:
**Account Settings → Security → New Access Token**

### 4. LLM API Key

**Free option (recommended)**: Groq — get a free key at `console.groq.com`

**Paid option**: OpenAI — add credits at `platform.openai.com/settings/billing`

> Note: OpenAI API billing is separate from ChatGPT subscriptions. A ChatGPT Plus/Pro subscription does NOT give free API access.

---

## GitHub Secrets Setup

Go to: **GitHub repo → Settings → Secrets and variables → Actions → New repository secret**

### Required Secrets

| Secret | Description | Example |
|--------|-------------|---------|
| `EC2_HOST` | EC2 public IP or hostname | `65.1.135.113` |
| `EC2_USERNAME` | SSH user | `ec2-user` or `ubuntu` |
| `EC2_SSH_KEY` | Full contents of `.pem` key file | `-----BEGIN RSA PRIVATE KEY-----...` |
| `DOCKERHUB_USERNAME` | Docker Hub username | `pawarmahesh2511` |
| `DOCKERHUB_TOKEN` | Docker Hub access token | `dckr_pat_...` |
| `LLM_PROVIDER` | LLM backend | `groq` |
| `LLM_MODEL` | Model name | `llama-3.1-8b-instant` |
| `GROQ_API_KEY` | Groq API key | `gsk_...` |
| `EMBEDDING_PROVIDER` | Embedding backend | `huggingface` |
| `EMBEDDING_MODEL` | Embedding model | `all-MiniLM-L6-v2` |

### Optional Secrets

| Secret | Description |
|--------|-------------|
| `OPENAI_API_KEY` | If using OpenAI as LLM provider |
| `ANTHROPIC_API_KEY` | If using Anthropic as LLM provider |
| `REDIS_PASSWORD` | Only if Redis is password-protected (leave empty if not) |

---

## Running the Pipeline

### Trigger CI manually

1. Go to **GitHub → Actions → CI Pipeline**
2. Click **Run workflow → Run workflow**
3. Watch CI complete (build + Docker push ~3-5 min)
4. CD triggers automatically after CI succeeds (~2-3 min)

### Verify deployment

```bash
curl http://<EC2_HOST>:8000/health
# Expected: {"status":"ok"}
```

Open the UI: `http://<EC2_HOST>:8000`

---

## EC2 Volume Expansion

Default EC2 volumes are 8 GB which is insufficient for this stack. Expand to 20 GB:

### Step 1 — AWS Console

1. EC2 → Instances → click your instance → **Storage** tab
2. Click the Volume ID → **Actions → Modify Volume**
3. Change size to **20** → **Modify → Yes**

### Step 2 — Apply on EC2 (SSH in)

```bash
lsblk   # identify disk name

# For nvme0n1 (Amazon Linux 2023 / modern EC2):
sudo growpart /dev/nvme0n1 1
sudo xfs_growfs /          # Amazon Linux uses XFS

# For xvda (older EC2):
sudo growpart /dev/xvda 1
sudo resize2fs /dev/xvda1  # Ubuntu uses ext4

df -h   # confirm new size
```

---

## S3 PDF Access

The ingest endpoint downloads PDFs directly from S3. The file must be publicly accessible.

### Make S3 file public via Bucket Policy

1. **S3 → bucket → Permissions → Block public access → Edit**
   - Uncheck all 4 options → Save
2. **Permissions → Bucket Policy → Edit**, paste:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/*"
    }
  ]
}
```

Replace `YOUR-BUCKET-NAME` with your actual bucket name.

---

## Troubleshooting

### No space left on device (during docker pull)

**Error**: `failed to register layer: write /usr/local/lib/python3.10/site-packages/nvidia/...: no space left on device`

**Cause**: EC2 disk full — sentence-transformers pulls CUDA/nvidia libraries (~3-4 GB).

**Fix**:
```bash
docker system prune -af --volumes   # free all unused Docker data
df -h                               # verify free space
```

If disk is still small, expand the EC2 volume (see EC2 Volume Expansion above).

**Long-term fix**: The Dockerfile installs CPU-only PyTorch before requirements.txt to avoid pulling CUDA libraries:
```dockerfile
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt
```

---

### Redis AUTH error on startup

**Error**: `AUTH <password> called without any password configured for the default user`

**Cause**: `REDIS_PASSWORD` GitHub Secret is set to a non-empty value, but the Redis container has no password configured.

**Fix**: Go to GitHub Secrets → set `REDIS_PASSWORD` to empty/blank, then redeploy.

---

### ChromaDB tenant error on startup

**Error**: `ValueError: Could not connect to tenant default_tenant. Are you sure it exists?`

**Cause**: Incompatibility between `langchain_chroma` and ChromaDB 1.x when using `persist_directory` directly.

**Fix** (already applied in `db/vector.py`): Explicitly create the ChromaDB `PersistentClient` and pass it in:
```python
client = chromadb.PersistentClient(path=setting.chroma_persist_dir)
return Chroma(client=client, collection_name=..., embedding_function=...)
```

---

### Health check fails after deployment

**Error**: `Health check failed after N attempts`

**Cause**: App container takes time to start (model loading). The health check fires before the app is ready.

**Fix** (already applied in `cd.yml`): Added 15-second initial wait + 10 retries with 10-second gaps.

**Manual check**:
```bash
docker logs chatbot-api-1 --tail 30   # check app startup logs
curl http://localhost:8000/health      # test from EC2 directly
```

---

### S3 ingest returns 403 Forbidden

**Error**: `403 Client Error: Forbidden for url: https://...s3.amazonaws.com/....pdf`

**Cause**: S3 file is private (default).

**Fix**: Apply the bucket policy above to make the file publicly readable.

---

### Ingest API returns 422 Unprocessable Entity

**Cause**: Request validation failed. Common reasons:
- `file_name` contains dots or slashes (e.g. `test.pdf` → use `test`)
- `s3_url` does not end in `.pdf`
- Either field is empty

**Fix**: Use a plain name with no extension for `file_name` (e.g. `company-policy`, `internet-evolution`).

---

### Ingest status message not showing in UI

**Cause**: Inline `style.display` was overriding CSS class display rules.

**Fix** (already applied in `static/index.html`): `showIngestStatus()` now clears the inline style before setting the class.

---

### OpenAI API key exists but calls fail

**Error**: `Error 429: You exceeded your current quota`

**Cause**: OpenAI API billing is separate from ChatGPT subscriptions. Generating a key is free but using it requires a paid credit balance.

**Fix**: Either add credits at `platform.openai.com/settings/billing`, or switch to Groq (free):
```
LLM_PROVIDER=groq
LLM_MODEL=llama-3.1-8b-instant
GROQ_API_KEY=<from console.groq.com>
```
