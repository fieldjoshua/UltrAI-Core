"""Test Data Factory for Integration Testing"""

import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from faker import Faker

fake = Faker()


class TestDataFactory:
    """Factory for generating test data"""

    @staticmethod
    def create_user_data(
        email: Optional[str] = None, password: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Create user registration data"""
        return {
            "email": email or fake.email(),
            "password": password or TestDataFactory.create_password(),
            "name": kwargs.get("name", fake.name()),
            "role": kwargs.get("role", "user"),
            **kwargs,
        }

    @staticmethod
    def create_password(length: int = 12) -> str:
        """Create a valid password"""
        # Ensure password meets requirements
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        password = [
            random.choice(string.ascii_uppercase),
            random.choice(string.ascii_lowercase),
            random.choice(string.digits),
            random.choice("!@#$%^&*"),
        ]

        # Fill remaining length
        for _ in range(length - 4):
            password.append(random.choice(chars))

        random.shuffle(password)
        return "".join(password)

    @staticmethod
    def create_document_data(
        title: Optional[str] = None,
        content: Optional[str] = None,
        doc_type: str = "pdf",
        **kwargs,
    ) -> Dict[str, Any]:
        """Create document metadata"""
        return {
            "title": title or fake.catch_phrase(),
            "content": content or fake.text(max_nb_chars=1000),
            "type": doc_type,
            "size": kwargs.get("size", random.randint(1000, 10000000)),
            "mime_type": kwargs.get("mime_type", f"application/{doc_type}"),
            "created_at": datetime.utcnow().isoformat(),
            **kwargs,
        }

    @staticmethod
    def create_analysis_request(
        document_id: Optional[str] = None,
        patterns: Optional[List[str]] = None,
        models: Optional[List[str]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create analysis request data"""
        default_patterns = ["summary", "insights", "recommendations"]
        default_models = ["gpt-4", "claude-3", "llama-2"]

        return {
            "document_id": document_id or str(uuid.uuid4()),
            "patterns": patterns
            or random.sample(
                default_patterns, k=random.randint(1, len(default_patterns))
            ),
            "models": models
            or random.sample(default_models, k=random.randint(1, len(default_models))),
            "priority": kwargs.get("priority", "normal"),
            "callback_url": kwargs.get("callback_url"),
            **kwargs,
        }

    @staticmethod
    def create_llm_request(
        prompt: Optional[str] = None, model: str = "gpt-4", **kwargs
    ) -> Dict[str, Any]:
        """Create LLM request data"""
        return {
            "model": model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt or fake.text(max_nb_chars=200)},
            ],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
            **kwargs,
        }

    @staticmethod
    def create_mock_llm_response(
        model: str = "gpt-4", content: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Create mock LLM response data"""
        return {
            "id": f"chat-{uuid.uuid4()}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": content or fake.text(max_nb_chars=500),
                    },
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": kwargs.get("prompt_tokens", random.randint(10, 100)),
                "completion_tokens": kwargs.get(
                    "completion_tokens", random.randint(50, 500)
                ),
                "total_tokens": kwargs.get("total_tokens", random.randint(60, 600)),
            },
        }

    @staticmethod
    def create_analysis_result(
        request_id: Optional[str] = None, status: str = "completed", **kwargs
    ) -> Dict[str, Any]:
        """Create analysis result data"""
        return {
            "request_id": request_id or str(uuid.uuid4()),
            "status": status,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "results": kwargs.get(
                "results",
                {
                    "summary": fake.text(max_nb_chars=200),
                    "insights": [fake.sentence() for _ in range(3)],
                    "recommendations": [fake.sentence() for _ in range(2)],
                },
            ),
            "metadata": kwargs.get(
                "metadata",
                {
                    "processing_time": random.uniform(0.5, 5.0),
                    "models_used": ["gpt-4", "claude-3"],
                    "token_usage": random.randint(100, 1000),
                },
            ),
            **kwargs,
        }

    @staticmethod
    def create_health_status(
        service: str = "api", status: str = "healthy", **kwargs
    ) -> Dict[str, Any]:
        """Create health status data"""
        return {
            "service": service,
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
            "version": kwargs.get("version", "1.0.0"),
            "uptime": kwargs.get("uptime", random.randint(1000, 100000)),
            "checks": kwargs.get(
                "checks",
                {
                    "database": "connected",
                    "redis": "connected",
                    "llm_providers": "available",
                },
            ),
            **kwargs,
        }

    @staticmethod
    def create_error_response(
        error_code: str = "INTERNAL_ERROR",
        message: Optional[str] = None,
        status_code: int = 500,
        **kwargs,
    ) -> Dict[str, Any]:
        """Create error response data"""
        return {
            "error": {
                "code": error_code,
                "message": message or fake.sentence(),
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": kwargs.get("request_id", str(uuid.uuid4())),
                "details": kwargs.get("details", {}),
            },
            "status_code": status_code,
        }

    @staticmethod
    def create_batch_data(
        factory_method: callable, count: int = 10, **kwargs
    ) -> List[Dict[str, Any]]:
        """Create batch of test data"""
        return [factory_method(**kwargs) for _ in range(count)]


class ScenarioDataFactory:
    """Factory for complete test scenarios"""

    @staticmethod
    def create_authentication_flow() -> Dict[str, Any]:
        """Create data for authentication flow"""
        user_data = TestDataFactory.create_user_data()

        return {
            "registration": user_data,
            "login": {"email": user_data["email"], "password": user_data["password"]},
            "invalid_login": {
                "email": user_data["email"],
                "password": "wrong_password",
            },
            "token_refresh": {"refresh_token": str(uuid.uuid4())},
        }

    @staticmethod
    def create_document_analysis_flow() -> Dict[str, Any]:
        """Create data for document analysis flow"""
        document = TestDataFactory.create_document_data()
        analysis_request = TestDataFactory.create_analysis_request(
            document_id=document.get("id", str(uuid.uuid4()))
        )

        return {
            "document": document,
            "upload": {
                "file": f"test_document_{uuid.uuid4()}.pdf",
                "metadata": document,
            },
            "analysis_request": analysis_request,
            "status_check": {
                "request_id": analysis_request.get("id", str(uuid.uuid4()))
            },
            "expected_result": TestDataFactory.create_analysis_result(
                request_id=analysis_request.get("id")
            ),
        }

    @staticmethod
    def create_concurrent_user_scenario(num_users: int = 10) -> Dict[str, Any]:
        """Create data for concurrent user testing"""
        users = []

        for i in range(num_users):
            user_data = TestDataFactory.create_user_data(
                email=f"concurrent_user_{i}@test.com"
            )
            users.append(
                {
                    "user": user_data,
                    "document": TestDataFactory.create_document_data(),
                    "analysis": TestDataFactory.create_analysis_request(),
                }
            )

        return {
            "users": users,
            "concurrent_operations": [
                "login",
                "upload_document",
                "request_analysis",
                "check_status",
            ],
        }

    @staticmethod
    def create_error_scenario() -> Dict[str, Any]:
        """Create data for error handling testing"""
        return {
            "invalid_auth": {"token": "invalid_token_12345"},
            "malformed_request": {
                "analysis_request": {
                    "document_id": None,  # Missing required field
                    "patterns": [],  # Empty array
                }
            },
            "resource_not_found": {
                "document_id": str(uuid.uuid4()),
                "analysis_id": str(uuid.uuid4()),
            },
            "rate_limit": {"requests_per_second": 100, "duration": 10},
        }

    @staticmethod
    def create_performance_scenario() -> Dict[str, Any]:
        """Create data for performance testing"""
        return {
            "small_document": TestDataFactory.create_document_data(
                content=fake.text(max_nb_chars=100), size=1000
            ),
            "medium_document": TestDataFactory.create_document_data(
                content=fake.text(max_nb_chars=10000), size=100000
            ),
            "large_document": TestDataFactory.create_document_data(
                content=fake.text(max_nb_chars=100000), size=10000000
            ),
            "load_profile": {
                "ramp_up": {"start_users": 1, "end_users": 100, "duration": 300},
                "sustained": {"users": 50, "duration": 600},
                "spike": {"normal_users": 10, "spike_users": 200, "spike_duration": 60},
            },
        }


# Convenience functions
def create_test_user(**kwargs) -> Dict[str, Any]:
    """Create test user data"""
    return TestDataFactory.create_user_data(**kwargs)


def create_test_document(**kwargs) -> Dict[str, Any]:
    """Create test document data"""
    return TestDataFactory.create_document_data(**kwargs)


def create_test_analysis(**kwargs) -> Dict[str, Any]:
    """Create test analysis request"""
    return TestDataFactory.create_analysis_request(**kwargs)


def create_auth_scenario() -> Dict[str, Any]:
    """Create authentication test scenario"""
    return ScenarioDataFactory.create_authentication_flow()


def create_analysis_scenario() -> Dict[str, Any]:
    """Create document analysis test scenario"""
    return ScenarioDataFactory.create_document_analysis_flow()


def create_concurrent_scenario(num_users: int = 10) -> Dict[str, Any]:
    """Create concurrent user test scenario"""
    return ScenarioDataFactory.create_concurrent_user_scenario(num_users)
