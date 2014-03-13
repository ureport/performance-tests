
from datetime import datetime
from statistic_helper import not_empty, execute_command, get_diff, statistic_for, get_time_from_result


def run_test():
    """"
    psql -h localhost -U postgres -d ureport -c
    "select m.id, m.date, m.connection_id, c.identity
    from rapidsms_httprouter_message AS m, rapidsms_connection AS c
    where m.connection_id=c.id and m.connection_id in ($CONNECTION_ID for unsolicited messages)" > data_for_unsolicited_msgs.txt;
    """""
    ini = 3
    time_diff_msg_receive_to_db = []

    with open('data_for_unsolicited_msgs.txt') as response_data:
        for index, line in enumerate(response_data):
            if index >= ini :
                times = getting_times_for(line)
                if(not_empty(times['message_in_db']) and not_empty(times['sms_received'])):
                    time_diff_msg_receive_to_db.append(get_diff(times['sms_received'],times['message_in_db']))

    statistic_for("Time that individual messages from yo to db", time_diff_msg_receive_to_db)


def get_receive_number_time(phone_number):
    """"
    The information is recollected from smsc.log. having log-level=0
    """""
    path_for_smsc_logs = "./yo_data_02_to_07"
    command_to_get_time = "grep %s %s/yo*" % (phone_number, path_for_smsc_logs)
    result = execute_command(command_to_get_time)
    regex = "yo1debug\.log\.?([0-9]|\_|[a-z])+:(.*) \[....\] \[.\] DEBUG:(.*)"
    format_time = "%Y-%m-%d %H:%M:%S"
    return get_time_from_result(result, regex, 2, format_time)


def getting_times_for(line):
    data= line.split('|')

    date = data[1].strip().split('+')[0]
    phone = data[3].strip()

    times = {}
    times['message_in_db'] = datetime.strptime(date, "%Y-%m-%d %H:%M:%S.%f")
    times['sms_received'] = get_receive_number_time(phone)
    print times
    return times

run_test()
