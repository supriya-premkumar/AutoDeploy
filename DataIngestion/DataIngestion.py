import requests
import json
import csv
import datetime
import argparse
from datetime import timedelta
from influxdb import InfluxDBClient

epoch = datetime.datetime.utcfromtimestamp(0)
def unix_time_hours(dt):
    return int((dt-epoch).total_seconds() * 1000)

def loadCsv(csvfile, server, user, password, metric, timecolumn, timeformat, tagcolumns, fieldcolumns, delimiter):
    host = '34.219.133.145'
    port = 8086
    dbname= 'ml-powerflow'
    client = InfluxDBClient(host, port, user, password, dbname)

    print('Creating Database %s'%dbname)
    client.create_database(dbname)


    # format tags and fields
    if tagcolumns:
        tagcolumns = tagcolumns.split(',')
    if fieldcolumns:
        fieldcolumns = fieldcolumns.split(',')

    #Open Csv
    datapoints =[]
    file = "csv/angle.csv"
    count = 0
    batchsize = 20000
    with open(file, 'r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delimiter)
        c=-1
        for row in reader:
            timestamp = datetime.datetime.now() + timedelta(hours = c, seconds = 0)
            c=c-1
            tags = {}
            for t in tagcolumns:
                v = 0
                if t in row:
                    v = row[t]
                tags[t] = v
                print("tag colums", tags[t])

            fields = {}
            for f in fieldcolumns:
                v = 0
                if f in row:
                    v = float(row[f])
                fields[f] = v
                print("field columns", fields[f])


            point = {"measurement": metric,"time":timestamp, "fields": fields, "tags": tags}
            print("timestamp", timestamp)

            datapoints.append(point)
            count+=1

            if len(datapoints) % batchsize == 0:
                print('Read %d lines'%count)
                print('Inserting %d datapoints...'%(len(datapoints)))
                response = client.write_points(datapoints)

                if response == False:
                    print('Problem inserting points, exiting...')
                    exit(1)

                print("Wrote %d, response: %s" % (len(datapoints), response))


                datapoints = []



    if len(datapoints) > 0:
        print('Read %d lines'%count)
        print('Inserting %d datapoints...'%(len(datapoints)))
        response = client.write_points(datapoints)

        if response == False:
            print('Problem inserting points, exiting...')
            exit(1)

        print("Wrote %d, response: %s" % (len(datapoints), response))

    print('Done')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Csv to influxdb.')
    parser.add_argument('-i', '--input', nargs='?', required=False, help='Input csv file.')
    parser.add_argument('-d', '--delimiter', nargs='?', required=False,default=',', help='CSV delimiter. Default:\',\'.')
    parser.add_argument('-s', '--server', nargs='?', default='54.193.103.207:8086', help='Server address. Default:54.193.103.207:8086')
    parser.add_argument('-u', '--user', nargs='?', default='ubuntu', help='user name.')
    parser.add_argument('-p', '--password', nargs='?', default='Slac_2018', help='password')

    parser.add_argument('-m', '--metricname', nargs='?', default='phase_angle',
                        help='Metric column name. Default: value')
    parser.add_argument('-tc', '--timecolumn', nargs='?', default='timestamp',
                        help='Timestamp column name. Default: timestamp.')
    parser.add_argument('-tf', '--timeformat', nargs='?', default='%Y-%m-%d %H:%M:%S',
                        help='Timestamp format. Default: \'%%Y-%%m-%%d %%H:%%M:%%S\' e.g.: 1970-01-01 00:00:00')
    parser.add_argument('--fieldcolumns', nargs='?', default='value',
                        help='List of csv columns to use as fields, separated by comma, e.g.: value1,value2. Default: value')

    parser.add_argument('--tagcolumns', nargs='?', default='host',
                        help='List of csv columns to use as tags, separated by comma, e.g.: host,data_center. Default: host')


    args = parser.parse_args()
    loadCsv(args.input, args.server, args.user, args.password, args.metricname, args.timecolumn, args.timeformat, args.tagcolumns, args.fieldcolumns, args.delimiter)


# run --> python DataIngestion.py  --tagcolumns 0,1,2,3,4,5,6,7
