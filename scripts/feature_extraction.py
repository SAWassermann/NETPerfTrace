import datetime, time, bisect, math, numpy as np


"""
Class representing a traceroute hop.
"""
class TracerouteHop:
    """
    Initiate a ``Hop`` instance
    """
    def __init__(self):
        self.IP = None

        self.minRTT = -1
        self.avgRTT = -1
        self.maxRTT = -1
        self.mdevRTT = -1


    """
    Tow ``Hop`` instances are considered as being equal if their IP addresses are the same.
    """
    def __eq__(self, other):
        return self.IP == other.IP


    """
    Tow ``Hop`` instances are considered as being unequal if their IP addresses are different.
    """
    def __ne__(self, other):
        return self.IP != other.IP


"""
Class representing a complete traceroute.
"""
class Traceroute:
    """
    Initiate a ``Traceroute`` instance
    """
    def __init__(self):
        self.hops = list()

        self.routeAge = 0
        self.resLifetime = -1

        self.timestamp = None
        self.timeslotIndex = 0

        self.lastHop = TracerouteHop()      # last hop of traceroute
        self.nextLastHop = TracerouteHop()  # last hop of the next traceroute sample

        self.currentNbChangesInSlot = None
        self.nbRouteChangesInSlot = -1
        self.nbRouteChangesInNextSlot = -1

        self.srcIP = None
        self.dstIP = None


    """
    Two ``Traceroute`` instances are considered as being equal if their lists of hops are the identical.
    """
    def __eq__(self, other):
        return self.hops == other.hops


    """
    Two ``Traceroute`` instances are considered as being unequal if their lists of hops are different.
    """
    def __ne__(self, other):
        return self.hops != other.hops


"""
Class representing statistics about the observed route durations.
The statistics that are stored are: average, minimum, maximum, 5% -, 10% -, 25% -, 50% -, 75% -, 90% -, and 95% - percentile.
"""
class RouteDurationStatistics:
    """
    Initiate an instance of ``RouteDurationStatistics``.
    """
    def __init__(self, avg, min, max, percentiles):
        self.routeDurationAverage = avg
        self.routeDurationMinimum = min
        self.routeDurationMaximum = max
        self.routeDurationPercentiles = percentiles


    """
    String representation of an instancr of ``RouteDurationStatistics``.
    Its format is: average <tab> minimum <tab> maximum <tab> percentiles (tab separated)
    """
    def __str__(self):
        return str(self.routeDurationAverage) + '\t' + \
                str(self.routeDurationMinimum) + '\t' + \
                str(self.routeDurationMaximum) + '\t' + \
                '\t'.join(map(str, self.routeDurationPercentiles))


"""
Class representing statistics about the observed number of route changes.
The statistics that are stored are: total number of changes for the monitored path, average number of changes in timeslots,
minimum in timeslots, maximum in timeslots, 5% -, 10% -, 25% -, 50% -, 75% -, 90% -, and 95% - percentile.
"""
class NumberOfRouteChangesStatistics:
    """
    Initiate an instance of ``NumberOfRouteChangesStatistics``.
    """
    def __init__(self, avg, min, max, percentiles):
        self.numberOfRouteChangesInTimeslotsAverage = avg
        self.numberOfRouteChangesInTimeslotsMinimum = min
        self.numberOfRouteChangesInTimeslotsMaximum = max
        self.numberOfRouteChangesInTimeslotsPercentiles = percentiles
        self.totalNumberOfRouteChanges = None


    """
    String representation of an instance of ``NumberOfRouteChangesStatistics``.
    Its format is: total number of route changes <tab> average in timeslots <tab> minimum <tab> maximum <tab> percentiles
    (tab separated)
    """
    def __str__(self):
        return str(self.totalNumberOfRouteChanges) + '\t' + \
                str(self.numberOfRouteChangesInTimeslotsAverage) + '\t' + \
                str(self.numberOfRouteChangesInTimeslotsMinimum) + '\t' + \
                str(self.numberOfRouteChangesInTimeslotsMaximum) + '\t' + \
                '\t'.join(map(str, self.numberOfRouteChangesInTimeslotsPercentiles))


