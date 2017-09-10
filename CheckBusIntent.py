from google.transit import gtfs_realtime_pb2
import time
import boto3


def check_bus(bus_id, stop_id):
    s3 = boto3.resource('s3')
    s3_object = s3.Object('austin-transit', 'tripupdates.pb')

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(s3_object.get()['Body'].read())

    stop_time_updates_raw = list(
        map(lambda x: list(x.trip_update.stop_time_update),
            filter(lambda x: x.trip_update.trip.route_id == str(bus_id), feed.entity)))

    if len(stop_time_updates_raw) == 0:
        return []

    stop_time_updates = filter(lambda x: x.stop_id == str(stop_id), reduce(list.__add__, stop_time_updates_raw))

    if len(stop_time_updates) == 0:
        return []

    current_time = time.time()

    minutes_list = []

    for stu in stop_time_updates:
        print 'stop_id = %s\tdelays = %s\ttime = %s' \
              % (stu.stop_id, stu.arrival.delay,
                 time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime(stu.arrival.time)))
        minutes = int((stu.arrival.time - current_time) / 60)
        if minutes >= 0:
            minutes_list.append(minutes)

    return sorted(minutes_list)


if __name__ == '__main__':
    print check_bus(7, 1174)
