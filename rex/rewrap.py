#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: rewrap.py
# Author: Wadih Khairallah
# Description: 
# Created: 2024-12-03 11:29:31
# Modified: 2024-12-03 12:08:56
import re
from functools import lru_cache
from contextlib import contextmanager

class PatternConflictError(Exception):
    """Custom exception for pattern conflicts."""
    pass

class InvalidPatternError(Exception):
    """Custom exception for invalid patterns."""
    pass

class ReWrap:
    _custom_patterns = {}
    _custom_flags = {}

    # List of reserved regex sequences
    reserved_sequences = [
        r'\d', r'\w', r'\s', r'\b', r'\B', r'\D', r'\S', r'\W', r'\A', r'\Z', r'\t', r'\r', r'\n', r'\f', r'\v'
    ]

    def __init__(self):
        self.base_re = re
        self.buffers = {}     # For live buffer management
        self.variables = {}   # For variable assignments

    def add_buffer(self, buffer_name):
        """Assign a buffer with the given name."""
        self.buffers[buffer_name] = []

    @contextmanager
    def BUFFER(self, buffer_name):
        """Context manager to access the live buffer."""
        buffer = self.buffers.setdefault(buffer_name, [])
        try:
            yield buffer
        finally:
            pass  # Buffer can be modified within the context

    def add_pattern(self, placeholder, replacement, var_name=None, callback=None):
        """
        Register a custom regex pattern. Optionally assign the match result to a variable.
        If no variable name is provided, the match will be placed into the name derived from the placeholder.
        Optionally, a callback function can be provided to process the match inline.
        """
        # Check if placeholder conflicts with reserved sequences
        if placeholder in self.reserved_sequences:
            raise PatternConflictError(f"Placeholder '{placeholder}' conflicts with reserved regex sequences.")

        # Test the replacement pattern by compiling it
        try:
            self.base_re.compile(replacement)
        except re.error as e:
            raise InvalidPatternError(f"Invalid regex pattern '{replacement}': {e}")

        # Register the custom pattern
        self._custom_patterns[placeholder] = (replacement, var_name or placeholder, callback)

    @lru_cache(maxsize=500)
    def _process_pattern(self, pattern):
        """
        Replace custom patterns in the regex with their replacements.
        """
        for placeholder, (replacement, _, _) in self._custom_patterns.items():
            # Use named groups for easier access
            pattern = pattern.replace(f"[[:{placeholder}:]]", f"(?P<{placeholder}>{replacement})")
        return pattern

    def _compile(self, pattern, flags=0):
        """Compile a regex pattern with custom processing."""
        processed_pattern = self._process_pattern(pattern)
        return self.base_re.compile(processed_pattern, flags)

    def _handle_match(self, match):
        """
        Handle a single match object.
        Assign variables and call callbacks as needed.
        """
        group_dict = match.groupdict()
        for placeholder, (_, var_name, callback) in self._custom_patterns.items():
            if placeholder in group_dict:
                value = group_dict[placeholder]
                if var_name:
                    self.variables[var_name] = value
                if callback:
                    callback(value)

    def search(self, pattern, string, flags=0, pre=None, post=None):
        """
        Search with custom preprocessing and buffer access.
        """
        if pre:
            string = pre(string)

        regex = self._compile(pattern, flags)
        match = regex.search(string)

        if match:
            self._handle_match(match)
            if post:
                post(match)

        return match

    def match(self, pattern, string, flags=0, pre=None, post=None):
        """
        Match with custom preprocessing and buffer access.
        """
        if pre:
            string = pre(string)

        regex = self._compile(pattern, flags)
        match = regex.match(string)

        if match:
            self._handle_match(match)
            if post:
                post(match)

        return match

    def findall(self, pattern, string, flags=0):
        """
        Find all matches using custom pattern processing.
        """
        regex = self._compile(pattern, flags)
        matches = regex.finditer(string)
        results = []

        for match in matches:
            self._handle_match(match)
            results.append(match.group())

        return results

    def sub(self, pattern, repl, string, count=0, flags=0):
        """
        Substitute using custom preprocessing.
        """
        regex = self._compile(pattern, flags)
        return regex.sub(repl, string, count)

    def recursive_search(self, pattern, data, flags=0):
        """
        Recursively search for the pattern within nested data structures.
        """
        matches = []
        if isinstance(data, str):
            match = self.search(pattern, data, flags)
            if match:
                matches.append(match)
        elif isinstance(data, list):
            for item in data:
                matches.extend(self.recursive_search(pattern, item, flags))
        elif isinstance(data, dict):
            for key, value in data.items():
                matches.extend(self.recursive_search(pattern, value, flags))
        return matches

    def get_variable(self, var_name):
        """Get the value of a variable assigned from a match."""
        return self.variables.get(var_name)

    def get_buffer(self, buffer_name):
        """Return the specified buffer."""
        return self.buffers.get(buffer_name, [])

