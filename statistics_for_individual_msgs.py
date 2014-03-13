from datetime import datetime
from statistic_helper import execute_command, get_diff, statistic_for, get_time_from_result

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

def get_sent_out_time(message_id):
    #  2014-03-03 16:00:03,597 [command] INFO: SMS[50751122] SENT
    command_to_get_time = "grep -i %s send_individuals.txt" % message_id
    result = execute_command(command_to_get_time)
    regex = "(.*) \[command\] INFO: SMS(.*)"
    format_time = "%Y-%m-%d %H:%M:%S,%f"
    return get_time_from_result(result, regex, 1, format_time)


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

run_test()