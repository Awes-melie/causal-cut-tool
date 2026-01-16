from importlib.metadata import entry_points

# Load user data
runtime_eps = entry_points(group='causal_cut_tool.runtime_data')
parameters_eps = entry_points(group='causal_cut_tool.parameters')
try:
    runtime = runtime_eps['runtime_data'].load()
except Exception:
    print(Exception.with_traceback())
    def runtime():
        return "FAILED TO LOAD"
    print("No Runtime Data provided")
    exit(2) # Improper command Usage

try:
    parameters = parameters_eps['parameters'].load()
except Exception:
    def parameters():
        return "FAILED TO LOAD"
    print("No Estimation Parameters provided")
    exit(2) # Improper command Usage
