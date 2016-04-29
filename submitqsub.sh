#!/bin/bash

for i in {0..2}; do qsub ./pbs/pbs.script.$i; done
