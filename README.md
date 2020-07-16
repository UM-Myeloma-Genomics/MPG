# UNDER ACTIVE DEVELOPMENT

# Myeloma Genome Project 1000
Comprehensive bioinformatics pipeline for the large-scale collaborative analysis of Multiple Myeloma genomes in an effort to deliniate the broad spectrum of somatic events

## Pipeline Overview
In order to analyze over one thousand matched tumor/normal whole-genome samples across multiple data centers in a consistent manner, a pipeline was created that leverages the workflow management, portability, and reproducibility of [Nextflow](http://www.nextflow.io/) in conjuction with [Singularity](https://sylabs.io/docs/).

The entire pipeline is divided into 3 steps: Preprocessing, Germline Variant Analysis, and Somatic Variant Analysis
This compartmentalizes the workflow and provides significant completion checkpoints which is effective for large-scale batch processing. 

<img src="https://github.com/pblaney/mgp1000/blob/master/MGP1000Pipeline.png" width="1000">

## Deploying the Pipeline
The pipeline was developed to be run on various HPCs without concern of environment incompatabilities, version issues, or missing dependencies. None of the commands require admin access or `sudo`  to be completed. However, there are a few assumptions regarding initial setup of the pipeline but the required software should be readily available in nearly all HPC environments.
* Git
* GNU Utilities
* Java 8 (or later)
* Singularity (validated on v3.1, other versions will be tested)

## Installing Git LFS
In an effort to containerize the pipeline further, all the necessary reference files used are stored in the GitHub repository using their complementary [Large File Storage (LFS)](https://git-lfs.github.com) extension. This requires a simple installation of the binary executible file at a location on your `$PATH`. The extension pairs seemlessly with Git to download all files while cloning the repository.
```
# Example of installation of Linux AMD64 binary executible git-lfs file, (other binary files: https://github.com/git-lfs/git-lfs/releases)
$ cd $HOME/bin
$ wget https://github.com/git-lfs/git-lfs/releases/download/v2.11.0/git-lfs-linux-amd64-v2.11.0.tar.gz && \
  tar -zxvf git-lfs-linux-amd64-v2.11.0.tar.gz && \
  git lfs install

### Note, these commands will clean the installation, leaving only the binary executible git-lfs file ###
$ rm git-lfs-linux-amd64-v2.11.0.tar.gz && \
  rm install.sh && \
  rm CHANGELOG.md && \
  rm README.md
```

## Clone GitHub Repository
The first step in the deployment process is to clone the MGP1000 GitHub repository to a location on your HPC that is large enough to hold the input/output data, like a scratch directory, and has access to the job scheduling software, such as SLURM or SGE.
```
$ cd <scratch dir>

$ git lfs clone https://github.com/pblaney/mgp1000.git
### Example output ###
# Cloning into 'mgp1000'...
# remote: Enumerating objects: 90, done.
# remote: Counting objects: 100% (90/90), done.
# remote: Compressing objects: 100% (71/71), done.
# remote: Total 307 (delta 33), reused 70 (delta 16), pack-reused 217
# Receiving objects: 100% (307/307), 415.32 KiB | 12.58 MiB/s, done.
# Resolving deltas: 100% (159/159), done.
# Filtering content: 100% (20/20), 9.63 GiB | 88.90 MiB/s, done.

$ cd mgp1000/
```

## Install Nextflow
This series of `make` commands will install Nextflow, and, optionally, test or update the current Nextflow installation. First, check for what current version of Java is available to the current environment.
```
$ java -version
### Example output ###
# openjdk version "1.8.0_131"
# OpenJDK Runtime Environment (build 1.8.0_131-b12)
# OpenJDK 64-Bit Server VM (build 25.131-b12, mixed mode)

$ make install-nextflow
### Example output ###
# curl -fsSL get.nextflow.io | bash
# CAPSULE: Downloading dependency .....
# ....
# ....
# 	  N E X T F L O W
#     version 20.04.1 build 5335
#     created 03-05-2020 19:37 UTC (15:37 EDT)
#     cite doi:10.1038/nbt.3820
#     http://nextflow.io
#
# Nextflow installation completed. Please note:
# - the executable file `nextflow` has been created in the folder: /gpfs/scratch/blanep01/mgp1000
# - you may complete the installation by moving it to a directory in your $PATH

# Move the binary executible nextflow file to same directory as git-lfs
$ mv nextflow $HOME/bin
```

## Prepare the Pipeline for Usage
Due to size, certain reference genome files are GNU zipped so these `make` commands will unzip them for use in the pipeline. Additionally, an `input` directory is created for staging all input BAM or FASTQ files, `preprocessedBams` subdirectory for BAMs that have undergone preprocessing and are ready for Germline/Somatic Variant Analysis steps, and a `logs` directory to store Nextflow output log files for each run.
```
$ make prep-pipeline
### Example output ###
# gunzip references/hg38/bwa/genome.fa.gz
# gunzip references/hg38/bwa/genome.fa.bwt.gz
# gunzip references/hg38/bwa/genome.fa.sa.gz
# mkdir -p input
# mkdir -p input/preprocessedBams
# mkdir -p logs
```

## Stage Input BAM or FASTQ Files
For the Preprocessing step of the pipeline, all input files are handled out of `input` directory that was created. Given the sheer size of the input data, the samples will have to be processed in batches. Additionally, the pipeline is designed to process batches of identical format, i.e. all BAMs or all FASTQs. One key assumption is that any input BAM file was trimmed for quality before being previously aligned. Another assumption is that any input FASTQs use an 'R1/R2' naming convention to designate paired-end read files.
```
# Example of staging input data files
$ cp -r </normal/samples/directory/*.bam> input/ 
```

## Run the Preprocessing Step of the Pipeline
Now the simplicity of Nextflow takes over. The Preprocessing step of the pipeline will be started with one command that will handle linking each individual process in the pipeline to the next. A key advantage of using Nextflow within an HPC environment is that will also perform all the job scheduling/submitting given the correct configuration with the user's [executor](https://www.nextflow.io/docs/latest/executor.html).
```
$ nextflow run preprocessing.nf --help
N E X T F L O W  ~  version 20.04.1
Launching `preprocessing.nf` [jolly_majorana] - revision: f5a75c24b1

##### Myeloma Genome Project 1000 Pipeline #####
################################################
~~~~~~~~~~~~~~~~~ PREPROCESSING ~~~~~~~~~~~~~~~~
################################################

Usage:

	nextflow run preprocessing.nf -bg --input_format fastq --singularity_module "singularity/3.1" -profile preprocessing

Mandatory Arguments:
	--input_format                 [str]  Format of input files, either: fastq or bam
	-profile                       [str]  Configuration profile to use, each profile described in nextflow.config file
	                                      Currently available: preprocessing

Main Options:
	-bg                           [flag]  Runs the pipeline processes in the background, this option should be included if deploying
	                                      pipeline with real data set so processes will not be cut if user disconnects from deployment
	                                      environment
	--singularity_module    [quoted str]  Indicates the name of the Singularity software module to be loaded for use in the pipeline,
	                                      this option is not needed if Singularity is natively installed on the deployment environment
	--skip_to_qc                   [str]  Skips directly to final Preprocessing QC step, either: yes or no 
	                                      can only be used in conjunction with bam as the input_format, should only be used for extreme
	                                      coverage BAMs that have been previously aligned with BWA MEM to the hg38 reference genome and
	                                      have adequate provenance to reflect this
	--help                        [flag]  Prints this message

################################################
```

