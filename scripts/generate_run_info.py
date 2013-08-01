#!/usr/bin/env python
from argparse import ArgumentParser
from genologics.lims import Lims
from genologics.entities import Project,Process,Artifact
from genologics.epp import configure_logging
import yaml
import sys
import os
from collections import defaultdict
from copy import copy
import tarfile

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
    """ Fetches most of the information from the parent process and its 
    input artifacts"""

    process = Process(lims,id=processid)
    parent_processes = process.parent_processes()
    assert len(parent_processes) == 1
    parent_process = parent_processes[0]
    input_artifacts = process.all_inputs(unique=True)

    # Store each project as a key with the samples and artifacts as values
    projects = defaultdict(list)
    for i_a in input_artifacts:
        # Input artifacts are pools, sometimes containing multiple samples.
        for sample in i_a.samples:
            projects[sample.project].append((sample,i_a))

    # Create a separate file for each project present in the artifacts
    files=[]
    for project in projects.keys():
        tmp_info = copy.deepcopy(default_info)

        print 'Collecting application udf from project with id {0}'.format(p.id)
        fn = p.id+'.yml'
        tmp = file(fn,'wb')

        # fetch the multiplexing information, the main sources of information 
        # should be:
        # parent_process.udf.items() and
        # project.udf.items()

        # *Should have error handling here to catch projects without application stated*
        a = p.udf['Application']
        tmp_info['details'][1]['analysis'] = a
        yaml.dump(default_info,tmp,default_flow_style=False)
        tmp.close()
        files.append(fn)
        
    # Save all files into a tarball
    outtar = tarfile.open(outfile,'w:gz')
    for fn in files:
        # Put file in tar archive and delete the temporary one
        tarinfo = tarfile.TarInfo(fn)
        outtar.add(fn)
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
