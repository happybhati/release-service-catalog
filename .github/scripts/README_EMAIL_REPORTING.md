# Email Reporting System for Release Service Catalog

This system automatically generates and sends comprehensive email reports for branch promotions in the release-service-catalog repository. It combines AI-powered commit summarization with task-pipeline impact analysis to provide professional, human-readable reports.

## Features

- 🤖 **AI-Powered Summarization**: Uses OpenRouter API to generate intelligent, consistent summaries
- 📊 **Task-Pipeline Analysis**: Automatically identifies which tasks were changed and their pipeline impact
- 📧 **Professional Email Templates**: Beautiful HTML emails with statistics and links
- 🔄 **Automated Integration**: Works seamlessly with existing promotion workflows
- 📅 **Scheduled Reports**: Optional weekly automated promotions with reports
- 🎯 **Consistent Formatting**: Maintains professional, structured format every week

## Quick Start

### 1. Environment Setup

Set up the required environment variables in your GitHub repository secrets:

```bash
# Required for AI summarization
OPENROUTER_API_KEY=your_openrouter_api_key

# Required for email sending
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=release-reports@konflux-ci.com
EMAIL_TO=team@company.com,manager@company.com

# Required for GitHub operations
GH_TOKEN=your_github_token
```

### 2. Manual Usage

Generate a promotion report manually:

```bash
# For development to staging promotion
python .github/scripts/generate_promotion_report.py development staging

# For staging to production promotion
python .github/scripts/generate_promotion_report.py staging production
```

### 3. Automated Workflow

Use the enhanced GitHub Actions workflow:

1. Go to Actions → "Promote branch with automated reporting"
2. Select promotion type and options
3. Enable "Send email report"
4. Run the workflow

## Configuration

### Email Configuration

Edit `.github/scripts/report_config.yaml` to customize:

- AI model settings
- Email templates
- Report content options
- Task analysis patterns
- Notification integrations

### SMTP Setup

For Gmail:
1. Enable 2-factor authentication
2. Generate an App Password
3. Use the App Password as `SMTP_PASSWORD`

For other providers:
- Update `SMTP_SERVER` and `SMTP_PORT` in the config
- Use appropriate credentials

## Report Structure

Each email report includes:

### 📊 Statistics Section
- Number of commits
- Number of contributors
- Total files changed

### 📋 Executive Summary
AI-generated summary with:
- Key themes and business impact
- Most significant changes
- Professional, non-technical language

### 🧩 Task Impact Analysis
Table showing:
- Changed tasks with links
- Task types (managed, tenant, internal, collectors)
- Affected pipelines
- Pipeline count

### 🔗 References
- Links to all commits
- Repository links
- Pipeline and task documentation

## AI Summarization

The system uses OpenRouter API with Llama 3.1 8B Instruct model to:

- **Categorize changes** into logical groups
- **Generate executive summaries** in business language
- **Maintain consistency** across reports
- **Focus on impact** rather than technical details

### Customizing AI Prompts

Edit the system prompts in `generate_promotion_report.py`:

```python
def _get_system_prompt(self, promotion_type: str) -> str:
    return f"""
    You are a professional DevOps engineer creating a weekly promotion report...
    """
```

## Task-Pipeline Analysis

The system automatically:

1. **Scans commits** for task file changes
2. **Parses pipeline YAML** files to find task references
3. **Maps relationships** between changed tasks and pipelines
4. **Generates impact tables** with clickable links

### Supported Task Types

- `managed/` - Managed tasks
- `tenant/` - Tenant-specific tasks  
- `internal/` - Internal tasks
- `collectors/` - Data collection tasks

## Weekly Automation

Enable scheduled weekly promotions:

1. The workflow runs every Wednesday at 10:00 UTC
2. Promotes development → staging → production
3. Generates reports for each promotion
4. Sends email notifications
5. Creates GitHub releases for production

### Customizing Schedule

Edit the workflow file to change:
- Day of week (currently Wednesday)
- Time (currently 10:00 UTC)
- Promotion sequence

## Integration with Existing Scripts

This system enhances your existing scripts:

- **`collect_commits_with_diff.py`** - Enhanced with better error handling
- **`summarize_commits.py`** - Improved AI prompts and formatting
- **`generate_task_pipeline_table.py`** - Integrated into main workflow

## Troubleshooting

### Common Issues

1. **Email not sending**
   - Check SMTP credentials
   - Verify firewall settings
   - Test with a simple email first

2. **AI summary fails**
   - Verify OpenRouter API key
   - Check API quota limits
   - Review commit data format

3. **Task analysis empty**
   - Verify task file patterns
   - Check pipeline YAML structure
   - Review file paths

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
python .github/scripts/generate_promotion_report.py development staging
```

### Testing

Test the system locally:

```bash
# Test commit collection
python .github/scripts/collect_commits_with_diff.py development staging

# Test AI summarization
python .github/scripts/summarize_commits.py commits.json

# Test full workflow
python .github/scripts/generate_promotion_report.py development staging
```

## Advanced Features

### Custom Notifications

Add Slack, Teams, or Discord notifications:

```yaml
notifications:
  slack:
    enabled: true
    webhook_url: "your_webhook_url"
    channel: "#releases"
```

### Report Customization

Customize report content:

```yaml
report:
  include_commit_links: true
  include_task_analysis: true
  include_pipeline_impact: true
  include_statistics: true
```

### Performance Optimization

Configure for large repositories:

```yaml
performance:
  max_parallel_commits: 20
  enable_caching: true
  cache_duration: 7200
```

## Security Considerations

- Store sensitive credentials in GitHub Secrets
- Use App Passwords instead of regular passwords
- Limit email recipients to necessary team members
- Review AI-generated content before sending
- Monitor API usage and costs

## Contributing

To enhance the system:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Development Setup

```bash
# Install dependencies
pip install requests pyyaml

# Set up environment
export OPENROUTER_API_KEY=your_key
export SMTP_USERNAME=your_email
export SMTP_PASSWORD=your_password

# Run tests
python -m pytest tests/
```

## Support

For issues and questions:

1. Check the troubleshooting section
2. Review GitHub Actions logs
3. Test components individually
4. Create an issue with detailed information

## License

This system is part of the release-service-catalog project and follows the same license terms. 