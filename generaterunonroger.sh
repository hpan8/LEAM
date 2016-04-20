rm runroger.sh
for i in $(seq 1 100):
do 
     echo "module load goal.stack && source mypy/bin/activate && python stocasticgreedy_randomwalk.py "$i >> runroger.sh
done
 
