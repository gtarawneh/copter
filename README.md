## Composability Optimizer (Copter)

### What is it

Copter is a tool for optimizing composable systems. A composable system is a
collection of _modules_ that can be assembled or decomposed according to
certain _rules_. For example, a `bicycle` is a composable system that can be
specified as:

`bicycle = wheels . frame . seat`

where `.` is a composition operator. Each _module_ may itself be a composable
system. For example:

* `wheels = front_wheel . rear_wheel`
* `frame = hub . spokes . rim . tire . tube`
* `seat = saddle . post`

making the following an alternative valid specification for `bicycle`:

`bicycle = front_wheel . rear_wheel . frame . saddle . post`

Modules that cannot be decomposed into other modules are `atoms`. All
composable systems can be reduced to collections of atoms.

Given a specification of a composable system with large numbers of atoms and
rules, it is sometimes useful to find alternative specifications that are
shorter, less/more verbose or free from (or inclusive of) certain modules. For
example, one may be interested in finding a simpler specification equivalent
to:

`something = front_wheel . rear_wheel . saddle . post`

which would be `something = wheels . seat`, or another specification which is
less verbose but still contains the module `saddle` such as `something =
wheels . saddle . post`.

Alternative specifications such as these can be found by Copter. Copter is an
optimization tool for composable system specifications based on
[Z3](https://github.com/Z3Prover/z3). The tool is developed primarily to
optimize [Concepts](https://github.com/tuura/plato) (a DSL for expressing
asynchronous circuits using behavioral compositions) but can be used with
arbitrary composable systems.

### Manual

For installation and usage instructions, see [the
manual](https://github.com/gtarawneh/copter/blob/master/doc/manual.md).
