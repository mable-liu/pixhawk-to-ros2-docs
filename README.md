# Connecting Pixhawk to ROS 2

Documentation for setting up a Raspberry Pi as a companion computer for a Pixhawk
flight controller, so PX4 flight data appears as ROS 2 topics on the network.

**Read the docs: https://ura-docs.readthedocs.io/en/latest/**

## Building locally

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/sphinx-autobuild . _build/html --open-browser
```

That serves the site at http://localhost:8000 and rebuilds whenever you save.

Before pushing, check the build the same way Read the Docs does. It treats warnings
as errors, so a broken cross-reference fails the build instead of publishing a dead
link:

```bash
.venv/bin/python -m sphinx -b html -W . _build/html
```

Exit code 0 means Read the Docs will build it.
