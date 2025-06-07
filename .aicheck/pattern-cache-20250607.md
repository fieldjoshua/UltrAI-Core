# Frequently Used Patterns Cache

## Code Patterns
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:Tests all UI/UX features to ensure frontend functionality is preserved.
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:class TestFrontendMVPFeatures:
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def driver(self):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_core_pages_accessible(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_analysis_workflow(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_model_selector_functionality(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_document_upload_component(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:        """Test document upload functionality."""
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_results_display_views(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_error_handling_ui(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_responsive_design(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_export_functionality(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_loading_states(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_keyboard_navigation(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:        assert "focus" in focused_element.get_attribute("class")
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:class TestFrontendPerformance:
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_page_load_time(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_js_bundle_size(self, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:    def test_api_response_times(self, driver, base_url):
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:            const originalFetch = window.fetch;

## Import Patterns  
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:from typing import Any, Dict
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:import pytest
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:import requests
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:from selenium import webdriver
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:from selenium.common.exceptions import TimeoutException
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:from selenium.webdriver.common.by import By
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:from selenium.webdriver.support import expected_conditions as EC
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:from selenium.webdriver.support.ui import WebDriverWait
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:        """Test complete analysis workflow from start to finish."""
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:        import time
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:        import requests
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:        """Test API response times from frontend."""
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:        # Check important elements have ARIA labels
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:        important_elements = ["button", "input", "select", "nav"]
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py:        for element_type in important_elements:

## Test Patterns
./.aicheck/.aicheck_backup_20250524_095556/scripts/test_pre_commit.sh
./.aicheck/.aicheck_backup_20250524_095556/scripts/test_security.sh
./.aicheck/.aicheck_backup_20250524_095556/scripts/test_all.sh
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/frontend-tests.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/complete-mvp-validation-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/test-minimal-deployment.sh
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/mvp-minimal-tests.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/deployment-validation-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/resource-monitoring-test.py
./.aicheck/.aicheck_backup_20250524_095556/actions/mvp-minimal-deployment/supporting_docs/test_minimal_deployment.py

*Cache generated: Sat Jun  7 09:34:21 PDT 2025*
