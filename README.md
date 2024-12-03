# ReX

ReX is a powerful and flexible regex wrapper tool designed to simplify and 
extend regular expression capabilities in Python. It offers seamless 
registration of custom patterns, real-time buffer management, recursive 
searching within nested data structures, and integration with callbacks and 
data validation.

## Features

- **Custom Pattern Registration**: Easily add reusable regex patterns with 
  optional callbacks for validation or transformation.
- **Real-Time Buffer Management**: Use buffers to dynamically store and 
  manage regex matches in real time.
- **Recursive Search**: Perform regex searches across deeply nested Python 
  structures like dictionaries and lists.
- **Data Validation and Cleaning**: Automatically validate and clean matches 
  using user-defined callbacks.
- **Conflict Detection**: Prevent conflicts with reserved regex sequences or 
  invalid patterns.
- **Minimalistic and Intuitive API**: Simple method names like `add_pattern`, 
  `search`, `match`, `findall`, and `sub` ensure ease of use.

## Installation

To install ReX, use pip:

```bash
pip install rex
```

## Quick Start

### Import and Initialize
```python
from rex import ReWrap

rw = ReWrap()
```

### Register Custom Patterns
```python
rw.add_pattern('email', r'[\w\.-]+@[\w\.-]+\.\w+', 'email_var')
rw.add_pattern('phone', r'\d{3}-\d{3}-\d{4}', 'phone_var')
```

### Perform a Search
```python
text = "Contact us at support@example.com or call 123-456-7890."

# Search for patterns
rw.search(r'[[:email:]]', text)
rw.search(r'[[:phone:]]', text)

# Access variables assigned from matches
print(rw.get_variable('email_var'))  # Outputs: support@example.com
print(rw.get_variable('phone_var'))  # Outputs: 123-456-7890
```

### Recursive Search in Nested Structures
```python
data = {"users": [{"email": "user1@example.com"}, {"email": "user2@example.com"}]}

matches = rw.recursive_search(r'[[:email:]]', data)
print(rw.get_variable('email_var'))  # Outputs: user2@example.com
```

### Real-Time Buffer Management
```python
rw.add_buffer("my_buffer")

with rw.BUFFER("my_buffer") as buffer:
    buffer.append("Example data")
    
print(rw.get_buffer("my_buffer"))  # Outputs: ["Example data"]
```

## Advanced Features

### Callbacks for Validation or Transformation
You can attach custom callbacks to patterns for in-place validation or data 
transformation:

```python
def validate_email(email):
    if "@" not in email:
        return None
    return email.lower()

rw.add_pattern('email', r'[\w\.-]+@[\w\.-]+\.\w+', 'email_var', 
               callback=validate_email)
```

### Substitution
Perform substitutions using custom patterns:

```python
text = "Replace 12345 with something."
rw.add_pattern('digit', r'\d+', 'digit_var')
result = rw.sub(r'[[:digit:]]', '###', text)
print(result)  # Outputs: Replace ### with something.
```

## Testing

The project includes a comprehensive test suite to ensure functionality. 
To run the tests, use `pytest`:

```bash
pytest test_rex.py
```

## License

ReX is licensed under the MIT License. See the LICENSE file for details.
