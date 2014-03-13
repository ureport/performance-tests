from datetime import datetime
from statistic_helper import execute_command, get_diff, statistic_for, get_time_from_result

def run_test():
    """
    We would need:
    1.- Filter individual messages from db -> get id, connection_id and date
    psql -U postgres -h localhost -d ureport -c "select id, connection_id, date
    from rapidsms_httprouter_message where direction='O' and
    id in ($MESSAGE_IDs THAT ARE NOT ASSOCIATED TO A POLL);" > individual_messages_dates.txt
    2.- Get send_message logs from the time that a big poll was sent out. E.g. messenger.log
    """
    ini = 3
    time_diff_msg_db_to_send_out = []

    with open('individual_messages_dates.txt') as response_data:
        for index, line in enumerate(response_data):
            if index >= ini:
                times = getting_times_for(line)
                time_diff_msg_db_to_send_out.append(get_diff(times['message_in_db'],times['sms_sent_out_time']))


    statistic_for("Time that individual messages take to be sent out", time_diff_msg_db_to_send_out)

def get_sent_out_time(message_id):
    #  2014-03-03 16:00:03,597 [command] INFO: SMS[$MESSAGE_ID] SENT
    command_to_get_time = "grep -i %s messenger.log*" % message_id
    result = execute_command(command_to_get_time)
    regex = "(.*) \[command\] INFO: SMS(.*)"
    format_time = "%Y-%m-%d %H:%M:%S,%f"
    return get_time_from_result(result, regex, 1, format_time)


def getting_times_for(line):
    data = line.split("|")

    message_id = data[0].strip()
    date = data[2].strip().split('+')[0]

    times = {}
    times['message_in_db'] = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    times['sms_sent_out_time'] = get_sent_out_time(message_id)
    return times

run_test()