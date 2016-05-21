import re
import copy
import euclid

from analysisperiod import AnalysisPeriod


class LBHeader:
    """Standard Ladybug header for lists.

    The header carries data for city, data type, unit, and analysis period

    Attributes:
        city: A string for the city name
        dataType: A valid Ladybug data type. Try DataType.dataTypes to see list of data types
        unit: dataType unit. If empty string it will be set based on dataType
        timestep: Data timestep "Hourly", "Daily", "Monthly", "Annual", "N/A"
        analysisPeriod: A Ladybug analysis period. (defualt: 1 Jan 1 to 31 Dec 24)
    """

    def __init__(self, city='unknown', dataType='unknown', unit='unknown',
                 frequency='unknown', analysisPeriod=None):
        """Initiate Ladybug header for lists."""
        self.city = city
        self.dataType = dataType
        self.unit = unit
        self.frequency = frequency
        self.analysisPeriod = 'unknown' if not analysisPeriod \
            else AnalysisPeriod.fromAnalysisPeriod(analysisPeriod)

    def duplicate(self):
        """Duplicate header."""
        return copy.deepcopy(self)

    @property
    def __key(self):
        return 'location|dataType|units|frequency|dataPeriod'

    def toList(self):
        """Return Ladybug header as a list."""
        return [
            self.__key,
            self.city,
            self.dataType,
            self.unit,
            self.frequency,
            self.analysisPeriod
        ]

    def __repr__(self):
        """Return Ladybug header as a string."""
        return "%s for %s during %s" % (self.dataType, self.city, self.analysisPeriod)


# TODO: write classes for latitude, longitude, etc
class Location:
    """Ladybug Location class."""

    def __init__(self, city='', country='', latitude='0.00',
                 longitude='0.00', timeZone='0.00', elevation='0.00',
                 source='', stationId=''):
        """Create a Ladybug location."""
        self.city = str(city)
        self.country = str(country)
        self.latitude = float(latitude)
        self.longitude = float(longitude)
        self.timeZone = float(timeZone)
        self.elevation = float(elevation)
        self.source = str(source)
        self.stationId = str(stationId)

    def createFromEPString(self, EPString):
        """Create a Ladybug location from an EnergyPlus location string.

        Args:
            EPString: Standard EP location string

        Usage:

            l = Location() #initiate location
            l.createFromEPString(EPString)
            print "LAT:%s, LON:%s"%(l.latitude, l.longitude)
        """
        try:
            self.city, self.latitude, self.longitude, self.timeZone, \
                self.elevation = re.findall(
                    r'\r*\n*([a-zA-Z0-9.:_-]*)[,|;]', EPString, re.DOTALL
                )[1:]

            self.latitude = float(self.latitude)
            self.longitude = float(self.longitude)
            self.timeZone = float(self.timeZone)
            self.elevation = float(self.elevation)
        except Exception, e:
            raise Exception("Failed to import EP string! %s" % str(e))

    def duplicate(self):
        """Duplicate location."""
        return copy.deepcopy(self)

    @property
    def EPStyleLocationString(self):
        """Return EnergyPlus's location string."""
        return "Site:Location,\n" + \
            self.city + ',\n' + \
            str(self.latitude) + ',      !Latitude\n' + \
            str(self.longitude) + ',     !Longitude\n' + \
            str(self.timeZone) + ',     !Time Zone\n' + \
            str(self.elevation) + ';       !Elevation'

    def __repr__(self):
        """Return location as a string."""
        return "%s" % (self.EPStyleLocationString)


class LBData(object):
    """Ladybug data point."""

    __slots__ = ("__value", "datetime")

    # TODO: Change value to be an object from it's data type
    # Check datatype.py for available datatypes
    def __init__(self, value, dateTime):
        """Create Ladybug data point."""
        self.datetime = dateTime
        self.value = value

    @classmethod
    def fromLBData(cls, data):
        """Create Ladybug datapoint from a Ladybug datapoint."""
        assert isinstance(data, LBData), "Input is not a LBData."
        return data

    @property
    def value(self):
        """Get/set value of data."""
        return self.__value

    @value.setter
    def value(self, newValue):
        """Update value of LBData."""
        self.__value = newValue

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def __str__(self):
        return str(self.value)

    def __eq__(self, other):
        return self.value == float(other)

    def __ne__(self, other):
        return self.value != float(other)

    def __lt__(self, other):
        return self.value < other

    def __gt__(self, other):
        return self.value > other

    def __le__(self, other):
        return self.value <= other

    def __ge__(self, other):
        return self.value >= other

    def __add__(self, other):
        return self.value + other

    def __sub__(self, other):
        return self.value - other

    def __mul__(self, other):
        return self.value * other

    def __floordiv__(self, other):
        return self.value // other

    def __div__(self, other):
        return self.value / other

    def __mod__(self, other):
        return self.value % other

    def __pow__(self, other):
        return self.value**other

    def __radd__(self, other):
        return self.__add__(other)

    def __rsub__(self, other):
        return other - self.value

    def __rmul__(self, other):
        return self.__mul__(other)

    def __rfloordiv__(self, other):
        return other // self.value

    def __rdiv__(self, other):
        return other / self.value

    def __rmod__(self, other):
        return other % self.value

    def __rpow__(self, other):
        return other**self.value

    def __repr__(self):
        return self.__str__()


