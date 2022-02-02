#!/bin/bash

#SBATCH --output=output/out/slurm-%A-%a.out
#SBATCH --error=output/err/error-%A-%a.err
#SBATCH --array=1-360
#SBATCH --nodes=1
#SBATCH --exclusive
#SBATCH --partition=q1,q2,q3,q4

module refresh
module load use.own
module load java/jdk-17.0.1
echo "SLURM_JOB_ID:        $SLURM_JOB_ID"
echo "SLRUM_ARRAY_JOB_ID:  $SLURM_ARRAY_JOB_ID"
echo "SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_ID"
echo "SLURM_ARRAY_TASK_ID: $SLURM_ARRAY_TASK_COUNT"

python extractInformation-parallel.py $SLURM_ARRAY_TASK_ID

