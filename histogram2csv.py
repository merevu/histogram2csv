import requests
import json
import datetime
import sys
import csv


def toDate(timestamp):
    value = datetime.datetime.fromtimestamp(timestamp / 1000)
    return value.strftime('%Y-%m-%d')


def toTime(timestamp):
    value = datetime.datetime.fromtimestamp(timestamp / 1000)
    return value.strftime('%H:%M:%S')


def getQueryIdx(input_json):
    queries = {}
    input_json = input_json[:-1]
    # print readed
    loaded = json.loads(input_json)
    # print loaded

    i = 0
    try:
        while True:
            x = loaded['facets'][str(i)]['facet_filter']['fquery']['query']['filtered']['query']['query_string'][
                'query']
            queries[str(i)] = x
            i += 1
    except BaseException, e:
        pass

    return queries


def getIdx(dic, key):
    return dic[key]


def main(json_input=None, csv_output=None):
    # Read the request
    with open(json_input, "r") as f_in:
        request = f_in.read()

    # Split URL and request
    curl_request = request.split("' -d '")
    p = curl_request[0].find("-XGET ")
    url = curl_request[0][p + 7:]
    request = curl_request[1][0:-1]

    queryIdx = getQueryIdx(request)
    response = requests.post(url, data=request)
    response_json = json.loads(response.text)

    if "facets" in response_json:
        i = 0
        with open(csv_output, "wb") as f_out:
            writer = csv.writer(f_out)
            try:
                writer.writerow(['date', 'time', 'query', 'min', 'max', 'total', 'total_count', 'mean'])
                while True:
                    if response_json["facets"][str(i)]["entries"]:
                        for x in response_json["facets"][str(i)]["entries"]:
                            writer.writerow(
                                [toDate(x['time']), toTime(x['time']), queryIdx[str(i)], x['min'], x['max'], x['total'],
                                 x['total_count'],
                                 x['mean']])
                    i = i + 1
            except Exception, e:
                # print e
                pass


if __name__ == "__main__":

    input_file = None
    output_file = None

    for arg in sys.argv:
        if arg.find('=') > 0:
            strArg = arg.split('=')

            if str(strArg[0]).lower() == '--in':
                input_file = str(strArg[1])

            if str(strArg[0]).lower() == '--out':
                output_file = str(strArg[1])

    now = str(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))

    if not input_file or not output_file:
        print 'USAGE: python histogram2csv.py --in=[INPUT_JSON] --out=[OUTPUT_CSV]'
        exit(1)

    main(json_input=input_file, csv_output=output_file)
