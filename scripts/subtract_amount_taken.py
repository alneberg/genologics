#!/usr/bin/env python
DESC = """EPP script to subtract the value of "Amount taken (ng)" udf from "Amount (ng)"
 udf in Clarity LIMS. Can be executed in the background, without user pressing a "blue button".

What happens if the process step is aborted? Is the amount taken put back into the amount?
What safety checks should we have for the amount taken value... Less than what's in the amount udf?

Written by Johannes Alneberg, Science for Life Laboratory, Stockholm, Sweden
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

def check_udf_is_defined(artifacts,udf):
    """ Exit if udf is not defined for any of inputs. """
    filtered_artifacts = []
    incorrect_artifacts = []
    for artifact in artifacts:
        if (udf in artifact.udf):
            filtered_artifacts.append(artifact)
        else:
            logging.warning(("Found artifact for sample {0} with {1} "
                             "undefined/blank.").format(input.samples[0].name,udf))
            incorrect_artifacts.append(artifact)
    return filtered_artifacts, incorrect_artifacts

def main(lims,args,epp_logger):
    p = Process(lims,id = args.pid)
    amount_udf = 'Amount (ng)'
    taken_udf = 'Amount taken (ng)'

    if args.aggregate:
        artifacts = p.all_inputs(unique=True)
    else:
        all_artifacts = p.all_outputs(unique=True)
        artifacts = filter(lambda a: a.output_type == "Analyte", all_artifacts)

    correct_amount_a, incorrect_amount_a = check_udf_is_defined(artifacts, amount_udf)
    correct_artifacts, incorrect_taken_a = check_udf_is_defined(correct_amount_a, taken_udf)

    # Merge lists of mutually exclusive incorrect artifcats
    incorrect_artifacts = incorrect_amount_a + incorrect_taken_a

    apply_calculations(lims,correct_artifacts, amount_udf, taken_udf, epp_logger)

    abstract = ("Updated {0} artifact(s), skipped {1} artifact(s) with incorrect udf info.").format(len(correct_artifacts),
                                             len(incorrect_artifacts))
    print >> sys.stderr, abstract # stderr will be logged and printed in GUI


if __name__ == "__main__":
    # Initialize parser with standard arguments and description

    parser = ArgumentParser(description=DESC)
    parser.add_argument('--pid',
                        help='Lims id for current Process')
    parser.add_argument('--log',default=sys.stdout,
                        help='Log file')
    parser.add_argument('--aggregate', action='store_true',
                        help=('This flag is needed if the current process '
                              'is an aggregate QC step'))
    args = parser.parse_args()

    lims = Lims(BASEURI,USERNAME,PASSWORD)
    lims.check_version()

    with EppLogger(args.log,lims=lims, prepend=True) as epp_logger:
        main(lims, args, epp_logger)
