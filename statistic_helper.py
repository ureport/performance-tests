import re
import subprocess
from datetime import datetime

def statistic_for(name, latency_request_list):
    average_latency = get_average_latency(latency_request_list)
    max_latency = max(latency_request_list)
    min_latency = min(latency_request_list)
    median_latency = median(latency_request_list)

    print "Statistics for " + name
    print latency_request_list
    print "Total : %s" % str(len(latency_request_list))
    print 'Average latency:' + str(average_latency)
    print 'Max latency:' + str(max_latency)
    print 'Min latency:' + str(min_latency)
    print 'Median latency: ' + str(median_latency)

def get_average_latency(latency_request_list):
    return sum(latency_request_list) / len(latency_request_list)

def get_diff(start_time, end_time):
    diff = (end_time - start_time)
    return diff.total_seconds()

def execute_command(command):
    shell_response = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    lines = shell_response.stdout.readlines()
    if len(lines) > 0:
        return lines[0].strip()
    else:
        return None

def not_empty(value):
    return value is not None and value!=""

def median(a):
    ordered = sorted(a)
    length = len(a)
    return float((ordered[length/2] + ordered[-(length+1)/2]))/2

def get_time_from_result(result, regex, group_number, time_format):
    if result is not None:
        result_time = re.search(regex, result, re.IGNORECASE)
        result_time = result_time.group(group_number)

        time = datetime.strptime(result_time, time_format)
        return time
    else:
        return None