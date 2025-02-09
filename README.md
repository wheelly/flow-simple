# Flow Simple
#### Simplified Python Test Framework for API flows

### Example of the flow definition
```yaml
base_url: https://localhost/api/v1

flow:
  - system/set-secret-provider:
      method: PUT
      parameters:
        - local-vault
      body:
        type: vault
        parameters:
          vaultAddress: http://vault.default:8200
          roleName: database
          objects:
            - objectName: credentials
              secretPath: secret/data/db-credentials
              secretKey: credentials
      response:
        body:
          action_id: ${action_id}
      awaits:
        ref: deploy-status
  - secrets:
      method: PUT
      body:
        target-db:
          TARGET_DB_USERNAME: default
          TARGET_DB_PASSWORD: test
      retries:
        max: 3
        delay:
          min: 1
          max: 20
        until:
          response:
            status: 200

refs:
  deploy-status:
    actions:
      method: GET
      parameters:
        - ${action_id}
      response:
        body:
          action_id: ${action_id}
          status:
            "&in":
              - pending
              - processing
      retries:
        max: 6
        delay:
          min: 3
          max: 20
        until:
          response:
            body:
              action_id: ${action_id}
              status: completed
```
### Installation
```shell
  git clone https://github.com/wheelly/flow-simple
  cd flow-simple
  pip install -r requirements.txt
```

### Example of usage
```python
from flow_simple import FlowRunner

def test_example():
    """Runs the example."""
    def contains(expected: str, actual: str):
        """Checks if the expected string is in the actual string."""
        assert actual.find(expected) != -1, f"Expected {expected} in {actual}"

    FlowRunner(read_yaml("./httpbins.yaml"), [contains]).run()
```

### Example of execution
```shell
  PYTHONPATH="./src" pytest ./examples/test_example.py
```

### Testing

```shell
  PYTHONPATH="./src" pytest ./tests
```
