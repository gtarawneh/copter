## Copter User Manual

### Installation

Follow the instructions below to install and setup Copter:

1. Install [Microsoft Z3](https://github.com/Z3Prover/z3/releases) (v4.5.0 or higher)
2. Install the Python module `docopt` (`pip install docopt`)
3. Add Z3's Python module path to the environmental variable `PYTHONPATH`:

`export PYTHONPATH=$PYTHONPATH:/z3-4.5.0-x64-ubuntu-14.04/bin/python`

(adjust appropriately for your system)

Notes:

1. `pip` is package manager for Python which may not be installed by default
on your system. If `pip` is not installed (run `pip -V` to check) then follow
[these instructions](https://pip.pypa.io/en/stable/installing/).

### Command Line Interface

```
Composability Optimizer (Copter)

Usage:
  copter.py [--mode=<m>] [--output=<file>] [--quiet|--print] <problem.json>...
  copter.py --version

Options:
  -m --mode=<m>       Choose optimization mode (unique/count) [default: unique].
  -o --output=<file>  Write solution to json file.
  -p --print          Print problem (rules, costs and system).
  -q --quiet          Suppress output.
```

### Example Usage

The input is a JSON file containing a list of rules, a dictionary of module
costs and the system specification to optimize. For example:

```JSON
{
    "rules": [
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
    "system": [
        "outputRise x y z",
        "inputFall x y z",
        "outputFall x y z",
        "inputRise x y z"
    ]
}
```

This example is included in the `examples` directory. To run it, execute:

`./copter.py examples/circuit2.json`

and Copter will produce the following output:

```
System Modules             : 4
Unique Cost Elements       : 48
Unique Rules               : 48

Solution:

["handshake x z", "handshake y z"]

Cost : 4
```

Note: the example above uses _parameterized rules_.

### Input Format

The input file must be a JSON dictionary containing the keys `rules` and
`system`. `rules` is a list of compositions rule strings and `system` is a
composable system specification in one of the formats:

* `"module1 param1 param2 . module2 param1 param2"`
* `["module1 param1 param2", "module2 param1 param2"]`

The `costs` dictionary is optional. If `costs` is incomplete or not included
in the input file then any unknown module costs will be assumed `1` by
default. The default behavior of `Copter` is therefore to minimize the _number
of modules_ in the specification.

Additionally, a dictionary file with override module costs can be load using
the `--costs` switch. This provides a mechanism to specifyu

is useful for users wishing to reuse several cost
profiles across a number of problems
