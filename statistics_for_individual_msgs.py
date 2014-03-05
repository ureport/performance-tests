import re
import subprocess
from datetime import datetime

def run_test():
    """
    Filter individual messages from db -> get id, connection_id and date
    Steps
    1.- Get send_message logs from the time that a big poll was sent out
    2.- Filter the logs for individual send sms E.g.grep -i "INFO: SMS\[........\] SENT" messenger.log
    3.- Get from db message detail where ids in the ids filter from logs and direction='O' and batch is NULL
    -> this info in send_individuals.txt
    """
    line = 3
    limit = 50
    time_diff_msg_db_to_send_out = []


    while (line < limit):
        times = getting_times_for_line(line)
        time_diff_msg_db_to_send_out.append(get_diff(times['message_in_db'],times['sms_sent_out_time']))
        line = line + 1

    statistic_for("Time that individual messages take to be sent out", time_diff_msg_db_to_send_out)


def between(date, ini, end):
    return date<end and date > ini

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


def get_sent_out_time(message_id):
    #  2014-03-03 16:00:03,597 [command] INFO: SMS[50751122] SENT
    command_to_get_time = "grep -i %s send_individuals.txt" % message_id
    result = execute_command(command_to_get_time)
    result_time = re.search("(.*) \[command\] INFO: SMS(.*)", result, re.IGNORECASE)
    result_time = result_time.group(1)

    time = datetime.strptime(result_time, "%Y-%m-%d %H:%M:%S,%f")
    return time


def getting_times_for_line(line):
    command_to_get_message_id = "head -n %d individual_messages_dates.txt | tail -1" % line
    result = execute_command(command_to_get_message_id)
    result_data= result.split('|')

    message_id = result_data[0].strip()
    connection_id = result_data[1].strip()
    date = result_data[2].strip().split('+')[0]

    times = {}
    times['message_in_db']=datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    times['sms_sent_out_time'] = get_sent_out_time(message_id)
    return times

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

run_test()