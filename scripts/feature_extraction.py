import datetime, time, bisect, math, numpy as np


"""
Class representing a traceroute hop.
"""
class TracerouteHop:
    """
    Initiate a Hop instance
    """
    def __init__(self):
        self.IP = ''

        self.minRTT = '-1'
        self.avgRTT = '-1'
        self.maxRTT = '-1'
        self.mdevRTT = '-1'


    """
    Tow Hop instances are considered as being equal if their IP addresses are the same.
    """
    def __eq__(self, other):
        return self.IP == other.IP


    """
    Tow Hop instances are considered as being unequal if their IP addresses are different.
    """
    def __ne__(self, other):
        return self.IP != other.IP


"""
Class representing a complete traceroute.
"""
class Traceroute:
    """
    Initiate a Traceroute instance
    """
    def __init__(self):
        self.hops = list()

        self.routeAge = 0
        self.resLife = -1

        self.timestamp = None
        self.timeslotIndex = 0

        self.lastHop = TracerouteHop()      # last hop of traceroute
        self.nextLastHop = TracerouteHop()  # last hop of the next traceroute sample

        self.currentNbChangesInSlot = None
        self.nbRouteChangesInSlot = 0
        self.nbRouteChangesInNextSlot = -1

        self.srcIP = None
        self.dstIP = None


    """
    Two Traceroute instances are considered as being equal if their lists of hops are the identical.
    """
    def __eq__(self, other):
        return self.hops == other.hops


    """
    Two Traceroute instances are considered as being unequal if their lists of hops are different.
    """
    def __ne__(self, other):
        return self.hops != other.hops


"""
Get the unixtimestamp from the string <dateString> in the format YYYYMMDDThh:mm:ss
YYYY = year
MM   = month
DD   = day
hh   = hour
mm   = minute
ss   = second
"""
def getUnixTimestamp(dateString):
    tracerouteTime = datetime.datetime.strptime(dateString, '%Y%m%dT%H:%M:%S')
    return time.mktime(tracerouteTime.timetuple())


"""
Get the index of the timeslot in <timeslotsLowerBounds> to which the route observed at time <timestamp> belongs to. A
timeslot in the array <timeslotsLowerBounds> is represented with its lower bound.  For instance, the entry for the
timeslot (0, 12) in the array is simply 0.
"""
def getTimeslotIndex(timeslotsLowerBounds, timestamp):
    return bisect.bisect_left(timeslotsLowerBounds, timestamp)


"""
Get the timeslots by which you want to separate your observation (learning) time. <timestamp> indicates the time (in
the unix-timestamp format) at which the observation time starts, <timeslotDuration> the duration (in hours) of one
timeslot, and <observationDuration> represents the duration of the observation time.
The timeslots are returned in the form of an array; each timeslot is represented by a tuple (<lb>, <ub>). <lb> is the lower
bound of this timeslot and <ub> is the upper bound.
"""
def getTimeslots(timestamp, timeslotDuration, observationDuration):
    numberOfTimeslotsBoundaries = math.ceil(observationDuration / timeslotDuration) + 1
    timeslotBoundaries = [timestamp + i * 60 * 60 * timeslotDuration for i in range(0, numberOfTimeslotsBoundaries)]
    timeslots = [tuple([timeslotBoundaries[i], timeslotBoundaries[i + 1]]) for i in
                 range(0, numberOfTimeslotsBoundaries - 1)]
    return timeslots


"""
Get statistics from the numpy array <numpyVec> containing either integers or floats. The statistics that are extracted are:
average (avg), minimum (min), maximum (max), 5% -, 10% -, 25% -, 50% -, 75% -, 90% -, and 95% - percentile (perc).
The collected stats are returned as strings in an array of the form:
[avg, min, max, 5perc, 10perc, 25perc, 50perc, 75perc, 90perc, 95perc].
If <numpyVec> is empty, return an array filled with 0's (length = 10).
"""
def getStatisticsVector(numpyVec):
    NUMBER_OF_STATS = 10
    if len(numpyVec):
        # average
        average = np.mean(numpyVec)

        # min
        minimum = min(numpyVec)

        # max
        maximum = max(numpyVec)

        # 5% -, 10% -, 25% -, 50% -, 75% -, 90% -, and 95% - percentile
        percentiles = np.percentile(numpyVec, [5, 10, 25, 50, 75, 90, 95])

        # vector containing computed statistics
        return [str(average), str(minimum), str(maximum)] + map(str, percentiles)
    else:
        return ['0' for i in range(0, NUMBER_OF_STATS)]


