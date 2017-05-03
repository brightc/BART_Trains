
import urllib2
import xml.etree.ElementTree as ET


class DepartingTrain(object):
    """
    An object to store the departing train's data:

    1. Destination
    2. Time to Depature
    """
    def __init__(self, destination, time_to_departure):
        self._destination = destination
        self._time_to_departure = time_to_departure

    @property
    def destination(self):
        return self._destination

    @property
    def time_to_departure(self):
        return self._time_to_departure


def populate_departing_train_times(station_root, max_train_count):
    """
    Populate the departing train times into a list, and then sort it
    by the departure times.

    :station_root: The XML node containing the station's train departure
        data
    :type: str

    :max_train_count: The maximum number of train departure data to obtain
        from the BART's XML data.
    :type: int

    :return A list of train destinations and departure times, sorted by
        departure times, in the ascending order.
    :type: list
    """
    departing_trains = []

    train_count = 0

    for etd in station_root.findall("etd"):
        destination = etd.find("destination").text
        time_to_leave = etd.find("estimate").find("minutes").text

        departing_time = None
        if time_to_leave.lower() == "leaving":
            # BART's departure minutes are in string, but we need all the departing
            # times to be in integers for sorting
            departing_time = 0
        else:
            departing_time = int(time_to_leave)

        departing_trains.append(DepartingTrain(destination, departing_time))

        train_count += 1
        if train_count == max_train_count:
            break

    # Sort by the departure times (minutes)
    departing_trains = sorted(departing_trains, key=lambda train: train.time_to_departure)

    return departing_trains


def get_schedule_root(api_key, origin, schedule_url):
    """
    Obtain the schedule root from the BART's XML data
    :api_key: The user's API key that is allowed to access BART's data.
    :type: str

    :origin: The originating station name abbrevation, e.g. "MONT", as
        specified by the BART API.
    :type: str

    :schedule_url: The API URL, as specified by BART.
    :type: str

    :return: a string that contains the entire BART's train departure data, in
        XML format.
    :type: str
    """
    schedule_contents = ""
    try:
        schedule_contents = urllib2.urlopen(schedule_url + origin + "&key=" + api_key).read()
    except (urllib2.URLError, urllib2.HTTPError) as url_error:
        print("Cannot access the URL '%(url)s'. Error message: '%(error)s'. The BART API site "
              "could be unavailable. You'll have to try again later." % {
                  "url": schedule_url + origin + "&key=" + api_key,
                  "error": url_error}
              )

    return ET.fromstring(schedule_contents)


def main():
    # Currently, using the API demo key
    API_KEY = "MW9S-E7SL-26DU-VV8V"
    SCHEDULE_URL = "http://api.bart.gov/api/etd.aspx?cmd=etd&orig="

    TRAIN_COUNT_LIMIT = 10

    schedule_root = get_schedule_root(API_KEY, "MONT", SCHEDULE_URL)

    try:
        error = schedule_root.find("message").find("error").find("text").text
        details = schedule_root.find("message").find("error").find("details").text

        if (len(error)):
            print("Error from the server: '%(e)s'. Error details: '%(details)s'. "
                  "Your API call could be incorrect. Validate your API call and "
                  "try again." % {"e": error, "details": details})
            return

    except AttributeError:
        # No error returned from the server, so continue
        pass

    date = schedule_root.find("date").text
    time = schedule_root.find("time").text

    station_root = schedule_root.find("station")
    station_name = station_root.find("name").text

    departing_trains = populate_departing_train_times(station_root, TRAIN_COUNT_LIMIT)

    print("--------------------------------------------------")
    print(station_name + "\t" + date + "\t" + time)
    print("--------------------------------------------------")

    for train in departing_trains:
        t = train.time_to_departure
        if t == 0:
            print("Leaving " + train.destination)
        else:
            print(str(t) + " min " + train.destination)


if __name__ == "__main__":
    main()