"""
Class representing statistics about the observed average round-trip times (RTT).
The statistics that are stored are: average, minimum, maximum, 5% -, 10% -, 25% -, 50% -, 75% -, 90% -, and 95% - percentile.
"""
class AvgRTTStatistics:
    """
    Initiate an instance of AvgRTTStatistics.
    """
    def __init__(self, avg, min, max, percentiles):
        self.avgRTTAverage = avg
        self.avgRTTMinimum = min
        self.avgRTTMaximum = max
        self.avgRTTPercentiles = percentiles


    """
    String representation of an instance of ``AvgRTTStatistics``.
    Its format is: average <tab> minimum <tab> maximum <tab> percentiles (tab separated)
    """
    def __str__(self):
        return str(self.avgRTTAverage) + '\t' + \
                str(self.avgRTTMinimum) + '\t' + \
                str(self.avgRTTMaximum) + '\t' + \
                '\t'.join(map(str, self.avgRTTPercentiles))


"""
Get the unixtimestamp from the string <dateString> in the format YYYYMMDDThh:mm:ss
YYYY = year
MM   = month
DD   = day
hh   = hour
mm   = minute
ss   = second
"""
def __getUnixTimestamp(dateString):
    tracerouteTime = datetime.datetime.strptime(dateString, '%Y%m%dT%H:%M:%S')
    return time.mktime(tracerouteTime.timetuple())


"""
Get the index of the timeslot in <timeslotsLowerBounds> to which the route observed at time <timestamp> belongs to. A
timeslot in the array <timeslotsLowerBounds> is represented with its lower bound.  For instance, the entry for the
timeslot (0, 12) in the array is simply 0.
"""
def __getTimeslotIndex(timeslotsLowerBounds, timestamp):
    return bisect.bisect_right(timeslotsLowerBounds, timestamp) - 1


"""
Get the timeslots by which you want to separate your observation (learning) time (in hours). <timestamp> indicates the time (in
the unix-timestamp format) at which the observation time starts, <timeslotDuration> the duration (in hours) of one
timeslot, and <observationDuration> represents the duration of the observation time.
The timeslots are returned in the form of an array; each timeslot is represented by a tuple (<lb>, <ub>). <lb> is the lower
bound of this timeslot and <ub> is the upper bound.
"""
def __getTimeslots(timestamp, timeslotDuration, observationDuration):
    numberOfTimeslotsBoundaries = int(math.ceil(observationDuration / timeslotDuration) + 1)
    timeslotBoundaries = [timestamp + i * 60 * 60 * timeslotDuration for i in range(0, numberOfTimeslotsBoundaries)]
    timeslots = [tuple([timeslotBoundaries[i], timeslotBoundaries[i + 1]]) for i in
                 range(0, numberOfTimeslotsBoundaries - 1)]
    return timeslots


"""
Get statistics from the numpy array <numpyVec> containing either integers or floats. The statistics that are extracted are:
average, minimum, maximum, 5% -, 10% -, 25% -, 50% -, 75% -, 90% -, and 95% - percentile.
The collected stats are returned either as a RouteDurationStatistics-, a NumberOfRouteChangesStatistics-, or as
MininumRTTStatistics-object.
if metric == 'res' -> RouteDurationStatistics
elif metric == 'rc' -> NumberOfRouteChangesStatistics
elif metric == 'rtt' -> AverageRTTStatistics
else None.
If <numpyVec> is empty, return an instance for which the fields are filled with 0's.
"""
def __getStatistics(numpyVec, metric):
    NUMBER_OF_PERCENTILES = 7
    if len(numpyVec):
        # average
        average = np.mean(numpyVec)

        # min
        minimum = min(numpyVec)

        # max
        maximum = max(numpyVec)

        # 5% -, 10% -, 25% -, 50% -, 75% -, 90% -, and 95% - percentile
        percentiles = np.percentile(numpyVec, [5, 10, 25, 50, 75, 90, 95])

        if metric == 'res':
            return RouteDurationStatistics(average, minimum, maximum, percentiles)
        elif metric == 'rc':
            return NumberOfRouteChangesStatistics(average, minimum, maximum, percentiles)
        elif metric == 'rtt':
            return AvgRTTStatistics(average, minimum, maximum, percentiles)
    else:
        if metric == 'res':
            return RouteDurationStatistics(0, 0, 0, [0 for i in range(0, NUMBER_OF_PERCENTILES)])
        elif metric == 'rc':
            return NumberOfRouteChangesStatistics(0, 0, 0, [0 for i in range(0, NUMBER_OF_PERCENTILES)])
        elif metric == 'rtt':
            return AvgRTTStatistics(0, 0, 0, [0 for i in range(0, NUMBER_OF_PERCENTILES)])
        else:
            return None


