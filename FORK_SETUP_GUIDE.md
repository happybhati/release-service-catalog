# 🍴 Fork Setup Guide for Manual Email Reporting

## Step-by-Step Setup for Your Fork

### **Step 1: Repository Setup**

1. **Create your fork** (if not done):
   - Go to https://github.com/konflux-ci/release-service-catalog
   - Click "Fork" → Create fork in your account

2. **Prepare and push your changes**:
   ```bash
   # Add all your email reporting files
   git add .github/scripts/generate_promotion_report.py
   git add .github/scripts/test_reporting_system.py
   git add .github/scripts/report_config.yaml
   git add .github/scripts/README_EMAIL_REPORTING.md
   git add .github/workflows/promote_branch_with_report.yaml
   git add requirements.txt
   git add EMAIL_REPORTING_SOLUTION.md
   git add demo_script.py
   
   # Commit changes
   git commit -m "feat: Add AI-powered email reporting system"
   
   # Push to your fork
   git push fork development
   ```

### **Step 2: Add Repository Secrets**

Go to your fork: **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

**Required secrets:**
```
OPENROUTER_API_KEY = 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
GEMINI_API_KEY = AIzaSyDmsfE9xQg16xVrX5G3uQ39CFn7w1NANkU
SMTP_SERVER = smtp.gmail.com
SMTP_PORT = 587
SMTP_USERNAME = happysinghbhati@gmail.com
SMTP_PASSWORD = gqjpjvrkemcjyasr
EMAIL_FROM = happysinghbhati@gmail.com
EMAIL_TO = hbhati@redhat.com
GH_TOKEN = your_github_token_here
```

### **Step 3: Test the Workflow**

1. **Go to your fork's GitHub page**
2. **Click Actions tab**
3. **Find "Promote branch with automated reporting"**
4. **Click "Run workflow"**
5. **Select options:**
   - **Promotion type**: `development-to-staging` 
   - **Force to staging**: `false`
   - **Override**: `false`
   - **Dry run**: `false`
   - **Send email report**: `true`
6. **Click "Run workflow"**

### **Files Updated for Fork Testing**

✅ **`.github/workflows/promote_branch_with_report.yaml`**
- Added `GEMINI_API_KEY` environment variable
- Added `GH_TOKEN` for GitHub access
- Updated to use `requirements.txt` for dependencies

✅ **`requirements.txt`** 
- Contains all Python dependencies

✅ **All email reporting scripts** are ready

### **Expected Workflow Behavior**

1. **Checkout code** with full git history
2. **Install Python dependencies** from requirements.txt
3. **Run branch promotion** (development → staging)
4. **Generate email report** with AI summary
5. **Send email** to your configured address
6. **Upload artifacts** (HTML report, JSON data)

### **Troubleshooting**

If the workflow fails:

1. **Check secrets**: Make sure all required secrets are set
2. **Check logs**: Go to Actions → Failed run → View logs
3. **Test locally**: Use the commands we tested earlier
4. **Email issues**: Check SMTP credentials and Gmail app password

### **Success Indicators**

✅ **Workflow completes successfully**
✅ **Email received** at your configured address
✅ **Artifacts uploaded** (report files)
✅ **No error messages** in the logs

### **Next Steps After Success**

1. **Review the generated report**
2. **Test staging → production promotion**
3. **Create PR to upstream** (when ready)
4. **Add scheduled automation** (optional)