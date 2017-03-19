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
  copter.py [--mode=<m>] [--output=<file>] [--quiet|--print]
            [--costs=<list>] <problem.json>...
  copter.py --version

Options:
  -m --mode=<m>       Choose optimization mode (unique/count) [default: unique].
  -o --output=<file>  Write solution to json file.
  -c --costs=<list>   Override costs (<list> is mod1:cost1,mod2:cost2 ...).
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
Problem Statistics:
    - System Modules             : 4
    - Defined Costs              : 12
    - Defined Rules              : 8
    - Expanded Costs             : 48
    - Expanded Rules             : 16

Solution (cost = 4):

handshake x z . handshake y z
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

#### Multiple Input Files

Copter can load a problem from multiple files. For example, running Copter
with the following arguments:

```
./copter.py file1.json file2.json file3.json
```

will concatenate the dictionaries from all three files. This enables users to
maintain rules, costs and system specifications independently (useful to
analyze different systems with the same set of rules for example). If there
are conflicting cost entries in different files then precedence will be given
to those in later files (e.g. costs in `file3.json` override those in earlier
files).

When loading a problem from multiple files, Copter can be ran with the
`--print` switch to pretty print the problem. This can be used to ensure the
concatenated system/rules and any overriden cost entries are what the user is
expecting. For example:

```
./copter.py --print examples/circuit2.json

Rules:
    - outputRise a b c         =  cause_rr a c . cause_rr b c
    - inputFall a b c          =  cause_rf c a . cause_rf c b
    - outputFall a b c         =  cause_ff a c . cause_ff b c
    - inputRise a b c          =  cause_fr c a . cause_fr c b
    - cElement a b c           =  buffer a c . buffer b c
    - inverter a b             =  cause_rf a b . cause_fr a b
    - buffer a b               =  cause_rr a b . cause_ff a b
    - handshake b c            =  buffer b c . inverter c b

Costs:
    - cause_ff                 = 20
    - handshake                = 2
    - cause_rf                 = 20
    - buffer                   = 5
    - inputRise                = 10
    - outputRise               = 10
    - cause_rr                 = 20
    - cElement                 = 1
    - outputFall               = 10
    - cause_fr                 = 20
    - inverter                 = 5
    - inputFall                = 10

System:
    - outputRise x y z
    - inputFall x y z
    - outputFall x y z
    - inputRise x y z

Problem Statistics:
    - System Modules             : 4
    - Defined Costs              : 12
    - Defined Rules              : 8
    - Expanded Costs             : 48
    - Expanded Rules             : 16

Solution (cost = 4):

handshake x z . handshake y z
```

#### Overriding Costs

For scripting purposes, Copter enables users to supply cost definitions using
the switch `--cost`. For example:

```
./copter.py --costs=handshake:50,buffer:10 examples/circuit2.json base_costs.json
```

Costs passed as arguments to `--costs` take highest precedence and will
override any that are loaded from files.
