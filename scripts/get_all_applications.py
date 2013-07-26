#!/usr/bin/env python
"""Fetch and pring all unique applications"""
from genologics.lims import Lims
from genologics.config import BASEURI,USERNAME,PASSWORD
from collections import Counter

def main(lims,d):
    all_projects = lims.get_projects()
    applications = []
    projects_without_application =[]
    for project in all_projects:
        try:
            applications.append(project.udf['Application'])
        except:
            projects_without_application.append(project)
    a_c = Counter(applications)
    print len(all_projects)
    print len(projects_without_application)
    print a_c
    unique_applications = list(frozenset(applications))
    for application in unique_applications:
        if application not in d:
            print application
        else:
            print 'Approved'
    

if __name__ =="__main__":
    lims = Lims(BASEURI,USERNAME,PASSWORD)
    lims.check_version()

    application_default=['Amplicon','ChIP-seq','Custom capture','de novo',
                         'Exome capture','Finished library','Mate-pair',
                         'Metagenome','miRNA-seq','RNA-seq (mRNA)', 
                         'RNA-seq (Ribominus)','RNA-seq (total RNA)',
                         'RNA-seq (RiboZero)', 'cDNA','Special','WG re-seq',
                         'QA']
    main(lims,application_default)
