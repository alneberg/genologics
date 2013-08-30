#!/usr/bin/env python
"""Fetch and pring all unique applications"""
from genologics.lims import Lims
from genologics.config import BASEURI,USERNAME,PASSWORD
from collections import Counter
from argparse import ArgumentParser

def main(lims,d,open_date=None):
    all_projects = lims.get_projects(open_date=open_date)
    applications = []
    best_practice = []
    bioinfo_qc = []
    projects_without_application =[]
    no_best = []
    no_qc = []
    for project in all_projects:
        try:
            applications.append(project.udf['Application'])
        except:
            projects_without_application.append(project)
        try:
            best_practice.append(project.udf['Best practice bioinformatics'])
        except:
            no_best.append(project)
        try:
            bioinfo_qc.append(project.udf['Bioinformatic QC'])
        except:
            no_qc.append(project)
    best_c = Counter(best_practice)
    bioinfo_c = Counter(bioinfo_qc)
    print "Best practice: {0}".format(best_c)
    print "Bioinformatics QC: {0}".format(bioinfo_c)
    a_c = Counter(applications)
    print "Projects in total: {0}".format(len(all_projects))
    print "Projects without application: {0}".format(len(projects_without_application))
    print a_c
    unique_applications = list(frozenset(applications))
    approved_counter = 0
    for application in unique_applications:
        if application not in d:
            print application
        else:
            approved_counter += 1
    print "Approved applications: {0}".format(approved_counter)

    

if __name__ =="__main__":

    parser = ArgumentParser()
    parser.add_argument('--open_date',
                        help='Only use projects opened after this date')
    args = parser.parse_args()


    lims = Lims(BASEURI,USERNAME,PASSWORD)
    lims.check_version()

    application_default=['Amplicon','ChIP-seq','Custom capture','de novo',
                         'Exome capture','Finished library','Mate-pair',
                         'Metagenome','miRNA-seq','RNA-seq (mRNA)', 
                         'RNA-seq (Ribominus)','RNA-seq (total RNA)',
                         'RNA-seq (RiboZero)', 'cDNA','Special','WG re-seq',
                         'QA']
    main(lims,application_default,open_date=args.open_date)
