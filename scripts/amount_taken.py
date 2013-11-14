#!/usr/bin/env python
DESC = """EPP script to add the value of "Amount taken (ng)" udf on analyte level
 to "Amount taken (ng)" udf on sample level in Clarity LIMS. Can be executed in 
the background, without user pressing a "blue button". Strictly checks that 
"Amount taken (ng)" udf is defined for all artifacts and all samples, and
that the value for the artifact is entered correct before updating anything.

Written by Johannes Alneberg, Science for Life Laboratory, Stockholm, Sweden
""" 

from argparse import ArgumentParser

from genologics.lims import Lims
from genologics.config import BASEURI, USERNAME, PASSWORD

from genologics.entities import Process
from genologics.epp import EppLogger

import logging
import sys

def apply_calculations(lims, artifacts, artifact_udf, sample_udf, epp_logger):
    for artifact in artifacts:
        for sample in artifact.samples:
            if not sample_udf in sample.udf:
                sample.udf[sample_udf] = 0

            logging.info(("Updating: sample id: {0}, "
                          "Adding {1} to {2}").format(sample.id, 
                                                      artifact.udf[artifact_udf],
                                                      sample.udf[sample_udf]))

            sample.udf[sample_udf] += artifact.udf[artifact_udf]
            sample.put()
            logging.info('Updated {0} to {1}.'.format(sample_udf,
                                                      sample.udf[sample_udf]))

def check_udf_is_defined(artifacts, udf):
    """ Filter and Warn if udf is not defined for any of artifacts. """
    filtered_artifacts = []
    incorrect_artifacts = []
    for artifact in artifacts:
        if (udf in artifact.udf):
            filtered_artifacts.append(artifact)
        else:
            logging.warning(("Found artifact for sample {0} with {1} "
                             "undefined/blank, skipping").format(artifact.samples[0].name, udf))
            incorrect_artifacts.append(artifact)
    return filtered_artifacts, incorrect_artifacts

def check_below_threshold(artifacts, value_udf, threshold):
    """ Filter and warn if value_udf is above threshold for any of artifacts. """
    filtered_artifacts = []
    incorrect_artifacts = []
    for artifact in artifacts:
        if artifact.udf[value_udf] <= threshold:
            filtered_artifacts.append(artifact)
        else:
            logging.warning(("Found artifact for sample {0} where {1} "
                             "is above threshold").format(artifact.samples[0].name, value_udf))
            incorrect_artifacts.append(artifact)
    return filtered_artifacts, incorrect_artifacts
    

def main(lims, args, epp_logger):
    p = Process(lims, id = args.pid)
    artifact_udf = 'Amount taken (ng)'
    sample_udf = 'Total amount taken (ng)'
    threshold = args.threshold

    if args.aggregate:
        artifacts = p.all_inputs(unique=True)
    else:
        all_artifacts = p.all_outputs(unique=True)
        artifacts = filter(lambda a: a.output_type == "Analyte", all_artifacts)

    correct_artifacts, undefined_amount_a = check_udf_is_defined(artifacts, artifact_udf)
    
    # strict checking of udf values
    if len(undefined_amount_a):
        # stderr will be logged and printed in GUI
        print >> sys.stderr, "Exiting due to {0} artifacts with blank {1}".format(len(undefined_amount_a), 
                                                                                  artifact_udf)
        sys.exit(-1)

    if threshold:
        correct_artifacts, above_threshold = check_below_threshold(artifacts, artifact_udf, threshold)
        if len(above_threshold):
            print >> sys.stderr, ("Exiting due to {0} artifacts where {1}"
                                  "is above threshold {2}").format(len(above_threshold),
                                                                   artifact_udf,
                                                                   threshold)
            sys.exit(-1)

    apply_calculations(lims, correct_artifacts, artifact_udf, sample_udf, epp_logger)

    abstract = ("Updated all samples' {0}.").format(sample_udf)
    print >> sys.stderr, abstract # stderr will be logged and printed in GUI


if __name__ == "__main__":
    # Initialize parser with standard arguments and description

    parser = ArgumentParser(description=DESC)
    parser.add_argument('--pid',
                        help='Lims id for current Process')
    parser.add_argument('--log', default=sys.stdout,
                        help='Log file for runtime info and errors.')
    parser.add_argument('--threshold', type=int, default=None,
                        help=("Upper threshold for the amount taken (ng) value "
                              "that is accepted. If any artifact has a HIGHER "
                              "value, the script will not update any samples."))
    parser.add_argument('--aggregate', action='store_true',
                        help=("Use this tag if your process is aggregating "
                              "results. The default behaviour assumes it is "
                              "the output artifact of type analyte that is "
                              "modified while this tag changes this to using "
                              "input artifacts instead."))
    args = parser.parse_args()

    lims = Lims(BASEURI, USERNAME, PASSWORD)
    lims.check_version()

    with EppLogger(args.log, lims=lims, prepend=True) as epp_logger:
        main(lims, args, epp_logger)
