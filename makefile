run: parse_sg

prepare_output:
	@ date > output.log
	@ echo "" >> output.log

parse_sg: prepare_output
	@ ./parse_sg.py >> output.log 2>&1

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