"""
Get all the features for the traceroute sample ``traceroute`` required for predicting the residual lifetime of a route in the
form of a string.
The format of the string is str(``routeDuration``) <tab> route age of the route <tab> residual lifetime of the route
str(``routeDuration``) refers to the string representation of a ``NumberOfRouteChangesStatistics`` instance.
"""
def __collectStringResidualLifetimeFeatures(traceroute, routeDuration):
    return str(routeDuration) + '\t' + str(traceroute.routeAge) + '\t' + str(traceroute.resLifetime)


# TODO
def __collectResidualLifetimeFeatures(traceroute, routeDuration):
    return [routeDuration.routeDurationAverage, routeDuration.routeDurationMinimum, routeDuration.routeDurationMaximum] +\
           list(routeDuration.routeDurationPercentiles) + \
           [traceroute.routeAge, traceroute.resLifetime]


"""
Get all the features for the traceroute sample ``traceroute`` required for predicting the number of route changes in the next
timeslot in the form of a string.
The format of the string is str(``numberOfRouteChanges``) <tab> total number of route changes in this timeslot <tab>
1 if there are route changes in this slot, 0 otherwise <tab> number of currently observed route changes in ``traceroute``'s timeslot
<tab> number of route changes in the next timeslot
str(``numberOfRouteChanges``) refers to the string representation of a ``NumberOfRouteChangesStatistics`` instance.
"""
def __collectStringNumberRouteChangesFeatures(traceroute, numberOfRouteChanges):
    return str(numberOfRouteChanges) + '\t' + str(traceroute.nbRouteChangesInSlot) + '\t' \
            + ('1' if traceroute.nbRouteChangesInSlot > 0 else '0') + '\t' \
            + str(traceroute.currentNbChangesInSlot) + '\t' + str(traceroute.nbRouteChangesInNextSlot)


# TODO
def __collectNumberRouteChangesFeatures(traceroute, numberOfRouteChanges):
    return [numberOfRouteChanges.totalNumberOfRouteChanges, numberOfRouteChanges.numberOfRouteChangesInTimeslotsAverage,
            numberOfRouteChanges.numberOfRouteChangesInTimeslotsMinimum, numberOfRouteChanges.numberOfRouteChangesInTimeslotsMaximum] \
            + list(numberOfRouteChanges.numberOfRouteChangesInTimeslotsPercentiles) + \
           [traceroute.nbRouteChangesInSlot, 1 if traceroute.nbRouteChangesInSlot > 0 else 0,
            traceroute.currentNbChangesInSlot, traceroute.nbRouteChangesInNextSlot]


"""
Get all the features for the traceroute sample ``traceroute`` required for predicting the average RTT of the next traceroute
sample in the form of a string.
The format of the string is str(``avgRTT``) <tab> avg RTT of the last hop of ``traceroute`` <tab> avg RTT of the last hop of the
traceroute sample following ``traceroute``
str(``avgRTT``) refers to the string representation of a ``AvgRTTStatistics`` instance.
"""
def __collectStringAvgRTTFeatures(traceroute, avgRTT):
    return str(avgRTT) + '\t' + str(traceroute.lastHop.avgRTT) + '\t' + str(traceroute.nextLastHop.avgRTT)


# TODO
def __collectAvgRTTFeatures(traceroute, avgRTT):
    return [avgRTT.avgRTTAverage, avgRTT.avgRTTMinimum, avgRTT.avgRTTMaximum] + list(avgRTT.avgRTTPercentiles) +\
           [traceroute.lastHop.avgRTT, traceroute.nextLastHop.avgRTT]


