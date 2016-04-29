#!/bin/bash
module load parallel
time seq 0 99 | parallel python stocasticgreedy_randomwalk.py
