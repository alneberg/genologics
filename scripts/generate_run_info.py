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

manual_info={'details': [{'algorithm': {'aligner': None
}
}
]
}

def main(lims,processid,outfile):
    """ Fetches most of the information from the parent process and its 
    input artifacts"""

    # The current demultiplexing process
    process = Process(lims,id=processid)
    # All unique input artifacts
    input_ids = map(lambda io: io[0]['limsid'],process.input_output_maps)
    uniq_input_ids = list(frozenset(input_ids))
    projects = defaultdict(list)

    for id in uniq_input_ids:
        i_a = Artifact(lims,id=id)
        for sample in i_a.samples:
            projects[sample.project].append(sample)
            # fetch the multiplexing information
            cluster_processes = lims.get_processes(
                type="Cluster Generation (Illumina SBS) 4.0",
                projectname=sample.project.name)
            # Fetching multiplex details
            cluster_input_ids = map(lambda io: io[0]['limsid'],process.input_output_maps)
            uniq_cluster_input_ids = list(frozenset(cluster_input_ids))
            for cluster_id in uniq_cluster_input_ids:
                print cluster_id

        # Collecting information for each pool
        
    outtar = tarfile.open(outfile,'w:gz')
    print projects.keys()
    for i,p in enumerate(projects):
        print 'Collecting application udf from project with id {0}'.format(p.id)
        a = p.udf['Application']
        # Should have error handling here to catch projects without application stated
        
        fn = p.id+'.yml'
        print 'Creating a yaml file named: {0}'.format(fn)
        tmp = file(fn,'wb')

        tmp_info = copy.deepcopy(default_info)
        tmp_info['details'][1]['analysis'] = a
        yaml.dump(default_info,tmp,default_flow_style=False)

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
