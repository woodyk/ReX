#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: test_rewrap.py
# Author: Wadih Khairallah
# Description: 
# Created: 2024-12-03 11:40:02
# Modified: 2024-12-03 12:08:29

import pytest
from rex import ReWrap, PatternConflictError, InvalidPatternError

# Test Adding and Removing Patterns
def test_add_remove_pattern():
    rw = ReWrap()
    rw.add_pattern('email', r'[\w\.-]+@[\w\.-]+\.\w+', 'email_var')
    rw.add_pattern('phone', r'\d{3}-\d{3}-\d{4}', 'phone_var')
    assert 'email' in rw._custom_patterns
    assert 'phone' in rw._custom_patterns

    # Simulate removal of a pattern
    del rw._custom_patterns['email']
    assert 'email' not in rw._custom_patterns

# Test Buffer Context Management
def test_buffer_context():
    rw = ReWrap()
    buffer_name = "test_buffer"
    rw.add_buffer(buffer_name)

    with rw.BUFFER(buffer_name) as buffer:
        buffer.append("test data")
    assert "test data" in rw.get_buffer(buffer_name)

# Test Buffer Cleanup
def test_buffer_cleanup():
    rw = ReWrap()
    buffer_name = "test_buffer"
    rw.add_buffer(buffer_name)

    with rw.BUFFER(buffer_name) as buffer:
        buffer.append("test data")

    # Ensure manual cleanup works
    del rw.buffers[buffer_name]
    assert buffer_name not in rw.buffers

# Test Buffer Stress Test
def test_buffer_stress():
    rw = ReWrap()
    buffer_name = "stress_buffer"
    rw.add_buffer(buffer_name)

    large_data = ["data" * 1000] * 1000
    with rw.BUFFER(buffer_name) as buffer:
        buffer.extend(large_data)
    assert len(rw.get_buffer(buffer_name)) == 1000

# Test Adding Conflicting Patterns
def test_pattern_conflict():
    rw = ReWrap()
    with pytest.raises(PatternConflictError):
        rw.add_pattern(r'\d', r'\d+', 'digit_var')

# Test Adding Invalid Patterns
def test_invalid_pattern():
    rw = ReWrap()
    with pytest.raises(InvalidPatternError):
        rw.add_pattern('invalid', r'[unclosed_group', 'invalid_var')

# Test Search Method
def test_search():
    rw = ReWrap()
    rw.add_pattern('email', r'[\w\.-]+@[\w\.-]+\.\w+', 'email_var')
    text = "Contact us at support@example.com"
    match = rw.search(r'[[:email:]]', text)
    assert match is not None
    assert rw.get_variable('email_var') == 'support@example.com'

# Test Match Method
def test_match():
    rw = ReWrap()
    rw.add_pattern('digit', r'\d+', 'digit_var')
    text = "12345 is a number"
    match = rw.match(r'[[:digit:]]', text)
    assert match is not None
    assert rw.get_variable('digit_var') == "12345"

# Test Findall Method
def test_findall():
    rw = ReWrap()
    rw.add_pattern('digit', r'\d+', 'digit_var')
    text = "Numbers: 123, 456, 789."
    matches = rw.findall(r'[[:digit:]]', text)
    assert matches == ['123', '456', '789']

# Test Substitution
def test_sub():
    rw = ReWrap()
    rw.add_pattern('digit', r'\d+', 'digit_var')
    text = "Replace 12345 with something"
    result = rw.sub(r'[[:digit:]]', '###', text)
    assert result == "Replace ### with something"

# Test Recursive Search
def test_recursive_search():
    rw = ReWrap()
    rw.add_pattern('email', r'[\w\.-]+@[\w\.-]+\.\w+', 'email_var')
    data = {"users": [{"email": "test1@example.com"}, {"email": "test2@example.com"}]}
    matches = rw.recursive_search(r'[[:email:]]', data)
    assert len(matches) == 2
    assert rw.get_variable('email_var') == "test2@example.com"

# Test Recursive Edge Cases
def test_recursive_edge_cases():
    rw = ReWrap()
    rw.add_pattern('email', r'[\w\.-]+@[\w\.-]+\.\w+', 'email_var')
    nested_data = {"level1": [{"level2": {"email": "deep@example.com"}}]}
    matches = rw.recursive_search(r'[[:email:]]', nested_data)
    assert len(matches) == 1
    assert rw.get_variable('email_var') == "deep@example.com"

# Test Callback Handling
def test_callback_handling():
    rw = ReWrap()

    def email_callback(match):
        assert match == "support@example.com"

    rw.add_pattern('email', r'[\w\.-]+@[\w\.-]+\.\w+', 'email_var', callback=email_callback)
    text = "Contact us at support@example.com"
    rw.search(r'[[:email:]]', text)

if __name__ == "__main__":
    pytest.main(["-v"])

