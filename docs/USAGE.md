# Getting Started & Usage Guide

This guide walks you through setting up the project from a fresh download and running every
script, including ad-hoc experiments with your own parameters. It assumes no prior knowledge of
`uv`.

> **TL;DR for reviewers:** install `uv`, then from the project folder run `uv sync` once, and
> run anything with `uv run python scripts/<name>.py`. The committed figures in `outputs/` already
> show the headline results if you'd rather not run anything.

---

## 1. Prerequisites

You need two things:

1. **Git** (only if you want to `clone`; you can also download a ZIP — see below).
2. **[uv](https://docs.astral.sh/uv/)** — a fast Python package/environment manager from Astral.
   It creates the virtual environment, installs the exact pinned dependencies, and will even
   fetch the correct Python version (3.12) for you. **You do not need to install Python yourself.**

### Install uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux (bash/zsh):**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

After installing, **open a new terminal** so `uv` is on your `PATH`, then confirm:
```bash
uv --version
```

> **Windows note:** uv installs to `C:\Users\<you>\.local\bin`. If `uv` isn't found in a terminal
> that was already open before you installed it, either open a fresh terminal, or add it for the
> current session:
> ```powershell
> $env:Path = "$env:USERPROFILE\.local\bin;$env:Path"
> ```

---

## 2. Get the code

**Option A — clone with Git:**
```bash
git clone https://github.com/chrisn1983/driven-pendulum.git
cd driven-pendulum
```

**Option B — download a ZIP:** on the GitHub page click **Code ▸ Download ZIP**, unzip it, and
open a terminal in the unzipped folder.

---

## 3. One-time setup

From the project folder, create the environment and install dependencies:
```bash
uv sync
```
This reads `pyproject.toml` + `uv.lock`, creates a `.venv/` folder, and installs the exact,
reproducible dependency versions. It takes ~10–20 seconds the first time and is instant afterwards.

You **do not** need to "activate" the virtual environment — `uv run` (below) uses it automatically.

---

## 4. Run the example scripts

Every script is run with `uv run python scripts/<name>.py` and writes its figures (and some CSVs)
into the `outputs/` folder.

```bash
uv run python scripts/run_timeseries.py      # angle & velocity vs time (regular + chaotic)
uv run python scripts/run_phase_portrait.py  # phase portraits + energy plots
uv run python scripts/run_resonance.py       # resonance curves for three damping values
uv run python scripts/run_poincare.py        # stroboscopic Poincaré section (strange attractor)
uv run python scripts/run_bifurcation.py     # bifurcation diagram — the route to chaos
uv run python scripts/run_sensitivity.py     # divergence of two near-identical trajectories
uv run python scripts/run_animation.py       # animated GIF of the swinging pendulum

uv run python scripts/run_all.py             # run all of the above in sequence
```

Most finish in a second or two. `run_poincare.py` and `run_bifurcation.py` perform many
integrations and take ~30–60 seconds — that's expected.

**Viewing results:** open the PNG/GIF files in `outputs/` with any image viewer. The CSV files
(raw time series) open in Excel, or with pandas.

---

## 5. Run your own experiment — `run_custom.py`

[`scripts/run_custom.py`](../scripts/run_custom.py) runs a single simulation with parameters you
choose on the command line, prints a summary, saves figures + a CSV, and can pop the plots on
screen with `--show`.

### Examples — copy/paste these

Pick your own amplitude and frequency, run for 60 s, and open the plots in a window:
```bash
uv run python scripts/run_custom.py --A 1.3 --omega 2.7 --t 60 --show
```

Let it choose **random** drive parameters for you (great for open-ended exploration):
```bash
uv run python scripts/run_custom.py --random --t 60 --show
```

The canonical **chaotic** set — watch it never settle:
```bash
uv run python scripts/run_custom.py --A 2.5 --omega 3.0 --t 60 --show
```

A gentle drive near the **natural frequency** (ω₀ ≈ 3.13) to see **resonance** build up:
```bash
uv run python scripts/run_custom.py --A 0.1 --omega 3.13 --t 60 --show
```

Save a run under its own name (so it doesn't overwrite previous experiments), without opening a
window:
```bash
uv run python scripts/run_custom.py --A 0.8 --omega 2.0 --t 60 --name gentle_swing
```

Change the pendulum itself — a longer, less-damped pendulum:
```bash
uv run python scripts/run_custom.py --L 2.0 --b 0.1 --A 1.0 --omega 2.0 --t 90 --show
```

### All available flags

| Flag           | Meaning                          | Default   |
|----------------|----------------------------------|-----------|
| `--A`          | drive amplitude (m)              | `1.0`     |
| `--omega`      | drive frequency (rad/s)          | `2.5`     |
| `--b`          | damping coefficient (1/s)        | `0.5`     |
| `--L`          | pendulum length (m)              | `1.0`     |
| `--g`          | gravity (m/s²)                   | `9.81`    |
| `--theta0`     | initial angle (rad)              | `0.2`     |
| `--theta-dot0` | initial angular velocity (rad/s) | `0.0`     |
| `--t`          | simulation end time (s)          | `60.0`    |
| `--n-points`   | number of output samples         | `6000`    |
| `--name`       | output filename prefix           | `custom`  |
| `--show`       | open the figures in a window     | off       |
| `--random`     | ignore `--A`/`--omega`, randomise them | off |

> **Note:** `--random` **overrides** `--A`/`--omega`. Use one approach or the other.

It always writes `outputs/<name>_timeseries.png`, `<name>_phase.png`, `<name>_energy.png`, and
`<name>.csv`, and prints a summary including the maximum angle and whether the pendulum went *over
the top*.

### Telling periodic from chaotic

A quick objective check — integrate two trajectories a hair apart and see if they diverge:
```bash
uv run python -c "from driven_pendulum import PendulumParameters, sensitivity_to_initial_conditions as s; r=s(PendulumParameters(A=2.5, omega=3.0, b=0.5), t_span=(0,80)); print('divergence factor: %.2e' % (r.separation[-1]/r.delta0))"
```
A factor near **1** means **periodic**; a factor of **10⁹–10¹¹** means **chaotic**.

---

## 6. Use the library directly (Python)

```python
from driven_pendulum import DrivenPendulum, PendulumParameters

params = PendulumParameters(L=1.0, b=0.5, A=2.5, omega=3.0)
result = DrivenPendulum(params).simulate(theta0=0.2, t_span=(0, 60), n_points=6000)

df = result.to_dataframe()        # raw + derived data as a pandas DataFrame
result.to_csv("outputs/run.csv")  # or straight to CSV
```

Run a snippet like this with `uv run python my_script.py` or `uv run python -c "..."`.

---

## 7. Run the tests

The physics-validation test suite (29 tests) is run with:
```bash
uv run pytest
```

---

## 8. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `uv : The term 'uv' is not recognized…` | The terminal opened before uv was installed. Open a new terminal, or run `$env:Path = "$env:USERPROFILE\.local\bin;$env:Path"` (PowerShell). |
| A plot window appears and the script seems to hang | That's `--show` waiting for you to close the window. Close it to continue, or omit `--show` to just save files. |
| `warning: VIRTUAL_ENV=… does not match the project environment` | Harmless. You have another virtual environment "activated"; `uv run` ignores it and uses this project's `.venv`. Run `deactivate` to silence it. |
| No plot window with `--show` on a server / headless machine | There's no display. The figures are still saved to `outputs/`; view the PNG files directly. |
| Want runs to never open windows | Set `MPLBACKEND=Agg` for the session (PowerShell: `$env:MPLBACKEND="Agg"`). |
