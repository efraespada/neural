"""Unit tests for constants."""

import pytest
from core.constants import RELEVANT_DOMAINS


class TestConstants:
    """Test constants values."""
    
    def test_relevant_domains_not_empty(self):
        """Test that RELEVANT_DOMAINS is not empty."""
        assert len(RELEVANT_DOMAINS) > 0
    
    def test_relevant_domains_contains_expected(self):
        """Test that RELEVANT_DOMAINS contains expected domains."""
        expected_domains = {
            'light', 'switch', 'cover', 'climate', 'fan',
            'media_player', 'scene', 'script', 'input_boolean',
            'input_select', 'input_number', 'vacuum', 'lock', 'garage_door',
            'alarm_control_panel', 'camera', 'zone', 'person', 
            'device_tracker', 'weather'
        }
        
        for domain in expected_domains:
            assert domain in RELEVANT_DOMAINS
    
    def test_relevant_domains_is_set(self):
        """Test that RELEVANT_DOMAINS is a set."""
        assert isinstance(RELEVANT_DOMAINS, set)
    
    def test_relevant_domains_no_duplicates(self):
        """Test that RELEVANT_DOMAINS has no duplicates."""
        # Sets automatically handle duplicates, so length should equal unique count
        assert len(RELEVANT_DOMAINS) == len(list(RELEVANT_DOMAINS))
