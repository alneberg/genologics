#!/usr/bin/env python
from argparse import ArgumentParser
from genologics.lims import Lims
from genologics.entities import Project,Process,Artifact
from genologics.epp import configure_logging
import yaml
import sys
from collections import defaultdict

example_info={'details': [{'algorithm': {'aligner': 'novoalign',
                                         'quality_format': 'Standard',
                                         'variantcaller': 'gatk'},
                           'analysis': 'variant2',
                           'description': 'Sample 1',
                           'files': ['/path/to/1_1-fastq.txt', '/path/to/1_2-fastq.txt'],
                           'genome_build': 'GRCh37'},
                          {'analysis': 'Minimal',
                           'description': 'Multiplex example',
                           'genome_build': 'hg19',
                           'multiplex': [{'barcode_id': 1,
                                          'barcode_type': 'Illumina',
                                          'name': 'One Barcode Sample',
                                          'sequence': 'ATCACG'},
                                         {'barcode_id': 2,
                                          'barcode_type': 'Illumina',
                                          'name': 'Another Barcode Sample',
                                          'sequence': 'CGATGT'}]}],
              'fc_date': '110812',
              'fc_name': 'unique_name',
              'upload': {'dir': '../final'}}

default_info={'details': [{'algorithm': {'aligner': 'novoalign',
                                         'quality_format': 'Standard',
                                         'variantcaller': 'gatk'},
                           'analysis': 'variant2',
                           'description': 'Sample 1',
                           'files': ['/path/to/1_1-fastq.txt', '/path/to/1_2-fastq.txt'],
                           'genome_build': 'GRCh37'},
                          {'analysis': 'Minimal',
                           'description': 'Multiplex example',
                           'genome_build': 'hg19',
                           'multiplex': [{'barcode_id': 1,
                                          'barcode_type': 'Illumina',
                                          'name': 'One Barcode Sample',
                                          'sequence': 'ATCACG'},
                                         {'barcode_id': 2,
                                          'barcode_type': 'Illumina',
                                          'name': 'Another Barcode Sample',
                                          'sequence': 'CGATGT'}]}],
              'fc_date': '110812',
              'fc_name': 'unique_name',
              'upload': {'dir': '../final'}}

def main(lims,processid,outfile):
    process = Process(lims,id=processid)
    io = process.input_output_maps
    io_filtered = filter(lambda (x,y): y['output-generation-type']=='PerInput',io)
    projects = defaultdict(list)
    for input,output in io_filtered:
        i_a = Artifact(lims,id=input['limsid'])
        for sample in i_a.samples:
            projects[sample.project].append(sample)
    
    print projects.keys()
    import tarfile
    outtar = tarfile.open(outfile,'w:gz')
    for i,p in enumerate(projects):
        try:
            a = p.udf['Application']
        except:
            sys.stderr.write(('Error while collecting Application udf from project '
                              'with id{0}').format(projectid))
            raise
        fn = p.id+'.yml'
        print 'Created a yml file named: {0}'.format(fn)
        tmp = file(fn,'wb')
        default_info['details'][1]['analysis'] = a
        yaml.dump(default_info,tmp,default_flow_style=False)
        tarinfo = tarfile.TarInfo(fn)
        outtar.add(fn)
        import os
        os.remove(fn)
    outtar.close()

if __name__=="__main__":
    parser = ArgumentParser()
    parser.add_argument('--username',
                        help='The user name')
    parser.add_argument('--password',
                        help='Password')
    parser.add_argument('--baseuri',
                        help='Uri for the lims server')
    parser.add_argument('--pid',
                        help='Process Lims Id')
    parser.add_argument('-l','--log',default=None,
                        help='Log file')
    parser.add_argument('--outfile',
                        help='Name of outputfile')

    args = parser.parse_args()

    if args.log:
        configure_logging(args.log)

    lims = Lims(args.baseuri,args.username,args.password)
    lims.check_version()

    main(lims,args.pid,args.outfile)