def getFeatures(filename, observationDuration, timeslotDuration):
    with open(filename, 'r') as inputFile:
        diffTraceroutes = list()  # observed traceroutes without sequential repetition; example: A A B A is stored as A B A)
        traceroutes     = list()  # all obsserved traceroutes

        timestampMeasurementsBegin = None  # timestamp indicating the time at which the first traceroute was observed

        currentTraceroute = Traceroute()

        # each index corresponds to a timeslotIndex which points to a list of traceroutes corresponding to that timeslot
        # same traceroute-storing principle as for <difftraceroutes>
        routesInSlots = list()

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
                    unixTimestamp = getUnixTimestamp(data[1])

                    if not timestampMeasurementsBegin:   # first traceroute in file
                        # prepare the different timeslots: each traceroute sample will be assigned to its corresponding
                        # timeslot so that we can compute the number of route changes in each slot later
                        timeslots = getTimeslots(unixTimestamp, timeslotDuration, observationDuration)
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
                    hop.minRTT = data[2]
                    hop.avgRTT = data[3]
                    hop.maxRTT = data[4]
                    hop.mdevRTT = data[5]

                    currentTraceroute.hops.append(hop)

                    # if we obtained a responde (i.e. we have the corresponding IP and the minimum RTT), consider this
                    # hop as the last traceroute hop
                    if hop.minRTT != '-1' and hop.IP != 'NA':
                        currentTraceroute.lastHop = hop

                # all information about one traceroute has been collected - wrap up with this one
                elif data[0] == 'END':
                    # add this traceroute to its corresponding timeslot
                    timeslotIndex = getTimeslotIndex(timeslotsLowerBounds, currentTraceroute.timestamp)
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
                tracert.resLife = float(diffTraceroutes[currentIndexDiffTraceroutes + 1].timestamp) - float(tracert.timestamp)
            tracert.routeAge = float(tracert.timestamp) - float(diffTraceroutes[currentIndexDiffTraceroutes])

            # does the next traceroute represent the same route as the current traceroute?
            if currentIndexTraceroutes < lengthTraceroutes and traceroutes[currentIndexTraceroutes] != traceroutes[currentIndexTraceroutes + 1]:
                currentIndexDiffTraceroutes += 1  # move on to the next traceroute in <diffTraceroutes>

            if tracert.lastHop.minRTT != '-1':
                minRTTs.append(float(tracert.lastHop.minRTT))
                avgRTTs.append(float(tracert.lastHop.avgRTT))
                maxRTTs.append(float(tracert.lastHop.maxRTT))
                mdevRTTs.append(float(tracert.lastHop.mdevRTT))

            # save the hop of the next traceroute sample to the current traceroute will be used for feature computation later)
            if currentIndexTraceroutes < lengthTraceroutes - 1:
                tracert.nextLastHop = traceroutes[currentIndexTraceroutes + 1].lastHop
            else:
                tracert.nextLastHop = tracert.lastHop

            currentIndexTraceroutes += 1

        # compute stats about observed route durations
        routeDurations_np = np.array(routeDurations)  # create numpy array
        routeDurationVector = getStatisticsVector(routeDurations_np)

        # compute stats about route changes in timeslots
        nbRouteChangesInTimeslots = [len(routes) - 1 if len(routes) > 0 else 0 for routes in routesInSlots]
        nbRouteChangesInTimeslots_np = np.array(nbRouteChangesInTimeslots)
        nbRouteChangesInTimeslotsVector = getStatisticsVector(nbRouteChangesInTimeslots_np)

        # compute stats about observed average RTTs
        avgRTTs_np = np.array(avgRTTs)  # create numpy array
        avgRTTVector = getStatisticsVector(avgRTTs_np)

        # compute stats about observed minimum RTTs
        minRTTs_np = np.array(minRTTs)  # create numpy array
        minRTTVector = getStatisticsVector(minRTTs_np)