# TODO
def __collectAllFeatures(traceroutes, routeDurationStats, numberRouteChangesStats, avgRTTStats, inTraining):
    resLifeInputFeatures = list()
    routeChangesInputFeatures = list()
    avgRTTInputFeatures = list()

    if inTraining:
        resLifeRealValues = list()
        routeChangesRealValues = list()
        avgRTTRealValues = list()

    invalidValues = [None, -1]

    for traceroute in traceroutes:
        # retrieve all the features of this traceroute and keep if valid
        resLifeFeatures = __collectResidualLifetimeFeatures(traceroute, routeDurationStats)
        if (inTraining and any(i in resLifeFeatures for i in invalidValues)) or \
            (not inTraining and any(i in resLifeFeatures[:-1] for i in invalidValues)):
            continue

        routeChangesFeatures = __collectNumberRouteChangesFeatures(traceroute, numberRouteChangesStats)
        if (inTraining and any(i in routeChangesFeatures for i in invalidValues)) or \
            (not inTraining and any(i in routeChangesFeatures[:-1] for i in invalidValues)):
            continue

        avgRTTfeatures = __collectAvgRTTFeatures(traceroute, avgRTTStats)
        if (inTraining and any(i in avgRTTfeatures for i in invalidValues)) or \
                (not inTraining and any(i in avgRTTfeatures[:-1] for i in invalidValues)):
            continue

        resLifeInputFeatures.append(resLifeFeatures[:-1])
        routeChangesInputFeatures.append(routeChangesFeatures[:-1])
        avgRTTInputFeatures.append(avgRTTfeatures[:-1])

        if inTraining:
            resLifeRealValues.append(resLifeFeatures[-1])
            routeChangesRealValues.append(routeChangesFeatures[-1])
            avgRTTRealValues.append(avgRTTInputFeatures[-1])

    if inTraining:
        return resLifeInputFeatures, routeChangesInputFeatures, avgRTTInputFeatures, resLifeRealValues, \
               routeChangesRealValues, avgRTTRealValues
    else:
        return resLifeInputFeatures, routeChangesInputFeatures, avgRTTInputFeatures


"""
<TO CHANGE>
Dump features required for the predictions for traceroutes in the array ``traceroutes`` into a log file. This file will
be located in the log folder and the naming scheme of it is: '<timestamp>_features_<srcIP>_<dstIP>.log', where <timestamp>
is the time at which this function has been executed, <srcIP> the source IP of the monitored path, and <dstIP> the
destination IP of it.
One line corresponds to the features for one traceroute sample.
The (tab separated) format of a line is: <resLifeFeatures> <tab> <routeChangesFeatures> <tab> <minRTTFeatures>.
These features are the results of the functions __collectStringResidualLifetimeFeatures(), __collectStringNumberRouteChangesFeatures(),
and __collectStringAvgRTTFeatures().
"""
def __saveFeaturesInFile(traceroutes, routeDurationStats, numberRouteChangesStats, avgRTTStats):
    if traceroutes:
        currentTime = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')
        srcIP = traceroutes[0].srcIP
        dstIP = traceroutes[0].dstIP

        invalidValues = [None, -1]

        fileName = '../logs/' + str(currentTime) + '_features_' + srcIP + '_' + dstIP + '.log'

        with open(fileName, 'w') as out:
            for traceroute in traceroutes:
                # retrieve all the features of this traceroute and check if valid
                resLifeFeatures = __collectResidualLifetimeFeatures(traceroute, routeDurationStats)
                if any(i in resLifeFeatures for i in invalidValues):
                    continue
                routeChangesFeatures = __collectNumberRouteChangesFeatures(traceroute, numberRouteChangesStats)
                if any(i in routeChangesFeatures for i in invalidValues):
                    continue
                avgRTTfeatures = __collectAvgRTTFeatures(traceroute, avgRTTStats)
                if any(i in avgRTTfeatures for i in invalidValues):
                    continue

                # save to log file
                resLifeFeaturesString = __collectStringResidualLifetimeFeatures(traceroute, routeDurationStats)
                routeChangesFeaturesString = __collectStringNumberRouteChangesFeatures(traceroute, numberRouteChangesStats)
                minRTTFeaturesString = __collectStringAvgRTTFeatures(traceroute, avgRTTStats)

                out.write(str(resLifeFeaturesString) + '\t' + str(routeChangesFeaturesString) + '\t' + str(minRTTFeaturesString + '\n'))

        print 'Features of traceroutes for source = ' + srcIP + ', destination = ' + dstIP + ' have been dumped into a log file.'
    else:
        print 'No traceroutes found...'


