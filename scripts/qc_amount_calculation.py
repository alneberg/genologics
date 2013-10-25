#!/usr/bin/env python
DESC="""EPP script to calculate amount in ng from concentration and volume 
udf:s in Clarity LIMS. The script checks that the 'Volume (ul)' and 
'Concentration' udf:s are defined for all artifacts that are to be updated,
 otherwise the script exits with an error message. The udf. 'Conc. Units' 
has to have the value: 'ng/ul', otherwise that artifact is skipped by the 
script.

Johannes Alneberg, Science for Life Laboratory, Stockholm, Sweden
""" 
from argparse import ArgumentParser

from genologics.lims import Lims
from genologics.config import BASEURI,USERNAME,PASSWORD

from genologics.entities import Process
from genologics.epp import EppLogger

import logging
import sys

def apply_calculations(lims,artifacts,udf1,op,udf2,result_udf,epp_logger):
    logging.info(("result_udf: {0}, udf1: {1}, "
           "operator: {2}, udf2: {3}").format(result_udf,udf1,op,udf2))
    for artifact in artifacts:
        try:
            artifact.udf[result_udf]
        except KeyError:
            artifact.udf[result_udf]=0

        logging.info(("Updating: Artifact id: {0}, "
                     "result_udf: {1}, udf1: {2}, "
                     "operator: {3}, udf2: {4}").format(artifact.id, 
                                                        artifact.udf[result_udf],
                                                        artifact.udf[udf1],op,
                                                        artifact.udf[udf2]))
        artifact.udf[result_udf] = eval(
            '{0}{1}{2}'.format(artifact.udf[udf1],op,artifact.udf[udf2]))
        artifact.put()
        logging.info('Updated {0} to {1}.'.format(result_udf,
                                                 artifact.udf[result_udf]))
def check_udf_is_defined(inputs,udf):
    """ Exit if udf is not defined for any of inputs. """
    for input in inputs:
        if not (udf in input.udf):
            msg = ("Found artifact for sample {0} with {1} "
                   "undefined/blank, exiting").format(input.samples[0].name,udf)
            print >> sys.stderr, msg
            sys.exit(-1)

def check_udf(artifacts,udf,value):
    """ Filter artifacts on undefined udf or if udf has wrong value. """
    filtered_artifacts = []
    incorrect_artifacts = []
    for artifact in artifacts:
        if udf in artifact.udf and (artifact.udf[udf] == value):
            filtered_artifacts.append(artifact)
        elif udf in artifact.udf:
            incorrect_artifacts.append(artifact)
            logging.info(("Filtered out artifact for sample: {0}"
                          ", due to wrong {1}").format(artifact.samples[0].name,udf))
        else:
            incorrect_artifacts.append(artifact)
            logging.info(("Filtered out artifact for sample: {0}"
                          ", due to undefined/blank {1}").format(artifact.samples[0].name,udf))

    return filtered_artifacts,incorrect_artifacts

def main(lims,args,epp_logger):
    p = Process(lims,id = args.pid)
    udf_check = 'Conc. Units'
    value_check = 'ng/ul'
    if args.aggregate:
        artifacts = p.all_inputs(unique=True)
    else:
        all_artifacts = p.all_outputs(unique=True)
        artifacts = filter(lambda a: a.output_type == "ResultFile" ,all_artifacts)

    check_udf_is_defined(artifacts, 'Concentration')
    check_udf_is_defined(artifacts, 'Volume (ul)')

    correct_artifacts, incorrect_artifacts = check_udf(artifacts,udf_check,value_check)

    apply_calculations(lims,correct_artifacts,'Concentration','*',
                       'Volume (ul)','Amount (ng)',epp_logger)

    abstract = ("Updated {0} artifact(s), skipped {1} artifact(s) with "
                "wrong or blank 'Conc. Unit'.").format(len(correct_artifacts),
                                                       len(incorrect_artifacts))
    print >> sys.stderr, abstract # stderr will be logged and printed in GUI


if __name__ == "__main__":
    # Initialize parser with standard arguments and description
    parser = ArgumentParser(description=DESC)
    parser.add_argument('--pid',
                        help='Lims id for current Process')
    parser.add_argument('--log',default=sys.stdout,
                        help='Log file for runtime info and errors.')
    parser.add_argument('--no_prepend',action='store_true',
                        help="Do not prepend old log file")
    parser.add_argument('--aggregate', action='store_true',
                        help=('Use this tag if current Process is an '
                              'aggregate QC step'))
    args = parser.parse_args()

    lims = Lims(BASEURI,USERNAME,PASSWORD)
    lims.check_version()
    prepend = not args.no_prepend
    with EppLogger(args.log,lims=lims,prepend=prepend) as epp_logger:
        main(lims, args,epp_logger)
