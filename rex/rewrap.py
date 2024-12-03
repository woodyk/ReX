#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: rewrap.py
# Author: Wadih Khairallah
# Description: 
# Created: 2024-12-03 11:29:31
# Modified: 2024-12-03 17:04:59

import re
from functools import lru_cache
from contextlib import contextmanager
import itertools

class PatternConflictError(Exception):
    """Custom exception for pattern conflicts."""
    pass

class InvalidPatternError(Exception):
    """Custom exception for invalid patterns."""
    pass

class ReWrap:
    # Reserved regex sequences
    reserved_sequences = [
        r'\d', r'\w', r'\s', r'\b', r'\B', r'\D', r'\S', r'\W', r'\A', r'\Z', r'\t', r'\r', r'\n', r'\f', r'\v'
    ]

    # Map re module constants and exceptions to ReWrap
    error = re.error
    I = IGNORECASE = re.IGNORECASE
    M = MULTILINE = re.MULTILINE
    S = DOTALL = re.DOTALL
    U = UNICODE = getattr(re, 'UNICODE', 0)  # UNICODE flag is deprecated in Python 3
    L = LOCALE = re.LOCALE
    X = VERBOSE = re.VERBOSE
    A = ASCII = re.ASCII
    TEMPLATE = re.TEMPLATE
    DEBUG = re.DEBUG

    def __init__(self):
        self.base_re = re
        self._custom_patterns = {}
        self._custom_flags = {}
        self._buffer = None  # Current buffer to collect matches
        self.buffers = {}  # Live buffer management

    def add_buffer(self, buffer_name):
        """Assign a buffer with the given name."""
        self.buffers[buffer_name] = []

    @contextmanager
    def BUFFER(self, buffer_name):
        """Context manager to access the live buffer."""
        buffer = self.buffers.setdefault(buffer_name, [])
        previous_buffer = self._buffer
        self._buffer = buffer  # Set current buffer
        try:
            yield buffer
        finally:
            self._buffer = previous_buffer  # Restore previous buffer

    def add_pattern(self, placeholder, replacement, callback=None):
        """
        Register a custom regex pattern or multiple patterns under a single placeholder.
        If replacement is a list, each pattern is registered.
        Optionally apply a callback function to process the match.
        """
        # Ensure placeholder is a valid identifier
        if not placeholder.isidentifier():
            raise PatternConflictError(f"Invalid placeholder name '{placeholder}'. Must be a valid identifier.")

        # Check if replacement is empty
        if isinstance(replacement, list) and not replacement:
            raise InvalidPatternError(f"No patterns provided for placeholder '{placeholder}'.")

        # If replacement is a list, register each pattern
        if isinstance(replacement, list):
            for pattern in replacement:
                self._validate_pattern(pattern)
                self._custom_patterns.setdefault(placeholder, []).append((pattern, callback))
        else:
            self._validate_pattern(replacement)
            self._custom_patterns.setdefault(placeholder, []).append((replacement, callback))

    def _validate_pattern(self, pattern):
        """Validate that a regex pattern can be compiled."""
        try:
            self.base_re.compile(pattern)
        except re.error as e:
            raise InvalidPatternError(f"Invalid regex pattern '{pattern}': {e}")

    def _process_pattern(self, pattern):
        """Replace custom patterns in the regex with their replacements."""
        # Counter to ensure unique group names
        placeholder_counts = {}

        # Function to replace placeholders with unique group names
        def replace_placeholder(match):
            placeholder = match.group(1)
            if placeholder in self._custom_patterns:
                patterns = self._custom_patterns[placeholder]
                if patterns:
                    combined_pattern = "|".join([p[0] for p in patterns])
                else:
                    combined_pattern = r'(?!.)'
                # Generate a unique group name
                count = placeholder_counts.get(placeholder, 0) + 1
                placeholder_counts[placeholder] = count
                group_name = f"{placeholder}_{count}"
                return f"(?P<{group_name}>{combined_pattern})"
            else:
                raise re.error(f"Undefined placeholder '[[:{placeholder}:]]' in pattern.")

        pattern = re.sub(r'\[\[:(.*?)\:\]\]', replace_placeholder, pattern)
        return pattern

    def _handle_match(self, match, callback):
        """
        Handle a single match object.
        Call the callback if defined, and allow for real-time buffering.
        """
        group_dict = match.groupdict()
        for group_name, value in group_dict.items():
            # Extract the placeholder name from the group name
            placeholder = group_name.rsplit('_', 1)[0]
            # Apply callback if defined
            patterns = self._custom_patterns.get(placeholder, [])
            for pattern, cb in patterns:
                if cb:
                    value = cb(value)
                    break  # Assuming one callback per placeholder

            # Add to current buffer if set
            if self._buffer is not None:
                self._buffer.append((placeholder, value))

        if callback:
            callback(match)

    def _compile(self, pattern, flags=0):
        """Compile a regex pattern with custom processing."""
        processed_pattern = self._process_pattern(pattern)
        return self.base_re.compile(processed_pattern, flags)

    def search(self, pattern, string, flags=0, pre=None, post=None):
        """Search with preprocessing, postprocessing."""
        if pre:
            string = pre(string)

        regex = self._compile(pattern, flags)
        match = regex.search(string)

        if match:
            self._handle_match(match, post)
        return match

    def match(self, pattern, string, flags=0, pre=None, post=None):
        """Match with preprocessing, postprocessing."""
        if pre:
            string = pre(string)

        regex = self._compile(pattern, flags)
        match = regex.match(string)

        if match:
            self._handle_match(match, post)
        return match

    def findall(self, pattern, string, flags=0):
        """Find all matches using custom patterns."""
        regex = self._compile(pattern, flags)
        matches = regex.finditer(string)
        results = []

        for match in matches:
            self._handle_match(match, None)
            results.append(match.group())

        return results

    def finditer(self, pattern, string, flags=0):
        """Find all matches using custom patterns, returning match objects."""
        regex = self._compile(pattern, flags)
        matches = regex.finditer(string)
        matches, matches_copy = itertools.tee(matches)  # Create a copy of the iterator

        for match in matches:
            self._handle_match(match, None)
        return matches_copy

    def sub(self, pattern, repl, string, count=0, flags=0):
        """Substitute matches with a replacement string."""
        regex = self._compile(pattern, flags)
        return regex.sub(repl, string, count)

    def sub_with_callback(self, pattern, string, callback, count=0, flags=0):
        """Substitute matches and apply the callback to each match."""
        regex = self._compile(pattern, flags)
        result = regex.sub(lambda match: callback(match.group()), string, count)
        return result

    def buffer_stream(self):
        """Real-time stream of all matches in the buffer."""
        if self._buffer is not None:
            for placeholder, match in self._buffer:
                yield placeholder, match

    def get_buffer(self, buffer_name):
        """Return the specified buffer."""
        return self.buffers.get(buffer_name, [])

    def compile(self, pattern, flags=0):
        """Proxy to re.compile() but with custom pattern processing."""
        return self._compile(pattern, flags)

    def recursive_search(self, pattern, data, flags=0, pre=None, post=None):
        """
        Recursively search for the pattern within nested data structures.
        """
        matches = []

        if isinstance(data, str):
            match = self.search(pattern, data, flags, pre, post)
            if match:
                matches.append(match)
        elif isinstance(data, list):
            for item in data:
                matches.extend(self.recursive_search(pattern, item, flags, pre, post))
        elif isinstance(data, dict):
            for key, value in data.items():
                matches.extend(self.recursive_search(pattern, value, flags, pre, post))

        return matches


