# FlowCore Message Protocol

The `FlowCoreMessage` is the lingua franca of the FlowCore execution engine. All plugins must exchange data using this protocol, which is strongly typed using Pydantic.

## Message Types

```python
class MessageType(str, Enum):
    RECORD = "RECORD"
    STATE = "STATE"
    SCHEMA = "SCHEMA"
    LOG = "LOG"
```

## Structure

Every `FlowCoreMessage` consists of a `type` and an optional payload corresponding to that type:

### Record Message
Contains the actual extracted data from a stream.
```json
{
  "type": "RECORD",
  "record": {
    "stream": "users",
    "data": { "id": 1, "name": "Alice" },
    "time_extracted": "2026-07-31T12:00:00Z"
  }
}
```

### State Message
Contains opaque state payload emitted by a connector to persist incremental sync boundaries.
```json
{
  "type": "STATE",
  "state": {
    "stream": "users",
    "state_data": { "last_updated_at": "2026-07-31T12:00:00Z" }
  }
}
```

### Schema Message
Describes the JSON schema for a particular stream, usually emitted during discovery or dynamically.
```json
{
  "type": "SCHEMA",
  "schema_info": {
    "stream": "users",
    "schema_data": { "type": "object", "properties": { ... } }
  }
}
```
