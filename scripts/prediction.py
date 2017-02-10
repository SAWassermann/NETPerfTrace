import argparse
import os
import math
import sklearn.ensemble as sk_ensemble

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
    parser.add_argument('-t', action="store", dest="timeslotDuration", help="Duration in hours of a timeslot; "
                                                                            "i.e. the duration of the time windows in which "
                                                                            "the observation period will be subdivided.",
                                                                            type=int,
                                                                            required=True)

    arguments = vars(parser.parse_args())
    if arguments['observationTime'] <= 0 or arguments['timeslotDuration'] <= 0:
        print 'error: the observation time and the duration of the timeslots must be strictly higher than 0!'
        exit(1)
    # parameter handling -- end

    # training phase -- begin
    print 'Start training phase...'
    resLifeInputFeatures = list()
    routeChangesInputFeatures = list()
    avgRTTInputFeatures = list()

    resLifeRealValues = list()
    routeChangesRealValues = list()
    avgRTTRealValues = list()

    INIT_PATH_OBSERVATION = '../input/observationPaths/'
    observationPathsList = os.listdir(INIT_PATH_OBSERVATION)

    for observationPath in observationPathsList:
        if observationPath == '.gitignore':
            continue
        f = fe.getFeatures(INIT_PATH_OBSERVATION, observationPath, arguments['observationTime'], arguments['timeslotDuration'], True)

        # store features extracted from this observation path
        resLifeInputFeatures += f[0]
        routeChangesInputFeatures += f[1]
        avgRTTInputFeatures += f[2]

        resLifeRealValues += f[3]
        routeChangesRealValues += f[4]
        avgRTTRealValues += f[5]

    N_ESTIMATORS = 10
    N_JOBS = 4
    # regressor for reslife prediction
    regressorResLife = sk_ensemble.RandomForestRegressor(n_estimators=N_ESTIMATORS, n_jobs=N_JOBS)
    regressorResLife.fit(resLifeInputFeatures, resLifeRealValues)
    resLifeNBOutputs = regressorResLife.n_outputs_

    # regressor for # route changes in next timeslot prediction
    regressorRouteChanges = sk_ensemble.RandomForestRegressor(n_estimators=N_ESTIMATORS, n_jobs=N_JOBS)
    regressorRouteChanges.fit(routeChangesInputFeatures, routeChangesRealValues)
    routeChangesNBOutputs = regressorRouteChanges.n_outputs_

    # regressor for reslife prediction
    regressorAvgRTT = sk_ensemble.RandomForestRegressor(n_estimators=N_ESTIMATORS, n_jobs=N_JOBS)
    regressorAvgRTT.fit(avgRTTInputFeatures, avgRTTRealValues)
    avgRTTNBOutputs = regressorAvgRTT.n_outputs_
    # training phase -- end

    # forecasting phase -- begin
    print 'Start prediction phase...'
    resLifeInputFeatures = list()
    routeChangesInputFeatures = list()
    avgRTTInputFeatures = list()

    INIT_PATH_PREDICTION = '../input/predictionPaths/'
    predictionPathsList = os.listdir(INIT_PATH_PREDICTION)

    for predictionPath in predictionPathsList:
        if predictionPath == '.gitignore' or predictionPath == 'dummy':
            continue
        f = fe.getFeatures(INIT_PATH_PREDICTION, predictionPath, arguments['observationTime'],
                           arguments['timeslotDuration'], False)

        # store features extracted from this prediction path
        resLifeInputFeatures = f[0]
        routeChangesInputFeatures = f[1]
        avgRTTInputFeatures = f[2]

        srcIP = f[3]
        dstIP = f[4]

        # predict prediction targets
        if resLifeNBOutputs > 1:
            predResLife = math.fabs(regressorResLife.predict(resLifeInputFeatures)[0][0])
        else:
            predResLife = math.fabs(regressorResLife.predict(resLifeInputFeatures))

        if routeChangesNBOutputs > 1:
            predRouteChanges = regressorRouteChanges.predict(routeChangesInputFeatures)[0][0]
        else:
            predRouteChanges = regressorRouteChanges.predict(routeChangesInputFeatures)
        if predRouteChanges < 0:
            predRouteChanges = 0
        else:
            predRouteChanges = round(predRouteChanges)

        if avgRTTNBOutputs > 0:
            predAvgRTT = regressorAvgRTT.predict(avgRTTInputFeatures)[0][0]
        else:
            predAvgRTT = regressorAvgRTT.predict(avgRTTInputFeatures)

        # save estimations
        with open('../output/prediction_' + srcIP + '_' + dstIP + '.txt', 'w') as out:
            out.write('RESIDUAL_LIFE_TIME:\t' + str(predResLife) + '\n')
            out.write('NUMBER_ROUTE_CHANGES_NEXT_' + str(arguments['timeslotDuration']) + 'H_TIMESLOT:\t'
                      + str(predRouteChanges) + '\n')
            out.write('AVG_RTT_NEXT_TRACERT_SAMPLE:\t' + str(predAvgRTT) + '\n')


    # forecasting phase -- end