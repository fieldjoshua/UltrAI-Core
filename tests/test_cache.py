#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.

"""Tests for stevedore._cache
"""
import sys
from unittest import mock
import pytest
from datetime import datetime, timedelta
from src.models import ResponseCache, ModelResponse, QualityMetrics

from stevedore import _cache
from stevedore.tests import utils


class TestCache(utils.TestCase):
    def test_disable_caching_executable(self):
        """Test caching is disabled if python interpreter is located under /tmp
        directory (Ansible)
        """
        with mock.patch.object(sys, "executable", "/tmp/fake"):
            sot = _cache.Cache()
            self.assertTrue(sot._disable_caching)

    def test_disable_caching_file(self):
        """Test caching is disabled if .disable file is present in target
        dir
        """
        cache_dir = _cache._get_cache_dir()

        with mock.patch("os.path.isfile") as mock_path:
            mock_path.return_value = True
            sot = _cache.Cache()
            mock_path.assert_called_with("%s/.disable" % cache_dir)
            self.assertTrue(sot._disable_caching)

            mock_path.return_value = False
            sot = _cache.Cache()
            self.assertFalse(sot._disable_caching)

    @mock.patch("os.makedirs")
    @mock.patch("builtins.open")
    def test__get_data_for_path_no_write(self, mock_open, mock_mkdir):
        sot = _cache.Cache()
        sot._disable_caching = True
        mock_open.side_effect = IOError
        sot._get_data_for_path("fake")
        mock_mkdir.assert_not_called()

    def test__build_cacheable_data(self):
        # this is a rubbish test as we don't actually do anything with the
        # data, but it's too hard to script since it's totally environmentally
        # dependent and mocking out the underlying calls would remove the value
        # of this test (we want to test those underlying API calls)
        ret = _cache._build_cacheable_data()
        self.assertIsInstance(ret["groups"], dict)


@pytest.fixture
def cache():
    return ResponseCache(max_age_hours=1)


@pytest.fixture
def sample_response():
    return ModelResponse(
        model_name="TestModel",
        content="Test content",
        stage="test",
        timestamp=datetime.now().timestamp(),
        tokens_used=100,
        quality=QualityMetrics(
            coherence_score=0.8,
            technical_depth=0.9,
            strategic_value=0.85,
            uniqueness=0.75,
        ),
    )


def test_cache_initialization(cache):
    assert cache.max_age_hours == 1
    assert isinstance(cache.cache, dict)
    assert len(cache.cache) == 0


def test_cache_set_get(cache, sample_response):
    key = "test_key"
    cache.set(key, sample_response)
    retrieved = cache.get(key)

    assert retrieved is not None
    assert retrieved.model_name == sample_response.model_name
    assert retrieved.content == sample_response.content
    assert retrieved.stage == sample_response.stage
    assert retrieved.tokens_used == sample_response.tokens_used
    assert retrieved.quality.coherence_score == sample_response.quality.coherence_score


def test_cache_expiration(cache, sample_response):
    key = "test_key"
    cache.set(key, sample_response)

    # Simulate time passing
    cache.cache[key]["timestamp"] = datetime.now() - timedelta(hours=2)

    # Should return None as entry is expired
    assert cache.get(key) is None
    assert key not in cache.cache


def test_cache_clear_expired(cache, sample_response):
    # Add some entries
    cache.set("key1", sample_response)
    cache.set("key2", sample_response)

    # Make one entry expired
    cache.cache["key1"]["timestamp"] = datetime.now() - timedelta(hours=2)

    # Clear expired entries
    cache.clear_expired()

    assert "key1" not in cache.cache
    assert "key2" in cache.cache


def test_cache_nonexistent_key(cache):
    assert cache.get("nonexistent_key") is None


def test_cache_update_existing(cache, sample_response):
    key = "test_key"

    # First set
    cache.set(key, sample_response)

    # Update with new response
    new_response = ModelResponse(
        model_name="UpdatedModel",
        content="Updated content",
        stage="test",
        timestamp=datetime.now().timestamp(),
        tokens_used=200,
    )
    cache.set(key, new_response)

    retrieved = cache.get(key)
    assert retrieved.model_name == "UpdatedModel"
    assert retrieved.content == "Updated content"
    assert retrieved.tokens_used == 200
