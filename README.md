# Factoreally

Generate realistic test data from real data patterns.

Factoreally involves two steps:

1. **Analyze sample data** → create a factory spec based on input data
2. **Use the factory spec** → generate realistic data based on the factory spec

It automatically detects patterns (UUIDs, timestamps, email formats, numeric distributions) and generates statistically accurate test data that matches your real data.

## Features

- **Pattern detection**: UUIDs, timestamps, emails, phone numbers, custom formats
- **Statistical accuracy**: Maintains distributions and value frequencies
- **Dynamic objects**: Detects and generates varying dictionary keys
- **Null handling**: Preserves optional field probabilities
- **Batch generation**: Efficiently generate thousands of records

## Quick Start

### 1. Analyze sample data to create a factory spec

```bash
# Basic spec generation
factoreally create --in real_user_payloads.json --out user.spec.json

# With Pydantic model to identify dynamic dictionary fields
factoreally create \
  --in user_payloads.json \
  --out user.spec.json \
  --model myapp.models.UserModel
```

### 2. Use the factory spec to generate data

```python
from factoreally import Factory

# Create factory from spec
user_factory = Factory("user.spec.json")

# Generate single object
user_data = user_factory.build()

# Generate batch
users = user_factory[:1000]

# Integrate with Pydantic models
user = UserModel.model_validate(user_factory.build())
```

## Customization

```python
# Create factory with built-in overrides
admin_factory = Factory(spec, role="admin", permissions__level="high")

# Per-generation overrides
user = user_factory.build(email="specific@example.com")

# Nested field overrides
user = user_factory.build(address__country="US", profile__verified=True)

# Array element overrides
user = user_factory.build(items__name="default", items__value=None)  # override all array elements
user = user_factory.build(items__0__name="first", items__0_value=1) # override specific array index

# Dynamic overrides with callables
user = user_factory.build(
    id=lambda: str(uuid.uuid4()),  # Generate new value
    name=lambda value: value.upper(),  # Transform generated value
    display_name=lambda value, obj: f"{value} ({obj['role']})"  # Use context of entire generated object
)
```

## Pydantic Integration

Provide a Pydantic model to help identify dynamic dictionary fields:

```python
class UserEvent(BaseModel):
    user_id: str
    metadata: dict[str, str]  # Factoreally treats this as dynamic dict
```

```shell
factoreally create --in events.json --out events.spec.json --model myapp.models.UserEvent
```
