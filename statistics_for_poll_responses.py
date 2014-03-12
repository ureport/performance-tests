from datetime import datetime
from statistic_helper import get_time_from_result, execute_command, get_diff, statistic_for

def run_test():
    """"
    psql -h localhost -U postgres -d ureport -c "select r1.message_id, m1.date, r1.id, r1.date, c1.identity
    from rapidsms_httprouter_message AS m1, poll_response AS r1, rapidsms_connection AS c1
    where m1.id=r1.message_id and m1.connection_id = c1.id and r1. poll_id=$POLL_ID
    and r1.id>$FIRST_RESPONSE and r1.id<$LAST_RESPONSE and
    m1.connection_id not in
    (select  m.connection_id from rapidsms_httprouter_message AS m, poll_response AS r
    where m.id=r.message_id and r. poll_id=$POLL_ID and r.id>$FIRST_RESPONSE and r.id<$LAST_RESPONSE
    group by m.connection_id having count(m.connection_id) >1);" > data_for_responses_to_a_national_poll.txt
    """""
    ini = 3
    limit = 33
    list_throttle_msg_db = []
    list_throttle_response_db = []
    list_throttle_end = []
    list_response_end = []

    with open('data_for_responses_to_a_national_poll.txt') as response_data:
        for index, line in enumerate(response_data):
            if index >= ini :
                times = getting_times_for_line(line)
                list_throttle_msg_db.append(get_diff(times['throttle_start'],times['message_in_db']))
                list_throttle_response_db.append(get_diff(times['throttle_start'],times['response_in_db']))
                if times['response_finish_handled'] is not None:
                    list_throttle_end.append(get_diff(times['throttle_start'],times['response_finish_handled']))
                    list_response_end.append(get_diff(times['response_in_db'],times['response_finish_handled']))
            #if index == limit:
            #    break


    statistic_for("Throttle send to router receive until msg is store in db:", list_throttle_msg_db)
    statistic_for("Throttle send to router receive until response is store in db:", list_throttle_response_db)
    statistic_for("Throttle send to router receive until response get categorized:", list_throttle_end)
    statistic_for("Since Response is created until its Categorization:", list_response_end)

def get_throttle_time(phone_number):
    command_to_get_time = "grep -i send_directly_to_router.*%s throttle*" % phone_number
    result = execute_command(command_to_get_time)
    regex = "throttle\.log\.?([1-9])?:\[(.*): INFO\/Worker-[0-9]?\] throttle.tasks.send_directly_to_router(.*) "
    time_format = "%Y-%m-%d %H:%M:%S,%f"
    return get_time_from_result(result, regex, 2, time_format)

def get_start_handling_time(phone_number):
    path_to_ureport_app_log = "./ureport_app_logs"
    command_to_get_time = "grep -i %s %s/ureport_application* | head -n 1 " % (phone_number, path_to_ureport_app_log)
    result = execute_command(command_to_get_time)
    regex = "\.\/ureport_app_logs\/ureport_application\.log\.?[0-9]?[0-9]?:(.*) DEBUG(.*)"
    format_time = "%Y-%m-%d %H:%M:%S,%f"
    return get_time_from_result(result, regex, 1, format_time)

def get_response_finish_to_be_handled_time(response_id):
    path_to_ureport_app_log = "./ureport_app_logs"
    command_to_get_time = "grep -i %s %s/ureport_application*" % (response_id, path_to_ureport_app_log)
    result = execute_command(command_to_get_time)
    regex = "ureport_application\.log\.?[0-9]?[0-9]?:(.*) DEBUG(.*)"
    format_time = "%Y-%m-%d %H:%M:%S,%f"
    return get_time_from_result(result, regex, 1, format_time)


def getting_times_for_line(line):
    data = line.split("|")
    message_db = datetime.strptime(data[1].strip().split('+')[0],"%Y-%m-%d %H:%M:%S.%f")
    response_id = data[2].strip()
    response_db = datetime.strptime(data[3].strip().split('+')[0],"%Y-%m-%d %H:%M:%S.%f")
    phone_number = data[4].strip()


    message_sent_by_throttle_time = get_throttle_time(phone_number)
    response_handled_time = get_response_finish_to_be_handled_time(response_id)

    times = {
        'message_in_db' : message_db,
        'response_in_db' : response_db,
        'throttle_start' : message_sent_by_throttle_time,
        'response_finish_handled' : response_handled_time
    }

    return times

run_test()