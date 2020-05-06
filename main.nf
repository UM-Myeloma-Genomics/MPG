//  |\        /|   /---------\  /---------\
//  | \      / |  |             |         |
//  |  \    /  |  |   /------\  |---------/
//  |   \  /   |  |          |  |
//  |    \/    |   \---------/  |

input_fastq = Channel.value( 'U0a_CGATGT_L001_R1_001.fastq.gz' )
params.output_dir = "output"

process test {
	input:
	file fastq from input_fastq

	"echo fastq"
}

//process fastqc {
//	tag "${fastq}"
//	publishDir "${params.output_dir}/fastqc", mode: 'copy', overwrite: true
//	echo true
//
//	input:
//	file(fastq) from input_fastqs
//
//	output:
//	file(output_html)
//	file(output_zip)
//
//	script:
//	output_html = "${fastq}".replaceFirst(/.fastq.gz$/, "_fastqc.html")
//	output_zip = "${fastq}".replaceFirst(/.fastq.gz$/, "_fastqc.zip")
//	"""
//	fastqc -o . "${fastq}"
//	"""
//}