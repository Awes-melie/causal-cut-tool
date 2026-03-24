# How to Use the Causal Cut Tool
The causal-cut tool can be used to generate a reduced set of test cases by using causal inference
to estimate the contribution of each intervention from pre-existing runtime data.
## Running the system
The causal cut tool can be run using `uv` from the `causal_cut_tool` directory with the command:
`uv run bash ./causal_cut.sh [PATH TO DATAFILE].pqt`
There are several important arguments to run the command:
- __Attacks file__
`-a datafiles/successful_attacks.json`
- __Dagfile__
`-d datafiles/dcg.dot`
- __Safe ranges file__
`-s datafiles/safe_ranges.json`
- __Total time(steps)__
`-T 500`
- Timesteps per Intervention
`-t 5`
- Confidence alpha
`-c 0.2`
- Attack index
`-i 10`
(This should be the index of the attack to model from the attacks file)
- Output file
`-o datafiles/logs/ci_80/attack-[ATTACK NUMBER].json`

- Background confounders
`-b kjs kgj kjl kgl kxg kxgi kxi τ η kλ kμ Gprod0`
- Number of individuals in the study
`-n 5000`
- Silence exceptions and store
`-S`

__Bolded__ arguments are required

A minimal command would be something like: `uv run bash ./causal_cut.sh -a datafiles/successful_attacks.json -d datafiles/dcg.dot -s datafiles/safe_ranges.json -o datafiles/logs//ci_80/attack-1.json -T 500 datafiles/data/1.pqt`
## System Data
The system needs several pieces of data to run:
- `safe_ranges.json` lists the low and high values for each sensor of the form
```
{
  "Sensor1": {"lo": 50, "hi": 180},
  "Sensor2": {"lo": 50, "hi": 180}.
  ...
}
```

- `data.pqt` is a parquet file containing the runtime data in a table format where columns represent variables and rows represent the values of those variables at a _particular point in time_. This should be in "long format" where each run has an id and runs are just concatenated together, for example:

|run_id|time |x1  |x2 |x3 |outcome|Safe|
|------|-----|----|---|---|-------|----|
|0     |0    |... |...|...|...    |True|
|0     |1    |... |...|...|...    |True|
|0     |2    |... |...|...|...    |True|
|0     |3    |... |...|...|...    |False|
|__1__ |__0__|__...__ |__...__|__...__|__...__|__True__|
|__1__ |__1__|__...__ |__...__|__...__|__...__|__True__|
|__1__ |__2__|__...__ |__...__|__...__|__...__|__True__|
|__1__ |__3__|__...__ |__...__|__...__|__...__|__True__|
|__1__ |__4__|__...__ |__...__|__...__|__...__|__False__|
|  2   |  0  |... |...|...|...    |True|
|  2   |  1  |... |...|...|...    |True|
|  2   |  2  |... |...|...|...    |True|
|  2   |  3  |... |...|...|...    |True|
|  2   |  4  |... |...|...|...    |True|
|  2   |  5  |... |...|...|...    |True|

- `successful_attacks.json` is a json file specifying the "attacks" (tests) to minimise. This should take the form of
```
[
  {
    "attack_id": 0,             # ID of the attack
    "attack": [                 # list of interventions of the form [time, variable, value]
      [225, "bolus", 1],
      [275, "bolus", 1],
      [290, "bolus", 1]
    ],
    "timesteps": 499,           # Total number of timesteps to consider
    "fault_time": 298,          # When the fault happened
    "outcome": "Blood_Glucose", # Outcome variable
    "failure": "Low",           # Failure value
    ... # Other configuration arguments
  },
  ... # other attacks
]
```
- `dcg.dot` is a DOT file specifying the (possibly cyclic) expected causal relationships between the variables, e.g.
```
digraph G {
  x1 -> x2;
  x2 -> x3;
  x3 -> x1;
}
```

Note, file names are intended to be examples and are not hardcoded.
## Simulation interface
The `causal_cut_plugin` project acts as an interface between the causal cut tool and the system under test. It must contain the two methods `run()` and `find_faults()`.

```python
import matplotlib.pyplot as plt
import pandas as pd

HIGH = 1
LOW = 0

def _plot(df, timesteps):
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.set_title("No Intervention")
    ax1.hlines(y=[HIGH, LOW], xmin=0, xmax=timesteps, colors="r", linestyles="--", lw=1)
    ax2.set_title("With Intervention")
    ax2.hlines(y=[HIGH, LOW], xmin=0, xmax=timesteps, colors="r", linestyles="--", lw=1)

    df.plot("step", ax=ax2)
    plt.show()

def run(
    attack: dict,
    timesteps: int,
    interventions: list,
    constants: list,
    plot=False,
    model_control=False,
    tempdir="temp",
    kill_at_fault=False,
    timesteps_per_intervention=5,
):
    """

    :param: attack: Attack dictionary containing all data calculated during g-estimation and during data generation
    :param: timesteps: Number of timesteps to simulate
    :param: interventions: List containing all possible interventions
    :param: constants: List of all simulation constants
    :param: plot: Whether to plot the data
    :param: model_control: Whether to generate a control simulation
    :param: tempdir: Path to temporary directory
    :param: kill_at_fault: Should system terminate if a fault is caused
    :param: timesteps_per_intervention: How many timesteps to simulate between interventions
    :return: Dataframe containing simulation history
    """
    # Setup systems under test
    fault = False
    for t in range(1, timesteps + 1):
        if t % timesteps_per_intervention == 0:
            break
            # Add intervention(s)

        # Update modelled system
        fault = fault or True # See if fault has developed

        # Break at fault if needed
        if kill_at_fault and fault and t % timesteps_per_intervention == 0:
            break

    # Export model history from system
    df = pd.DataFrame()
    df["Safe"] = []
    if plot:
        _plot(df, timesteps)

    return df

def find_faults(sim_df):
    """
    Given simulation results, find all failing runs
    :param sim_df:
    :return: fault, fault_time
    """
    # Filter failing runs
    unsafe = sim_df.loc[sim_df, "step"]
    fault_time = int(unsafe.min())

    # Find cause of fault, e.g.
    # val = sim_df[fault_time].val
    # fault = "Low" if val < LOW else "High" if val > HIGH else None
    #assert fault is not None

    return "FAULT", fault_time
```
`run` should model the system under test. It will go one timestep at a time, updating the system and selecting interventions to use. If it encounters a fault, this should be logged and optionally the system should stop. A history of the run should then be output.
`find_faults` should be able to take the dataframe output by `run` and output the cause and time of failure.
An additional `_plot` method can be defined if plots are wanted. This should run based on the value of the plot flag passed to `run`.
If `model_control` is set, then `run` should also run a control simulation.
## Output
The result of the simulation will be outputted to the file given by -o as a .json file. It will contain a list of interventions and any other data that has been output during the `run` method.