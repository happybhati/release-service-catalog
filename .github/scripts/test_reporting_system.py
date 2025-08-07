#!/usr/bin/env python3
"""
Test script for the email reporting system
==========================================

This script tests the various components of the email reporting system
to ensure everything works correctly before deployment.
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

# Add the scripts directory to the path
sys.path.insert(0, Path(__file__).parent)

try:
    from generate_promotion_report import (
        CommitCollector, AISummarizer, TaskPipelineAnalyzer, 
        EmailGenerator, EmailSender
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the repository root")
    sys.exit(1)

def test_commit_collector():
    """Test the commit collector functionality."""
    print("🧪 Testing CommitCollector...")
    
    try:
        collector = CommitCollector(Path.cwd())
        print("✅ CommitCollector initialized successfully")
        
        # Test git command execution
        result = collector.run_git_command(["git", "--version"])
        if "git version" in result:
            print("✅ Git command execution works")
        else:
            print("❌ Git command execution failed")
            return False
            
    except Exception as e:
        print(f"❌ CommitCollector test failed: {e}")
        return False
    
    return True

def test_ai_summarizer():
    """Test the AI summarizer functionality."""
    print("🧪 Testing AISummarizer...")
    
    # Check if API key is available
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("⚠️ OPENROUTER_API_KEY not set, skipping AI test")
        return True
    
    try:
        summarizer = AISummarizer()
        print("✅ AISummarizer initialized successfully")
        
        # Test prompt generation
        test_commits = [
            {
                "summary": "Add new task for data collection",
                "author": "Test User",
                "email": "test@example.com",
                "date": "2024-01-01",
                "url": "https://github.com/test/commit/123",
                "files": ["tasks/managed/test-task/test-task.yaml"],
                "message": "Add new task for data collection\n\nThis task will collect data from various sources.",
                "diffstat": "1 file changed, 10 insertions(+), 2 deletions(-)"
            }
        ]
        
        system_prompt = summarizer._get_system_prompt("development-to-staging")
        user_prompt = summarizer._build_user_prompt(test_commits)
        
        if "professional DevOps engineer" in system_prompt:
            print("✅ System prompt generation works")
        else:
            print("❌ System prompt generation failed")
            return False
            
        if "Add new task for data collection" in user_prompt:
            print("✅ User prompt generation works")
        else:
            print("❌ User prompt generation failed")
            return False
            
    except Exception as e:
        print(f"❌ AISummarizer test failed: {e}")
        return False
    
    return True

def test_task_pipeline_analyzer():
    """Test the task-pipeline analyzer functionality."""
    print("🧪 Testing TaskPipelineAnalyzer...")
    
    try:
        analyzer = TaskPipelineAnalyzer(Path.cwd())
        print("✅ TaskPipelineAnalyzer initialized successfully")
        
        # Test with sample commits
        test_commits = [
            {
                "files": ["tasks/managed/test-task/test-task.yaml"],
                "hash": "1234567890abcdef",
                "url": "https://github.com/test/commit/123"
            }
        ]
        
        result = analyzer.analyze_changes(test_commits)
        
        if isinstance(result, dict) and "changed_tasks" in result:
            print("✅ Task analysis works")
        else:
            print("❌ Task analysis failed")
            return False
            
    except Exception as e:
        print(f"❌ TaskPipelineAnalyzer test failed: {e}")
        return False
    
    return True

def test_email_generator():
    """Test the email generator functionality."""
    print("🧪 Testing EmailGenerator...")
    
    try:
        generator = EmailGenerator()
        print("✅ EmailGenerator initialized successfully")
        
        # Test email content generation
        test_commits = [
            {
                "summary": "Test commit",
                "author": "Test User",
                "email": "test@example.com",
                "date": "2024-01-01",
                "files": ["test.yaml"],
                "url": "https://github.com/test/commit/123",
                "hash": "1234567890abcdef",
                "message": "Test commit message",
                "diffstat": "1 file changed"
            }
        ]
        
        test_summary = "This is a test summary with some content."
        test_task_analysis = {
            "changed_tasks": [],
            "pipeline_impact": {}
        }
        
        email_content = generator.generate_email_content(
            "development-to-staging",
            test_commits,
            test_summary,
            test_task_analysis
        )
        
        if "Release Service Catalog" in email_content and "Test commit" in email_content:
            print("✅ Email content generation works")
        else:
            print("❌ Email content generation failed")
            return False
            
    except Exception as e:
        print(f"❌ EmailGenerator test failed: {e}")
        return False
    
    return True

def test_email_sender():
    """Test the email sender functionality."""
    print("🧪 Testing EmailSender...")
    
    # Check if email credentials are available
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_username or not smtp_password:
        print("⚠️ SMTP credentials not set, skipping email sender test")
        return True
    
    try:
        sender = EmailSender()
        print("✅ EmailSender initialized successfully")
        
        # Test email sending (this would actually send an email)
        # Uncomment the following lines to test actual email sending
        """
        success = sender.send_email(
            "Test Email",
            "<h1>Test</h1><p>This is a test email.</p>",
            ["test@example.com"]
        )
        
        if success:
            print("✅ Email sending works")
        else:
            print("❌ Email sending failed")
            return False
        """
        
        print("✅ EmailSender configuration valid (actual sending skipped)")
        
    except Exception as e:
        print(f"❌ EmailSender test failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading."""
    print("🧪 Testing Configuration...")
    
    config_file = Path(__file__).parent / "report_config.yaml"
    
    if not config_file.exists():
        print("❌ Configuration file not found")
        return False
    
    try:
        import yaml
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        required_sections = ["ai", "email", "report", "repository"]
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing configuration section: {section}")
                return False
        
        print("✅ Configuration file is valid")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

def test_integration():
    """Test the full integration workflow."""
    print("🧪 Testing Integration Workflow...")
    
    try:
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Test the main workflow components
            collector = CommitCollector(temp_path)
            analyzer = TaskPipelineAnalyzer(temp_path)
            generator = EmailGenerator()
            
            # Test with mock data
            mock_commits = [
                {
                    "summary": "Integration test commit",
                    "author": "Test User",
                    "email": "test@example.com",
                    "date": "2024-01-01",
                    "files": ["tasks/managed/test/test.yaml"],
                    "url": "https://github.com/test/commit/123",
                    "message": "Test commit message",
                    "diffstat": "1 file changed",
                    "hash": "1234567890abcdef"
                }
            ]
            
            # Test task analysis
            task_analysis = analyzer.analyze_changes(mock_commits)
            
            # Test email generation
            email_content = generator.generate_email_content(
                "development-to-staging",
                mock_commits,
                "Test summary",
                task_analysis
            )
            
            if email_content and "Integration test commit" in email_content:
                print("✅ Integration workflow works")
            else:
                print("❌ Integration workflow failed")
                return False
                
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🚀 Starting Email Reporting System Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("CommitCollector", test_commit_collector),
        ("AISummarizer", test_ai_summarizer),
        ("TaskPipelineAnalyzer", test_task_pipeline_analyzer),
        ("EmailGenerator", test_email_generator),
        ("EmailSender", test_email_sender),
        ("Integration", test_integration),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name} test...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} test passed")
        else:
            print(f"❌ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready for use.")
        return 0
    else:
        print("⚠️ Some tests failed. Please review the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 