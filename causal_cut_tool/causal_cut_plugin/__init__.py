import matplotlib.pyplot as plt
import pandas as pd
from dataclasses import dataclass
from aps_digitaltwin.model import Model
from aps_digitaltwin.openaps import OpenAPS
from aps_digitaltwin.util import s_label, j_label, l_label, g_label, i_label, BOLUS, BASAL_BOLUS_THRESHOLD
from aps_digitaltwin.util import LOW, HIGH, BASAL_BOLUS_THRESHOLD, BOLUS, SNACK, LIGHT_MEAL, HEAVY_MEAL, constant_names

def initial_values(self):
    return [initial_carbs, initial_jej, initial_il, initial_bg, initial_iob]

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
):
    model_control = Model(initial_values(), constants)

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
    recorded_carbs=None,
    plot=False,
    model_control=False,
    tempdir="openaps_temp",
    profile_path=None,
    basal_profile_path=None,
    kill_at_fault=False,
    timesteps_per_intervention=5,
):
    initial_carbs = attack["initial_carbs"],
    initial_bg = attack["initial_bg"],
    initial_iob = attack["initial_iob"],

    if model_control:
        control_df = run_control(constants,
                                 plot=plot,
                                 kill_at_fault=kill_at_fault,
                                 timesteps=timesteps,
                                 timesteps_per_intervention=timesteps_per_intervention)

    open_aps = OpenAPS(recorded_carbs, profile_path=profile_path, basal_profile_path=basal_profile_path)
    model_openaps = Model(initial_values(), constants, interventions=interventions)

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