import datetime, time, bisect, math, numpy as np

"""
Class representing a traceroute hop
"""
class TracerouteHop:
    def __init__(self):
        self.IP = ''

        self.minRTT = '-1'
        self.avgRTT = '-1'
        self.maxRTT = '-1'
        self.mdevRTT = '-1'

    def __eq__(self, other):
        return self.IP == other.IP

    def __ne__(self, other):
        return self.IP != other.IP

"""
Class representing a complete traceroute
"""
class Traceroute:
    def __init__(self):
        self.hops = list()

        self.routeAge = '0'
        self.routeDuration = '0'
        self.resLife = '-1'

        self.timestamp = '-1'
        self.timeSlotIndex = 0

        self.lastHop = TracerouteHop()
        self.nextHop = TracerouteHop()

        self.currentNbChangesInSlot = 0
        self.nbRouteChangesInSlot = '-1'

        self.nbRouteChangesInNextSlot = '-1'

    def __eq__(self, other):
        return self.hops == other.hops

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
    ts = dateString.split('T')

    dayInfo = ts[0]
    hourInfo = ts[1]
    hourInfo = hourInfo.split(':')

    year = int(dayInfo[0:4])
    month = int(dayInfo[4:6])
    day = int(dayInfo[6:8])
    hour = int(hourInfo[0])
    minute = int(hourInfo[1])
    second = int(hourInfo[2])

    tracerouteTime = datetime.datetime(year, month, day, hour, minute, second)
    unixts = time.mktime(tracerouteTime.timetuple())

    return unixts


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
The collected stats are returned in an array of the form:
[avg, min, max, 5perc, 10perc, 25perc, 50perc, 75perc, 90perc, 95perc].
"""
def getStatisticsVector(numpyVec):
    average = np.mean(numpyVec)

    # min route age
    minimum = min(numpyVec)

    # max route age
    maximum = max(numpyVec)

    # 5% percentile
    perc5 = np.percentile(numpyVec, 5)

    # 10% percentile
    perc10 = np.percentile(numpyVec, 10)

    # 25% percentile
    perc25 = np.percentile(numpyVec, 25)

    # 50% percentile
    perc50 = np.percentile(numpyVec, 50)

    # 75% percentile
    perc75 = np.percentile(numpyVec, 75)

    # 90% percentile
    perc90 = np.percentile(numpyVec, 90)

    # 95% percentile
    perc95 = np.percentile(numpyVec, 95)

    # vector containing computed statistics
    return [str(average), str(minimum), str(maximum), str(perc5), str(perc10), str(perc25), str(perc50),
            str(perc75), str(perc90), str(perc95)]