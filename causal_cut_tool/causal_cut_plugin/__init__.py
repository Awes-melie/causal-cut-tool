from typing import Any

import matplotlib.pyplot as plt
import pandas as pd
from aps_digitaltwin.model import Model
from aps_digitaltwin.openaps import OpenAPS
from aps_digitaltwin.util import s_label, j_label, l_label, g_label, i_label, BOLUS, BASAL_BOLUS_THRESHOLD
from aps_digitaltwin.util import LOW, HIGH, BASAL_BOLUS_THRESHOLD, BOLUS, SNACK, LIGHT_MEAL, HEAVY_MEAL, constant_names

def _plot(df, timesteps):
    fig, (ax1, ax2) = plt.subplots(1, 2)
    ax1.set_title("No Intervention")
    ax1.hlines(y=[HIGH, LOW], xmin=0, xmax=timesteps, colors="r", linestyles="--", lw=1)
    ax2.set_title("OpenAPS Intervention")
    ax2.hlines(y=[HIGH, LOW], xmin=0, xmax=timesteps, colors="r", linestyles="--", lw=1)

    df.plot("step", [s_label, j_label, l_label, g_label, i_label], ax=ax2)
    plt.show()

def run_control(
    interventions, list,
    constants: list,
    timesteps: int,
    timesteps_per_intervention: int,
    plot=False,
    kill_at_fault=False,
    initial_values=None,
):
    model_control = Model(initial_values, constants)

    for intervention in interventions:
        model_control.add_intervention(intervention[0], intervention[1], intervention[2])

    control_violations = []
    fault = False
    for t in range(1, timesteps + 1):
        timestep = model_control.update(t)
        if not (LOW < timestep[g_label] < HIGH):
            fault = True
            control_violations.append(timestep["step"])
            if kill_at_fault and fault and t % timesteps_per_intervention == 0:
                break

    control_df = pd.DataFrame(model_control.history)

    if plot:
        _plot(control_df, timesteps)
    return control_df

def run(
    attack: dict,
    timesteps: int,
    interventions: list,
    constants: list,
    plot=False,
    model_control=False,
    tempdir="openaps_temp",
    kill_at_fault=False,
    timesteps_per_intervention=5,
):

    initial_values: list[float] = [attack["initial_carbs"], 0, 0, attack["initial_bg"], attack["initial_iob"]]

    if model_control:
        control_df = run_control(constants,
                                 plot=plot,
                                 kill_at_fault=kill_at_fault,
                                 timesteps=timesteps,
                                 timesteps_per_intervention=timesteps_per_intervention,
                                 initial_values=initial_values)

    open_aps = OpenAPS(None, profile_path=None, basal_profile_path=None)
    model_openaps = Model(initial_values, constants, interventions=interventions)

    fault = False
    for t in range(1, timesteps + 1):
        if t % timesteps_per_intervention == 0:
            rate = open_aps.run(model_openaps.history, tempdir)
            if rate > BASAL_BOLUS_THRESHOLD:
                model_openaps.add_intervention(t, "bolus", BOLUS)
            else:
                for j in range(5):
                    model_openaps.add_intervention(t + j, i_label, rate / 5.0)
        timestep = model_openaps.update(t)
        fault = fault or (not (LOW < timestep[g_label] < HIGH))
        if kill_at_fault and fault and t % timesteps_per_intervention == 0:
            break
    openaps_df = pd.DataFrame(model_openaps.history)
    openaps_df["Safe"] = openaps_df["Blood Glucose"].between(LOW, HIGH)

    hyper_violations = []
    hypo_violations = []
    bg_change = 0
    for idx, timestep in enumerate(model_openaps.history):
        if not idx == 0:
            bg_change += abs(timestep[g_label] - model_openaps.history[idx - 1][g_label])
        if timestep[g_label] > HIGH:
            hyper_violations.append(timestep["step"])

        if timestep[g_label] < LOW:
            hypo_violations.append(timestep["step"])

    if plot:
        _plot(openaps_df, timesteps)

    for k, v in zip(constant_names, constants):
        openaps_df[k] = v

    return openaps_df

def find_faults(sim_df):
    """
    Given simulation results, find all failing runs
    :param sim_df:
    :return: fault, fault_time
    """
    unsafe = sim_df.loc[~sim_df["Safe"], "step"]
    fault_time = int(unsafe.min())
    glucose_value = sim_df.loc[fault_time, "Blood Glucose"]
    fault = "Low" if glucose_value < LOW else "High" if glucose_value > HIGH else None
    assert fault is not None
    return fault, fault_time