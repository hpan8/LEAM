#!/bin/bash

for i in {0..99}; do qsub ./pbs/pbs.script.$i; done
