#!/bin/bash

for i in {0..2}
do
  echo "#!/bin/bash
#PBS -l nodes=1:ppn=1,walltime=03:00:00
#PBS -M helen.youshan@gmail.com
cd /projects/leam/LEAM
python stocasticgreedy_randomwalk.py $i >output$i.txt"> ./pbs/pbs.script.$i
done

