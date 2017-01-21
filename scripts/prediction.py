import argparse
import os
import feature_extraction as fe

if __name__ == '__main__':
    # parameter handling -- begin
    parser = argparse.ArgumentParser(description='Predict relevant dynamics and performance metrics of Internet paths')
    parser.add_argument('-v', action="version", version="version 1.0")
    parser.add_argument('-o', action="store", dest="observationTime", help="Duration in hours of the observation time; "
                                                                           "i.e. the time spanned by the samples used "
                                                                           "as observation (training) data.",
                                                                            type=int,
                                                                            required=True)
    parser.add_argument('-t', action="store", dest="timeslotDuration", help="The duration in hours of a timeslot; "
                                                                            "i.e. the duration of the time windows in which "
                                                                            "the observation period will be divided.",
                                                                            type=int,
                                                                            required=True)

    arguments = vars(parser.parse_args())
    if arguments['observationTime'] <= 0 or arguments['timeslotDuration'] <= 0:
        print 'error: the observation time and the duration of the timeslots must be strictly higher than 0!'
        exit(1)
    # parameter handling -- end

    INITPATH = '../input/observationPaths/'
    observationPathsList = os.listdir(INITPATH)

    for observationPath in observationPathsList:
        if observationPath == '.gitignore':
            continue
        fe.getFeatures(INITPATH, observationPath, arguments['observationTime'], arguments['timeslotDuration'])
