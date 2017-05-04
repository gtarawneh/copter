run: solve_david

prepare_output:
	@ date > output.log
	@ echo "" >> output.log

solve_david: prepare_output
	@ ./solve_david.py >> output.log 2>&1

cover: prepare_output
	@ ./cover.py >> output.log 2>&1

parse_sg: prepare_output
	@ ./parse_sg.py >> output.log 2>&1

david3: prepare_output
	@ ./copter.py \
		examples/concepts.json \
		examples/concepts-costs.json \
		examples/concepts-meta.json \
		examples/david3.json \
		>> output.log 2>&1

circuit2: prepare_output
	@ ./copter.py \
		--mode=inclusive \
		examples/concepts.json \
		examples/concepts-meta.json \
		examples/circuit2.json \
		>> output.log 2>&1

vme-read: prepare_output
	@ ./copter.py \
		--mode=inclusive \
		examples/concepts.json \
		examples/concepts-meta.json \
		examples/vme-read.json \
		>> output.log 2>&1

vme-controller: prepare_output
	@ ./copter.py \
		--mode=inclusive \
		examples/concepts.json \
		examples/concepts-meta.json \
		examples/vme-write.json \
		examples/vme-read.json \
		examples/vme-controller.json \
		>> output.log 2>&1