class LBPatchData(LBData):
    """Ladybug sky patch data."""

    def __init__(self, value, vector):
        """Create Ladybug sky patch data."""
        # sky data doesn't have time
        datetime = LBDateTime()
        LBData.__init__(self, value, datetime)
        self.vector = euclid.Vector3(*vector)


class DataList:
    """Ladybug data list.

    A list of ladybug data with a LBHeader
    """

    def __init__(self, data=None, header=None):
        """Create a DataList."""
        self.__data = self.checkInputData(data)
        self.header = LBHeader() if not header else header

    def values(self, header=False):
        """Return the list of values.

        Args:
            header: A boolean that indicates if values should include the headers

        Return:
            A list of values
        """
        if not header:
            return self.__data
        else:
            return self.header.toList() + self.__data

    @property
    def timeStamps(self):
        """Return list of time stamps for current data."""
        return [value.datetime for value in self.__data]

    def checkInputData(self, data):
        """Check input data."""
        if not data:
            return []

        return [LBData.fromLBData(d) for d in data]

    def append(self, data):
        """Append LBData to current list."""
        self.extend([data])

    def extend(self, dataList):
        """Extend a list of LBData to the end of current list."""
        self.__data.extend(self.checkInputData(dataList))

    def duplicate(self):
        """Duplicate current data list."""
        return copy.deepcopy(self)

    @staticmethod
    def average(data):
        """Return average value for a list of values."""
        values = [value.value for value in data]
        return sum(values) / len(data)

    def groupDataByMonth(self, monthRange=range(1, 13), userDataList=None):
        """
        Return a dictionary of values where values are grouped for each month.

        Key values are between 1-12

        Args:
           monthRange: A list of numbers for months. Default is 1-12
           userDataList: An optional data list of LBData to be processed

        Usage:

           epwfile = EPW("epw file address")
           monthlyValues = epwfile.dryBulbTemperature.groupValuesByMonth()
           print monthlyValues[2] # returns values for the month of March
        """
        hourlyDataByMonth = {}
        if userDataList:
            data = [LBData.fromLBData(d) for d in userDataList]
        else:
            data = self.__data

        for d in data:
            if d.datetime.month not in monthRange:
                continue

            if d.datetime.month not in hourlyDataByMonth:
                hourlyDataByMonth[d.datetime.month] = []  # create an empty list for month

            hourlyDataByMonth[d.datetime.month].append(d)

        print "Found data for months " + str(hourlyDataByMonth.keys())
        return hourlyDataByMonth

    def groupDataByDay(self, dayRange=range(1, 366), userDataList=None):
        """
        Return a dictionary of values where values are grouped by each day of year.

        Key values are between 1-365

        Args:
           dayRange: A list of numbers for days. Default is 1-365
           userDataList: An optional data list of LBData to be processed

        Usage:

           epwfile = EPW("epw file address")
           dailyValues = epwfile.dryBulbTemperature.groupDataByDay(range(1, 30))
           print dailyValues[2] # returns values for the second day of year
        """
        hourlyDataByDay = {}

        if userDataList:
            data = [LBData.fromLBData(d) for d in userDataList]
        else:
            data = self.__data

        for d in data:
            DOY = DateTimeLib.getDayOfYear(d.datetime.month, d.datetime.day)

            if DOY not in dayRange:
                continue

            if DOY not in hourlyDataByDay:
                hourlyDataByDay[DOY] = []  # create an empty list for month

            hourlyDataByDay[DOY].append(d)

        print "Found data for " + str(len(hourlyDataByDay.keys())) + " days."
        return hourlyDataByDay

    def groupDataByHour(self, hourRange=range(1, 25), userDataList=None):
        """Return a dictionary of values where values are grouped by each hour of day.

        Key values are between 1-24

        Args:
           hourRange: A list of numbers for hours. Default is 1-24
           userDataList: An optional data list of LBData to be processed

        Usage:

           epwfile = EPW("epw file address")
           monthlyValues = epwfile.dryBulbTemperature.groupDataByMonth([1])
           groupedHourlyData = epwfile.dryBulbTemperature.groupDataByHour(userDataList = monthlyValues[2])
           for hour, data in groupedHourlyData.items():
               print "average temperature values for hour {} during JAN is {} {}".format(
               hour, core.DataList.average(data), DBT.header.unit)
        """
        hourlyDataByHour = {}

        if userDataList:
            data = [LBData.fromLBData(d) for d in userDataList]
        else:
            data = self.__data

        for d in data:

            if d.datetime.hour not in hourRange:
                continue

            if d.datetime.hour not in hourlyDataByHour:
                hourlyDataByHour[d.datetime.hour] = []  # create an empty list for month

            hourlyDataByHour[d.datetime.hour].append(d)

        print "Found data for hours " + str(hourlyDataByHour.keys())
        return hourlyDataByHour

    # TODO: Add validity check for input values
    def updateDataForAnAnalysisPeriod(self, values, analysisPeriod=None):
        """Replace current values in data list with new set of values.

        Length of values should be equal to number of hours in analysis period.

        Args:
            values: A list of values to be replaced in the file
            analysisPeriod: An analysis period for input the input values.
                Default is set to the whole year.
        """
        if not analysisPeriod:
            analysisPeriod = AnalysisPeriod()

        # check length of data vs length of analysis period
        if len(values) != analysisPeriod.totalNumOfHours:
            raise ValueError(
                "Length of values %d is not equal to " +
                "number of hours in analysis period %d." % (len(values), analysisPeriod.totalNumOfHours)
            )

        # get all time stamps
        timeStamps = analysisPeriod.dates

        # map timeStamps and values
        newValues = {}
        for count, value in enumerate(values):
            HOY = timeStamps[count].HOY
            newValues[HOY] = value

        # update values
        updatedCount = 0
        for counter, data in enumerate(self.__data):
            try:
                value = newValues[data.datetime.HOY]
                data.updateValue(value)
                updatedCount += 1
            except KeyError:
                pass

        # return self for chaining methods
        print "%s data are updated for %d hours." % (self.header.dataType, updatedCount)

        # return self for chaining methods
        return self

    def updateDataForHoursOfYear(self, values, hoursOfYear):
        """Replace current values in data list with new set of values for a list of hours of year.

        Length of values should be equal to number of hours in hours of year

        Args:
            values: A list of values to be replaced in the file
            hoursOfYear: A list of HOY between 1 and 8760
        """
        # check length of data vs length of analysis period
        if len(values) != len(hoursOfYear):
            raise ValueError("Length of values %d is not equal to " +
                             "number of hours in analysis period %d" %
                             (len(values), len(hoursOfYear)))

        # map hours and values
        newValues = {}
        for count, value in enumerate(values):
            HOY = hoursOfYear[count]
            newValues[HOY] = value

        # update values
        updatedCount = 0
        for counter, data in enumerate(self.__data):
            try:
                value = newValues[data.datetime.HOY]
                data.updateValue(value)
                updatedCount += 1
            except KeyError:
                pass

        print "%s data %s updated for %d hour%s." % \
            (self.header.dataType,
             'are' if len(values) > 1 else 'is',
             updatedCount,
             's' if len(values) > 1 else '')

        # return self for chaining methods
        return self

    def updateDataForAnHour(self, value, hourOfYear):
        """
        Replace current value in data list with a new value for a specific HOY.

        Args:
            value: A single value
            hoursOfYear: The hour of the year
        """
        return self.updateDataForHoursOfYear([value], [hourOfYear])

    def filterByAnalysisPeriod(self, analysisPeriod):
        """
        Filter a list based on an analysis period.

        Args:
           analysis period: A Ladybug analysis period

        Return:
            A new DataList with filtered data

        Usage:

           # start of Feb to end of Mar
           analysisPeriod = AnalysisPeriod(2,1,1,3,31,24)
           epw = EPW("c:/ladybug/weatherdata.epw")
           DBT = epw.dryBulbTemperature
           filteredDBT = DBT.filterByAnalysisPeriod(analysisPeriod)
        """
        if not analysisPeriod or analysisPeriod.isAnnual:
            print "You need a valid analysis period to filter data."
            return self

        # There is no guarantee that data is continuous so I iterate through the
        # each data point one by one
        filteredData = [d for d in self.__data if analysisPeriod.isTimeIncluded(d.datetime)]

        # create a new filteredData
        filteredHeader = self.header.duplicate()
        filteredHeader.analysisPeriod = analysisPeriod
        filteredDataList = DataList(filteredData, filteredHeader)

        return filteredDataList

    def filterByHOYs(self, HOYs):
        """Filter the list based on an analysis period.

        Args:
           HOYs: A List of hours of the year [1-8760]

        Return:
            A new DataList with filtered data

        Usage:

           HOYs = range(1,48)  # The first two days of the year
           epw = EPW("c:/ladybug/weatherdata.epw")
           DBT = epw.dryBulbTemperature
           filteredDBT = DBT.filterByHOYs(HOYs)
        """
        # There is no guarantee that data is continuous so I iterate through the
        # each data point one by one
        filteredData = [d for d in self.__data if d.datetime.HOY in HOYs]

        # create a new filteredData
        filteredHeader = self.header.duplicate()
        filteredHeader.analysisPeriod = "unknown"
        filteredDataList = DataList(filteredData, filteredHeader)

        return filteredDataList

    def filterByConditionalStatement(self, statement):
        """Filter the list based on an analysis period.

        Args:
           statement: A conditional statement as a string (e.g. x>25 and x%5==0).
            The variable should always be named as x

        Return:
            A new DataList with filtered data

        Usage:

           epw = EPW("c:/ladybug/weatherdata.epw")
           DBT = epw.dryBulbTemperature
           # filter data for when dry bulb temperature is more then 25
           filteredDBT = DBT.filterByConditionalStatement('x > 25')
           # get the list of time stamps that meet the conditional statement
           print filteredDBT.timeStamps
        """
        def checkInputStatement(statement):
            stStatement = statement.lower() \
                .replace("and", "").replace("or", "") \
                .replace("not", "").replace("in", "").replace("is", "")

            l = [s for s in stStatement if s.isalpha()]
            if list(set(l)) != ['x']:
                statementErrorMsg = 'Invalid input statement. ' + \
                    'Statement should be a valid Python statement' + \
                    ' and the variable should be named as x'
                raise ValueError(statementErrorMsg)

        checkInputStatement(statement)

        statement = statement.replace('x', 'd.value')
        filteredData = [d for d in self.__data if eval(statement)]

        # create a new filteredData
        filteredHeader = self.header.duplicate()
        filteredHeader.analysisPeriod = 'N/A'
        filteredDataList = DataList(filteredData, filteredHeader)

        return filteredDataList

    def filterByPattern(self, patternList):
        """Filter the list based on a list of Boolean.

        Length of Boolean should be equal to length of values in DataList

        Args:
            patternList: A list of True, False values

        Return:
            A new DataList with filtered data
        """
        # check length of data vs length of analysis period
        if len(self.values) != len(patternList):

            print len(self.values), len(patternList)

            errMsg = "Length of values %d is not equal to number of patterns %d" \
                % AnalysisPeriod(len(self.values), len(patternList))

            raise ValueError(errMsg)

        filteredData = [d for count, d in enumerate(self.__data) if patternList[count]]

        # create a new filteredData
        filteredHeader = self.header.duplicate()
        filteredHeader.analysisPeriod = 'N/A'
        filteredDataList = DataList(filteredData, filteredHeader)

        return filteredDataList

    def averageMonthly(self, userDataList=None):
        """Return a dictionary of values for average values for available months."""
        # group data for each month
        monthlyValues = self.groupDataByMonth(userDataList=userDataList)

        averageValues = dict()

        # average values for each month
        for month, values in monthlyValues.items():
            averageValues[month] = self.average(values)

        return averageValues

    def averageMonthlyForEachHour(self, userDataList=None):
        """Calculate average value for each hour during each month.

        This method returns a dictionary with nested dictionaries for each hour
        """
        # get monthy values
        monthlyHourlyValues = self.groupDataByMonth(userDataList=userDataList)

        # group data for each hour in each month and collect them in a dictionary
        averagedMonthlyValuesPerHour = {}
        for month, monthlyValues in monthlyHourlyValues.items():
            if month not in averagedMonthlyValuesPerHour:
                averagedMonthlyValuesPerHour[month] = {}

            # group data for each hour
            groupedHourlyData = self.groupDataByHour(userDataList=monthlyValues)
            for hour, data in groupedHourlyData.items():
                averagedMonthlyValuesPerHour[month][hour] = self.average(data)

        return averagedMonthlyValuesPerHour

    def __len__(self):
        return len(self.__data)

    def __getitem__(self, key):
        return self.__data[key]

    def __setitem__(self, key, value):
        self.__data[key] = value

    def __delitem__(self, key):
        del self.__data[key]

    def __iter__(self):
        return iter(self.__data)

    # TODO: Reverse analysis period in header
    def __reversed__(self):
        return list(reversed(self.__data))

    def __repr__(self):
        return "Ladybug.DataList#%s" % self.header.dataType
