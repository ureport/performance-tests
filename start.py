#create several messages with unique contact numbers
import re
import subprocess
import time
import requests
import numpy

def generate_numbers(number_of_phone_numbers):
    numbers = []
    for n in range(0, number_of_phone_numbers):
        numbers.append("%s%s" % (n, str(int(time.time()))))
    return numbers


def send_message(number, message):
    print "Sending %s to number %s" % (message, number)
    url = "http://2.2.2.2/router/receive/?sender=%s&message=%s&backend=dev" % (number, message)
    time_sent = time.time()
    response = requests.get(url)
    return time_sent, response

def generate_report(message_stats):
    results = []
    for key, value in message_stats.iteritems():
        if 'end' in value:
            results.append(int(value['end']) - value['start'])
    print "timeout was set to %d sec" % timeout
    print "number of incomplete message: %d" % (len(message_stats) - len(results))
    print "number of messages: %d" % len(results)
    print "mean: %d sec" % numpy.mean(results)
    print "min: %d sec" % numpy.min(results)
    print "max: %d sec" % numpy.max(results)
    print "5th percentile: %f sec" % numpy.percentile(results, 5)
    print "10th percentile: %f sec" % numpy.percentile(results, 10)
    print "50th percentile: %f sec" % numpy.percentile(results, 50)
    print "95th percentile: %f sec" % numpy.percentile(results, 95)
    print "99th percentile: %f sec" % numpy.percentile(results, 99)

def parse_data_from_line(line):
    gex = re.compile("destination_addr=(\d+) .* timestamp=(\d+)")
    match = gex.search(line)
    if match:
        return match.groups()
    return None

### MAIN

logfile = "/vagrant/python-smpp/smpp/smsc.log"
timeout = 300
number_of_phone_numbers = 1000
counter = 0

numbers = generate_numbers(number_of_phone_numbers)
message_stats = {}
for number in numbers:
    time_sent, response = send_message(number, "join")
    message_stats[number] = {"start": time_sent, "response": response.status_code}

f = subprocess.Popen(['tail', '-F', logfile], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

start_time = time.time()
while True:
    line = f.stdout.readline()
    matched_data = parse_data_from_line(line)
    if matched_data is not None:
        print  matched_data
        number = matched_data[0]
        time_rec = matched_data[1]
        if number in message_stats and "end" not in message_stats[number]:
            counter += 1
            print "received message %d/%d" % (counter, number_of_phone_numbers)
            message_stats[number]['end'] = time_rec
    if counter == number_of_phone_numbers or (time.time() - start_time) > timeout:
        break

generate_report(message_stats)