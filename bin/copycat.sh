#!/usr/bin/env bash
# This is a placeholder copy of the script developed by Maria Nattestad https://github.com/MariaNattestad/copycat

USAGE="
copycat alignments.sorted.bam genome_file output_prefix
\n\nalignments.sorted.bam:
\n\tBam file must be sorted.
\n\tRemember to filter for mapping quality first if desired: \n\tsamtools view -q -b BAM.bam > FILTERED_BAM.bam
\n\ngenome_file:
\n\tThe genome file should be structured as chromosome_name<TAB>chromosome_size\n\tFor example:\n\tchr1\t249250621\n\tchr2\t243199373
\n\noutput_prefix
\n\tPrefix for all output files. Output files will be output_prefix.coverage.10kb, output_prefix.coverage.10kb.csv, output_prefix.coverage.10kb.for_IGV.seg
"


if [ -z "$1" ]
  then
    echo "ERROR in Copycat: No alignments.sorted.bam file given"
    echo "Usage:"
    echo -e $USAGE
    exit
fi
if [ -z "$2" ]
  then
    echo -e "ERROR in Copycat: No genome_file given."
    echo "Usage:"
    echo -e $USAGE
    exit
fi
if [ -z "$3" ]
  then
    echo "ERROR in Copycat: No output_prefix given"
    echo "Usage:"
    echo -e $USAGE
    exit
fi

BAM=${1?"$USAGE"}
GENOME_FILE=${2?"$USAGE"}
OUT=${3?"$USAGE"}

# getting coverage for every basepair in the genome and making 10kb bins on the coverage
bedtools genomecov -d -ibam $BAM -g $GENOME_FILE | awk 'BEGIN{num=10000;sum=0;possum=0}{if(NR!=1){if(possum==10000 || chrom!=$1){print chrom,pos,sum/possum,possum;sum=0;possum=0;}}{sum+=$3;pos=$2;chrom=$1;possum+=1;}}' OFS="\t" > $OUT.coverage.10kb

# Create a .csv file:
awk 'BEGIN{start=0;print "chromosome,start,end,unsegmented_coverage"}{if(chrom!=$1){start=0}; print $1,start,$2,$3;start=$2;chrom=$1}' OFS="," $OUT.coverage.10kb > $OUT.coverage.10kb.csv
gzip $OUT.coverage.10kb.csv

# Create a .seg file for viewing in IGV
awk 'BEGIN{start=0}{if(chrom!=$1){start=0}; print "Coverage",$1,start,$2,$3;start=$2;chrom=$1}' OFS="\t" $OUT.coverage.10kb > $OUT.coverage.10kb.for_IGV.seg