# TODO
def getFeatures(path, filename, observationDuration, timeslotDuration, inTraining):
    with open(path + filename, 'r') as inputFile:
        diffTraceroutes = list()  # observed traceroutes without sequential repetition; example: A A B A is stored as A B A)
        traceroutes     = list()  # all obsserved traceroutes

        timestampMeasurementsBegin = None  # timestamp indicating the time at which the first traceroute was observed

        currentTraceroute = Traceroute()

        # each index corresponds to a timeslotIndex which points to a list of traceroutes corresponding to that timeslot
        # same traceroute-storing principle as for <difftraceroutes>
        routesInSlots = list()

        print "Start parsing file '" + filename + "' and extracting features..."
        for line in inputFile:
            line = line.rstrip('\r\n')
            if line:
                data = line.split('\t')  # lines must be tab-separated

                # get source of traceroute
                if data[0] == 'SOURCE:':
                    currentTraceroute.srcIP = data[1]

                # get destination of traceroute
                elif data[0] == 'DESTINATION:':
                    currentTraceroute.dstIP = data[1]

                # get timestamp for time at which this traceroute was launched
                elif data[0] == 'TIMESTAMP:':
                    unixTimestamp = __getUnixTimestamp(data[1])

                    if not timestampMeasurementsBegin:   # first traceroute in file
                        timestampMeasurementsBegin = unixTimestamp
                        # prepare the different timeslots: each traceroute sample will be assigned to its corresponding
                        # timeslot so that we can compute the number of route changes in each slot later
                        timeslots = __getTimeslots(unixTimestamp, timeslotDuration, observationDuration)
                        timeslotsLowerBounds = [ts[0] for ts in timeslots]  # get lower bounds of different timeslots

                        # initiate the list for each timeslot (the lists will later contain the traceroutes associated to
                        # the different timeslots
                        for i in range(1, len(timeslots) + 1):
                            routesInSlots.append(list())

                    currentTraceroute.timestamp = unixTimestamp

                # get information about one traceroute hop
                elif data[0] == 'HOP:':
                    hop = TracerouteHop()
                    hop.IP = data[1]
                    hop.minRTT = float(data[2])
                    hop.avgRTT = float(data[3])
                    hop.maxRTT = float(data[4])
                    hop.mdevRTT = float(data[5])

                    currentTraceroute.hops.append(hop)

                    # if we obtained a responde (i.e. we have the corresponding IP and the minimum RTT), consider this
                    # hop as the last traceroute hop
                    if hop.minRTT != -1 and hop.IP != 'NA':
                        currentTraceroute.lastHop = hop

                # all information about one traceroute has been collected - wrap up with this one
                elif data[0] == 'END':
                    # add this traceroute to its corresponding timeslot
                    timeslotIndex = __getTimeslotIndex(timeslotsLowerBounds, currentTraceroute.timestamp)
                    currentTraceroute.timeslotIndex = timeslotIndex

                    # if applicable, add this traceroute to the list of different traceroutes
                    if len(diffTraceroutes) == 0 or currentTraceroute != diffTraceroutes[-1]:
                        diffTraceroutes.append(currentTraceroute)

                    # if applicable, add this traceroute to the list of traceroutes of its corresponding timeslot
                    if len(routesInSlots[currentTraceroute.timeslotIndex]) == 0 \
                            or currentTraceroute != routesInSlots[currentTraceroute.timeslotIndex][-1]:
                        routesInSlots[currentTraceroute.timeslotIndex].append(currentTraceroute)

                    # record for this traceroute the number of route changes so far observed in its timeslot
                    currentTraceroute.currentNbChangesInSlot = len(routesInSlots[currentTraceroute.timeslotIndex]) - 1 \
                                                            if len(routesInSlots[currentTraceroute.timeslotIndex]) - 1 else 0

                    # save this traceroute sample
                    traceroutes.append(currentTraceroute)

                    # prepare for next measurement/traceroute
                    currentTraceroute = Traceroute()

        lengthTraceroutes        = len(traceroutes)
        lengthDiffTraceroutes    = len(diffTraceroutes)

        # number of route changes in total we observed for this path
        nbRouteChanges = lengthDiffTraceroutes - 1 if lengthDiffTraceroutes > 0 else 0

        # compute the route duration of the different routes
        currentIndexDiffTraceroutes = 0  # value of index variable when running through <diffTraceroutes>
        routeDurations = list()

        for tracert in diffTraceroutes:
            if currentIndexDiffTraceroutes < lengthDiffTraceroutes - 1:
                routeDurations.append(float(diffTraceroutes[currentIndexDiffTraceroutes + 1].timestamp) - float(tracert.timestamp))
            currentIndexDiffTraceroutes += 1

        # compute route age and residual life for each sample + gather information about end-to-end delays
        currentIndexDiffTraceroutes = 0
        currentIndexTraceroutes     = 0  # value of index variable when running through <traceroutes>

        minRTTs  = list()
        avgRTTs  = list()
        maxRTTs  = list()
        mdevRTTs = list()

        for tracert in traceroutes:
            if currentIndexDiffTraceroutes < lengthDiffTraceroutes - 1:
                tracert.resLifetime = float(diffTraceroutes[currentIndexDiffTraceroutes + 1].timestamp) - float(tracert.timestamp)
            tracert.routeAge = float(tracert.timestamp) - float(diffTraceroutes[currentIndexDiffTraceroutes].timestamp)

            # does the next traceroute represent the same route as the current traceroute?
            if currentIndexTraceroutes < lengthTraceroutes - 1 and traceroutes[currentIndexTraceroutes] != traceroutes[currentIndexTraceroutes + 1]:
                currentIndexDiffTraceroutes += 1  # move on to the next traceroute in <diffTraceroutes>

            if tracert.lastHop.minRTT != -1:
                minRTTs.append(tracert.lastHop.minRTT)
                avgRTTs.append(tracert.lastHop.avgRTT)
                maxRTTs.append(tracert.lastHop.maxRTT)
                mdevRTTs.append(tracert.lastHop.mdevRTT)

            # save the hop of the next traceroute sample to the current traceroute will be used for feature computation later)
            if currentIndexTraceroutes < lengthTraceroutes - 1:
                tracert.nextLastHop = traceroutes[currentIndexTraceroutes + 1].lastHop
            else:
                tracert.nextLastHop = TracerouteHop()

            currentIndexTraceroutes += 1

        # compute stats about observed route durations
        routeDurations_np = np.array(routeDurations)  # create numpy array
        routeDurationStats = __getStatistics(routeDurations_np, 'res')

        # compute stats about route changes in timeslots
        nbRouteChangesInTimeslots = [len(routes) - 1 if len(routes) > 0 else 0 for routes in routesInSlots]
        nbRouteChangesInTimeslots_np = np.array(nbRouteChangesInTimeslots)
        nbRouteChangesStats = __getStatistics(nbRouteChangesInTimeslots_np, 'rc')

        # for the number of route changes, add also the total number of changes observed during the observation time
        nbRouteChangesStats.totalNumberOfRouteChanges = nbRouteChanges

        # compute stats about observed minimum RTTs
        # minRTTs_np = np.array(minRTTs)  # create numpy array
        # minRTTStats = __getStatistics(minRTTs_np, 'rtt')

        # compute stats about observed average RTTs
        avgRTTs_np = np.array(avgRTTs)  # create numpy array
        avgRTTStats = __getStatistics(avgRTTs_np, 'rtt')

        # for each traceroute, compute the number of route changes in its timeslot, and, if applicable, the number of
        # route changes in the next timeslot
        for traceroute in traceroutes:
            traceroute.nbRouteChangesInSlot = nbRouteChangesInTimeslots[traceroute.timeslotIndex]
            if traceroute.timeslotIndex < len(nbRouteChangesInTimeslots) - 1:
                traceroute.nbRouteChangesInNextSlot = nbRouteChangesInTimeslots[traceroute.timeslotIndex + 1]

        if inTraining:
            # save computed features for the traceroute samples in ``traceroutes`` to a file
            print 'Dumping features of observation paths to logfiles...'
            __saveFeaturesInFile(traceroutes, routeDurationStats, nbRouteChangesStats, avgRTTStats)
            return __collectAllFeatures(traceroutes, routeDurationStats, nbRouteChangesStats, avgRTTStats, True)
        else:
            # for the prediction, we only need the features of the traceroute we want to forecast, i.e. the last one
            # of the path
            return __collectAllFeatures([traceroutes[-1]], routeDurationStats, nbRouteChangesStats, avgRTTStats, False) \
                    + (traceroutes[-1].srcIP, traceroutes[-1].dstIP)