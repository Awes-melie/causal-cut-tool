import argparse

parser = argparse.ArgumentParser(prog="g_estimation", description="Causal testing for a provided system.")
parser.add_argument("-a", "--attacks", type=str, help="Path to JSON attacks file.", required=True)
parser.add_argument("-d", "--dag", type=str, help="Path to dag file.", required=True)
parser.add_argument(
    "-s",
    "--safe_ranges",
    type=str,
    help="Path to JSON file defining safe ranges for the output variables.",
    required=True,
)
parser.add_argument(
    "-t", "--timesteps_per_intervention", type=int, help="Timesteps per intervention (defaults to 1).", default=1
)
parser.add_argument(
    "-o",
    "--outfile",
    type=str,
    help="Path to save JSON results file (defaults to `logs/log.json`).",
    default="logs/log.json",
)
parser.add_argument("-b", "--background", nargs="+", help="The background confounders.", default=[])
parser.add_argument(
    "-A",
    "--adequacy",
    help="Specify this flag to record the causal test adequacy. (This will significantly increase the runtime.)",
    action="store_true",
)
parser.add_argument(
    "-S",
    "--silent",
    help="Silence exceptions and store them as part of the result rather than crashing early.",
    action="store_true",
)
parser.add_argument(
    "-i",
    "--attack_index",
    type=int,
    help="The index of the attack to execute.",
    required=False,
)
parser.add_argument(
    "-I",
    "--intervention_index",
    type=int,
    help="The index of the intervention to execute.",
    required=False,
)
parser.add_argument(
    "-c",
    "--ci_alpha",
    type=float,
    help="The alpha to use in confidence intervals.",
    default=0.05,
)
parser.add_argument(
    "-T",
    "--total_time",
    type=int,
    help="The total time of the study.",
    required=True,
)
parser.add_argument(
    "-B",
    "--block_size",
    type=int,
    help="The number of interventions to consider at once.",
    default=1,
)
parser.add_argument(
    "-n",
    "--num_individuals",
    type=int,
    help="The number of individuals in the study.",
    default=None,
)
parser.add_argument(
    "--start_time",
    type=int,
    help="The start time.",
    default=0,
)
parser.add_argument("datafile", type=str, help="Path to the long format data file.")

def get_args():
    args = parser.parse_args()
    return args