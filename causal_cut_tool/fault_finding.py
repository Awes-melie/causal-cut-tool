from importlib.metadata import entry_points
from uuid import uuid4

# Get run method from user plugin
run_eps = entry_points(group='causal_cut_tool.run')
run = run_eps['run'].load()

find_faults_eps = entry_points(group='causal_cut_tool.find_faults')
find_faults = find_faults_eps['find_faults'].load()

# pylint: disable=R0913,R0914
def reproduce_fault(
    attack: dict,
    timesteps: int,
    interventions: list,
    constants: list,
    save_path: str = None,
) -> (bool, int):
    """
    Attempt to reproduce a fault from the dataset by executing the given
    interventions for the given number of timesteps.

    :param timesteps: The number of timesteps to run the simulator for.
    :param initial_carbs: The initial carbohydrates in the stomach.
    :param initial_bg: The initial blood glucose.
    :param initial_iob: The initial amount of insulin in the blood.
    :param interventions: The interventions - a list of triples of the form (time, variable, value).
    :param constants: The subject's medical constants. See documentation of `scenario.run` for further details.
    :param save_path: Filepath to save the run details as a JSON file (optional).

    :return: Whether a fault occurred.
    """

    sim_df = run(attack,
                 timesteps=timesteps,
                 interventions=interventions,
                 constants=constants,
                 tempdir=f"tmp/{uuid4().hex}",
                 kill_at_fault=True)

    if save_path is not None:
        sim_df.to_csv(save_path)

    if sim_df["Safe"].all():
        return (False, None)

    fault, fault_time = find_faults(sim_df)

    return fault, fault_time