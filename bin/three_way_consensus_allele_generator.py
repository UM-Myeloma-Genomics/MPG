#!/usr/bin/env python

"""
This script generates a consensus major/minor allele BED file based on the per-segment agreement between the three
CNV callers included in the MGP1000 pipeline.
"""
import sys

class AlleleSegment(object):

    def __init__(self, allele_segment_line):
        """Parse merged allele segment file to construct object"""
        chrom, start, end, battenberg_alleles, controlfreec_alleles, facets_alleles = allele_segment_line.rstrip().split('\t')
        self.chrom = chrom
        self.start  = start
        self.end = end
        self.battenberg_alleles = battenberg_alleles
        self.controlfreec_alleles = controlfreec_alleles
        self.facets_alleles = facets_alleles
        self.na_count = (battenberg_alleles, controlfreec_alleles, facets_alleles).count('.')
        self.alleles_dict = {"battenberg": battenberg_alleles,
                             "controlfreec": controlfreec_alleles,
                             "facets": facets_alleles}

def consensus_writer(consensus_allele_segment_tuple):
    """Return output BED line with allele consensus of per segment"""
    return '\t'.join(consensus_allele_segment_tuple)

input_args = sys.argv

consensus_allele_bed = open(input_args[2], 'w')

header = ("chrom", "start", "end",
          "consensus_major_allele", "consensus_minor_allele", "allele_caller_agreement",
          "battenberg_alleles", "controlfreec_alleles", "facets_alleles")
consensus_allele_bed.write('{0}\n'.format(consensus_writer(header)))

with open(input_args[1]) as merged_allele_file:
    for line in merged_allele_file:
        allele_obj = AlleleSegment(line)

        # First, check for how many tools generated a call for the segment
        if allele_obj.na_count == 2:

            # Output major/minor alleles is equal to call from single tool
            single_caller_allele = [(key,value) for (key,value) in allele_obj.alleles_dict.items() if value != '.'][0]
            single_caller_allele_tuple = (allele_obj.chrom, allele_obj.start, allele_obj.end,
                                          single_caller_allele[1].replace("/", "\t"), single_caller_allele[0],
                                          allele_obj.battenberg_alleles, allele_obj.controlfreec_alleles, allele_obj.facets_alleles)
            consensus_allele_bed.write('{0}\n'.format(consensus_writer(single_caller_allele_tuple)))

        elif allele_obj.na_count == 1:
            double_caller_allele = [(key,value) for (key,value) in allele_obj.alleles_dict.items() if value != '.']

            # If more than 1 tool generated a call for the segment, determine if the calls match
            if double_caller_allele[0][1] == double_caller_allele[1][1]:
                double_caller_agreement_allele_callers = ','.join([double_caller_allele[0][0], double_caller_allele[1][0]])
                double_caller_agreement_allele_tuple = (allele_obj.chrom, allele_obj.start, allele_obj.end,
                                                        double_caller_allele[0][1].replace("/", "\t"), double_caller_agreement_allele_callers,
                                                        allele_obj.battenberg_alleles, allele_obj.controlfreec_alleles, allele_obj.facets_alleles)
                consensus_allele_bed.write('{0}\n'.format(consensus_writer(double_caller_agreement_allele_tuple)))

            else:
                double_caller_no_agreement_allele_tuple = (allele_obj.chrom, allele_obj.start, allele_obj.end,
                                                           ".", ".", "no_agreement",
                                                           allele_obj.battenberg_alleles, allele_obj.controlfreec_alleles, allele_obj.facets_alleles)
                consensus_allele_bed.write('{0}\n'.format(consensus_writer(double_caller_no_agreement_allele_tuple)))

        # If 3 tools generated a call for the segment, determine if the calls match
        elif allele_obj.na_count == 0:
            triple_caller_allele_dict = {}

            for caller,allele in allele_obj.alleles_dict.items():
                if allele not in triple_caller_allele_dict:
                    triple_caller_allele_dict[allele] = [caller]
                else:
                    triple_caller_allele_dict[allele].append(caller)

            # Catch segments with full agreement between 3 tools
            if len(triple_caller_allele_dict.keys()) == 1:
                triple_caller_full_agreement_allele_callers = ','.join(*triple_caller_allele_dict.values())
                triple_caller_full_agreement_allele_tuple = (allele_obj.chrom, allele_obj.start, allele_obj.end,
                                                             '{0}'.format(*triple_caller_allele_dict).replace("/", "\t"), triple_caller_full_agreement_allele_callers,
                                                             allele_obj.battenberg_alleles, allele_obj.controlfreec_alleles, allele_obj.facets_alleles)
                consensus_allele_bed.write('{0}\n'.format(consensus_writer(triple_caller_full_agreement_allele_tuple)))

            # Catch segments with split agreement where 2/3 tools agree
            elif len(triple_caller_allele_dict.keys()) == 2:
                triple_partial_agreement_allele = [*triple_caller_allele_dict.keys()]
                triple_partial_agreement_allele_callers = [*triple_caller_allele_dict.values()]

                if len(triple_partial_agreement_allele_callers[0]) > len(triple_partial_agreement_allele_callers[1]):
                    triple_caller_partial_agreement_pair1_allele_callers = ','.join(triple_partial_agreement_allele_callers[0])
                    triple_caller_partial_agreement_pair1_tuple = (allele_obj.chrom, allele_obj.start, allele_obj.end,
                                                                   triple_partial_agreement_allele[0].replace("/", "\t"), triple_caller_partial_agreement_pair1_allele_callers,
                                                                   allele_obj.battenberg_alleles, allele_obj.controlfreec_alleles, allele_obj.facets_alleles)
                    consensus_allele_bed.write('{0}\n'.format(consensus_writer(triple_caller_partial_agreement_pair1_tuple)))

                else:
                    triple_caller_partial_agreement_pair2_allele_callers = ','.join(triple_partial_agreement_allele_callers[1])
                    triple_caller_partial_agreement_pair2_allele_tuple = (allele_obj.chrom, allele_obj.start, allele_obj.end,
                                                                          triple_partial_agreement_allele[1].replace("/", "\t"), triple_caller_partial_agreement_pair2_allele_callers,
                                                                          allele_obj.battenberg_alleles, allele_obj.controlfreec_alleles, allele_obj.facets_alleles)
                    consensus_allele_bed.write('{0}\n'.format(consensus_writer(triple_caller_partial_agreement_pair2_allele_tuple)))

            # Catch segment with no agreement between the 3 tools
            else:
                triple_caller_no_agreement_allele_tuple = (allele_obj.chrom, allele_obj.start, allele_obj.end,
                                                           ".", ".", "no_agreement",
                                                           allele_obj.battenberg_alleles, allele_obj.controlfreec_alleles, allele_obj.facets_alleles)
                consensus_allele_bed.write('{0}\n'.format(consensus_writer(triple_caller_no_agreement_allele_tuple)))

consensus_allele_bed.close()
