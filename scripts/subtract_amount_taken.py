#!/usr/bin/env python
"""EPP script to subtract amount taken from amount in Clarity LIMS
Command to trigger this script:
bash -c "PATH/TO/INSTALLED/SCRIPT
--pid {processLuid} 
--log {compoundOutputFileLuidN}"
"

Johannes Alneberg, Science for Life Laboratory, Stockholm, Sweden
""" 
from argparse import ArgumentParser

from genologics.lims import Lims
from genologics.config import BASEURI,USERNAME,PASSWORD

from genologics.entities import Process
from genologics.epp import EppLogger

import logging
import sys

def apply_calculations(lims,artifacts,amount_udf,taken_udf,epp_logger):
    for artifact in artifacts:
        logging.info(("Updating: Artifact id: {0}, "
                     "Amount: {1}, Amount taken (ng): {2}, ").format(artifact.id, 
                                                        artifact.udf[amount_udf],
                                                        artifact.udf[taken_udf]))
        artifact.udf[amount_udf] += - artifact.udf[taken_udf]
        artifact.put()
        logging.info('Updated {0} to {1}.'.format(amount_udf,
                                                 artifact.udf[amount_udf]))
def check_udf_is_defined(inputs,udf):
    """ Exit if udf is not defined for any of inputs. """
    filtered_inputs = []
    incorrect_inputs = []
    for input in inputs:
        if not (udf in input.udf):
            msg = ("Found artifact for sample {0} with {1} "
                   "undefined/blank, exiting").format(input.samples[0].name,udf)
            print >> sys.stderr, msg
            sys.exit(-1)

            def main(lims,args,epp_logger):
    p = Process(lims,id = args.pid)
    udf_check = 'Conc. Units'
    value_check = 'ng/ul'
    concentration_udf = 'Concentration'
    size_udf = 'Size (bp)'
    if args.aggregate:
        artifacts = p.all_inputs(unique=True)
    else:
        all_artifacts = p.all_outputs(unique=True)
        artifacts = filter(lambda a: a.output_type == "File" ,all_artifacts)

    check_udf_is_defined(artifacts,concentration_udf)
    check_udf_is_defined(artifacts,size_udf)
    correct_artifacts, incorrect_artifacts = check_udf(artifacts,udf_check,value_check)
    apply_calculations(lims,correct_artifacts,concentration_udf,size_udf,udf_check,epp_logger)

    abstract = ("Updated {0} artifact(s), skipped {1} artifact(s) with "
                "wrong 'Conc. Unit'.").format(len(correct_artifacts),
                                             len(incorrect_artifacts))
    print >> sys.stderr, abstract # stderr will be logged and printed in GUI


if __name__ == "__main__":
    # Initialize parser with standard arguments and description
    desc = """EPP script to calculate molar concentration from concentration the
 udf in Clarity LIMS. """

    parser = ArgumentParser(description=desc)
    parser.add_argument('--pid',
                        help='Lims id for current Process')
    parser.add_argument('--log',default=sys.stdout,
                        help='Log file')
    parser.add_argument('--no_prepend',action='store_true',
                        help="Do not prepend old log file")
    parser.add_argument('--aggregate', action='store_true',
                        help='Current Process is an aggregate QC step')
    args = parser.parse_args()

    lims = Lims(BASEURI,USERNAME,PASSWORD)
    lims.check_version()
    prepend = not args.no_prepend
    with EppLogger(args.log,lims=lims,prepend=prepend) as epp_logger:
        main(lims, args,epp_logger)
