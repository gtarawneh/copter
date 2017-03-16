## Copter User Manual

### Installation

To setup the tool, following the instructions below:

1. Install [Microsoft Z3](https://github.com/Z3Prover/z3/releases) (version 4.5.0 or higher)
2. Install the Python module `docopt` (`pip install docopt`)
3. Add the path to Z3's Python module to the environmental variable `PYTHONPATH`:

`export PYTHONPATH=$PYTHONPATH:/z3-4.5.0-x64-ubuntu-14.04/bin/python`

Notes:

1. `pip` is package manager for Python which may not be installed by default
on your system (run `pip -V` to check if `pip` is installed). If not then
follow [these instructions](https://pip.pypa.io/en/stable/installing/) to
install `pip`.

### Command Line Interface

```
Composability Optimizer (Copter)

Usage:
  copter.py [--plato] [--mode=<m>] [--output=<file>] [--quiet] <problem.json>
  copter.py --version

Options:
  -p --plato          Load problem file in Plato format.
  -m --mode=<m>       Choose optimization mode (unique/count) [default: unique].
  -o --output=<file>  Write solution to json file.
  -q --quiet          Suppress output.
```

### Example Usage

The input is a JSON file containing a list of rules (concepts), a dictionary
of module costs and the system (circuit) specification to optimize. For
example:

```JSON
{
    "concepts": [
        "outputRise a b c = cause_rr a c . cause_rr b c",
        "inputFall a b c = cause_rf c a . cause_rf c b",
        "outputFall a b c = cause_ff a c . cause_ff b c",
        "inputRise a b c = cause_fr c a . cause_fr c b",
        "cElement a b c = buffer a c . buffer b c",
        "inverter a b  = cause_rf a b . cause_fr a b",
        "buffer a b = cause_rr a b . cause_ff a b",
        "handshake b c = buffer b c . inverter c b"
    ],
    "costs": {
        "cause_rr": 20,
        "cause_ff": 20,
        "cause_rf": 20,
        "cause_fr": 20,
        "outputRise": 10,
        "inputFall": 10,
        "outputFall": 10,
        "inputRise": 10,
        "buffer": 5,
        "inverter": 5,
        "handshake": 2,
        "cElement": 1
    },
    "circuit": [
        "outputRise x y z",
        "inputFall x y z",
        "outputFall x y z",
        "inputRise x y z"
    ]
}
```
This example is included in the `examples` directory. To run it, execute:

`./copter.py --plato examples/circuit2.json`

The tool will now produce:

```
Circuit Elements           : 4
Unique Cost Elements       : 48
Unique Decompositions      : 48

Solution:

["handshake a c", "handshake b c"]

Cost : 4
```

Note: the examples above uses _parameterized rules_.
