
def resolve_variables(params: dict, data: dict):
    """
        Resolves the variables like ${xxx} from parameters, query or body.
        The variables values expected to be inside response
    """

    def resolve_single_variable(value: str, data: dict):
        """Resolves the variable."""
        if value.startswith("${") and value.endswith("}"):
            variable_name = value[2:-1]
            if variable_name not in data:
                raise ValueError(f"Variable '{variable_name}' not found in response body")
            return data[variable_name]

    def resolve_list_variable(value: list, data: dict):
        """Resolves the list variable."""
        assert isinstance(data, dict), "Expected dict in response data"
        for i, item in enumerate(value):
            if isinstance(item, dict):
                resolve_variables(item, data)
            elif isinstance(item, list):
                resolve_list_variable(item, data)
            else:
                value[i] = resolve_single_variable(item, data)

    # Resolve the variables - requires data[prop] in response data
    # section in request parameters, query or body
    for section in ("parameters", "query", "body"):
        entity = params.get(section, {})
        # mandatory: must be prop in data - on the first level - no nested dicts
        if isinstance(entity, dict):
            for prop, value in entity.items():
                if prop not in data:
                    raise ValueError(f"Key '{prop}' not found in response body")
                if isinstance(value, dict):
                    # recursive call for nested dict
                    resolve_variables(value, data)
                elif isinstance(value, list):
                    resolve_list_variable(value, data)
                else:
                    params[section][prop] = resolve_single_variable(value, data)
        elif isinstance(entity, list):
            resolve_list_variable(entity, data)
        else:
            raise ValueError(f"Expected dict or list in '{section}'")
