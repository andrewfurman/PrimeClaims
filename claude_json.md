import anthropic

client = anthropic.Anthropic(
    # defaults to os.environ.get("ANTHROPIC_API_KEY")
    api_key="my_api_key",
)
message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "Hello, Claude"}
    ]
)
print(message.content)

# Getting Structured JSON Responses from Claude Using Tools

## Overview
You can get structured JSON responses from Claude by defining a tool with a specific JSON schema and having Claude "use" the tool. This approach ensures consistent, well-formatted JSON output.

## Basic Implementation

```python
import anthropic
from anthropic import Anthropic

client = Anthropic()

# 1. Define your tool with desired JSON schema
tools = [
    {
        "name": "format_response",
        "description": "Formats the response as JSON",
        "input_schema": {
            "type": "object",
            "properties": {
                "field1": {"type": "string", "description": "Description of field1"},
                "field2": {"type": "number", "description": "Description of field2"},
                # Add more fields as needed
            },
            "required": ["field1", "field2"]
        }
    }
]

# 2. Create the query and force tool use
query = """
<text>
Your input text here
</text>

Use the format_response tool.
"""

# 3. Make the API call
response = client.messages.create(
    model="claude-3-sonnet-20240229",
    max_tokens=4096,
    tools=tools,
    tool_choice={"type": "tool", "name": "format_response"},  # Force specific tool use
    messages=[{"role": "user", "content": query}]
)

# 4. Extract the JSON response
json_response = None
for content in response.content:
    if content.type == "tool_use" and content.name == "format_response":
        json_response = content.input
        break
```

## Practical Example: Sentiment Analysis

```python
# Define sentiment analysis tool
sentiment_tools = [
    {
        "name": "analyze_sentiment",
        "description": "Analyzes sentiment scores",
        "input_schema": {
            "type": "object",
            "properties": {
                "positive_score": {"type": "number", "description": "Positive sentiment (0-1)"},
                "negative_score": {"type": "number", "description": "Negative sentiment (0-1)"},
                "neutral_score": {"type": "number", "description": "Neutral sentiment (0-1)"}
            },
            "required": ["positive_score", "negative_score", "neutral_score"]
        }
    }
]

def get_sentiment(text):
    response = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4096,
        tools=sentiment_tools,
        tool_choice={"type": "tool", "name": "analyze_sentiment"},
        messages=[{
            "role": "user", 
            "content": f"Analyze the sentiment: {text}"
        }]
    )

    for content in response.content:
        if content.type == "tool_use" and content.name == "analyze_sentiment":
            return content.input

    return None

# Usage
text = "I love this product! It's amazing!"
sentiment = get_sentiment(text)
```

## Tips for Success

1. **Schema Definition**
   - Be specific in property descriptions
   - Use appropriate data types
   - Mark required fields
   - Consider nesting for complex structures

2. **Force Tool Use**
   - Use `tool_choice` parameter to ensure tool usage
   - Include tool use instruction in prompt as backup

3. **Error Handling**
   - Check for None responses
   - Validate JSON structure
   - Handle missing fields

4. **Complex Structures**
Example of nested schema:

```python
tools = [{
    "name": "complex_response",
    "description": "Returns nested JSON structure",
    "input_schema": {
        "type": "object",
        "properties": {
            "main_category": {"type": "string"},
            "subcategories": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "score": {"type": "number"}
                    }
                }
            }
        }
    }
}]
```

## Common Use Cases

1. Entity Extraction
2. Text Classification
3. Data Transformation
4. Structured Analysis
5. Multi-language Translation