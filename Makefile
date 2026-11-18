# make          build every C program (or: make count, make pipeline-A, make pipeline-B, make small)
# make quick    build, then run the quick checks (run_quick.sh, about 2 minutes)
CC       = gcc
CFLAGS  ?= -O2
OMPFLAGS = -fopenmp

COUNT = count/dc count/place count/classes count/split count/cnt count/cntf count/tilings
PA    = pipeline-A/bsearch pipeline-A/ub pipeline-A/ubv pipeline-A/ubr
PB    = pipeline-B/code/tile pipeline-B/code/count pipeline-B/code/dset pipeline-B/code/comp \
        pipeline-B/code/mcheck pipeline-B/code/check_arrays
SMALL = small/cnt small/bfa small/bfb small/bb small/bb3

all: count pipeline-A pipeline-B small
count: $(COUNT)
pipeline-A: $(PA)
pipeline-B: $(PB)
small: $(SMALL)

count/cnt count/cntf: count/count.h
count/%: count/%.c
	$(CC) $(CFLAGS) -o $@ $<

pipeline-A/%: pipeline-A/%.c
	$(CC) $(CFLAGS) -o $@ $<

pipeline-B/code/%: pipeline-B/code/%.c pipeline-B/code/common.h
	$(CC) $(CFLAGS) $(OMPFLAGS) -o $@ $<

small/%: small/%.c
	$(CC) $(CFLAGS) -o $@ $<

quick: all
	./run_quick.sh

clean:
	rm -f $(COUNT) $(PA) $(PB) $(SMALL)

.PHONY: all count pipeline-A pipeline-B small quick clean
