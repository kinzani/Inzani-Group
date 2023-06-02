#!/bin/bash

#SBATCH --job-name=OMC_yyy_U_zzz
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=128
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=3850

#SBATCH --time=48:00:00
#SBATCH --account=su006-040

###SBATCH --partition=compute

#SBATCH --mail-type=ALL
#SBATCH --mail-user=rated.beta@gmail.com

module purge
module load intel/2019b

export OMP_NUM_THREADS=1
export LD_LIBRARY_PATH=/sulis/easybuild/software/imkl/2019.5.281-gompi-2019b/mkl/lib/intel64:$LD_LIBRARY_PATH

EXE="/home/d/dcriveanu/VASP/vasp.5.4.4_2019bCompiler/vasp.5.4.4/bin/vasp_std"

time srun $EXE
