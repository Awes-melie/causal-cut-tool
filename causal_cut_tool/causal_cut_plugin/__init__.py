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