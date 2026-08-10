#!/bin/bash
set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Usage: ./run_sim.sh <rounds> [--no-show] [extra args for monopoly.py]" >&2
    exit 1
fi

cd "$(dirname "$0")"

rounds=$1
shift

# --no-show belongs to the plotter; everything else goes to the simulation.
sim_args=()
plot_args=()
for arg in "$@"; do
    if [ "$arg" = "--no-show" ]; then
        plot_args+=("$arg")
    else
        sim_args+=("$arg")
    fi
done

# The ${a+"${a[@]}"} guard keeps `set -u` happy with empty arrays on bash 3.2,
# which is what macOS still ships.
python3 ./monopoly.py "$rounds" ${sim_args+"${sim_args[@]}"}
python3 ./display_histograms.py "$rounds" ${plot_args+"${plot_args[@]}"}
