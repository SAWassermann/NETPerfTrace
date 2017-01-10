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
Get the index of the timeslot in <timeslotsLowerBounds> to which the route observed at time <timestamp> belongs to. A
timeslot in the array <timeslotsLowerBounds> is represented with its lower bound.  For instance, the entry for the
timeslot (0, 12) in the array is simply 0.
"""
def getTimeslotIndex(timeslotsLowerBounds, timestamp):
    return bisect.bisect_left(timeslotsLowerBounds, timestamp)


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