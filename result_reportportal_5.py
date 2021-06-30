import os
import time
import json
import random
import subprocess
import traceback
import urllib3
from mimetypes import guess_type

from reportportal_client import ReportPortalService

def timestamp():
    return str(int(time.time() * 1000))

endpoint = "https://reportportal-rhv.apps.ocp4.prod.psi.redhat.com"
# project = "yaniwang_personal"
project = "weiwang_personal"
### The next two parameters need to be modified along your testing. ###
token = "bc9fa790-c960-47e5-b34d-15963ea6d58d"
data_file_path = "./../he_tier2_firefox.json"

def get_parameters_result_data():
    # need to create a function for getting result file path automatically
    data_file = open(data_file_path, "rb")
    return json.load(data_file)

def get_launch_info():
    split_title_name = get_parameters_result_data()["title"].split('-')
    launch_name_list = split_title_name[0:3]
    launch_name_list.append(split_title_name[5])

    tag_str = split_title_name[-1].split('_')
    decription_launch = tag_str[-3]
    tag1_launch = tag_str[-2]
    tag2_launch = tag_str[-1]
    return ['-'.join(launch_name_list), decription_launch, tag1_launch, tag2_launch]

def get_suite_info():
    split_title_name = get_parameters_result_data()["title"].split('_')
    tag_suite = split_title_name[1]
    return ["hp-dl388g9-05",tag_suite]

launch_name = get_launch_info()[0] + "_" + get_launch_info()[2] + "_" + get_launch_info()[3]
suite_name = get_suite_info()[0] + "_" + get_suite_info()[1]
launch_doc = "Testing " + get_launch_info()[1]

def my_error_handler(exc_info):
    """
    This callback function will be called by async service client when error occurs.
    Return True if error is not critical and you want to continue work.
    :param exc_info: result of sys.exc_info() -> (type, value, traceback)
    :return:
    """
    print("Error occurred: {}".format(exc_info[1]))
    traceback.print_exception(*exc_info)

def main():
    urllib3.disable_warnings()
    service = ReportPortalService(endpoint=endpoint, project=project,
                                  token=token, verify_ssl=False)

    # Start launch.
    launch = service.start_launch(name=launch_name,
                                  start_time=timestamp(),
                                  description=launch_doc)

    suite_id = service.start_test_item(name=suite_name,
                                   description="",
                                   start_time=timestamp(),
                                   item_type="SUITE",
                                   parameters={"suite":"Tier1"})

    for key,value in get_parameters_result_data()["results"].items():
        # Start test item Report Portal.
        test_id = service.start_test_item(name=key,
                                       description="",
                                       start_time=timestamp(),
                                       parent_item_id = suite_id,
                                       item_type="test",
                                       parameters={key:value})

        time.sleep(1.5*3600*1000 + random.randint(1,9) * 0.1)

        # Finish test item Report Portal.
        service.finish_test_item(item_id=test_id,end_time=timestamp(), status="PASSED")

    service.finish_test_item(item_id=suite_id, end_time=timestamp(), status="PASSED")
    # Finish launch.
    service.finish_launch(end_time=timestamp())

    # Due to async nature of the service we need to call terminate() method which
    # ensures all pending requests to server are processed.
    # Failure to call terminate() may result in lost data.
    service.terminate()

if __name__ == '__main__':
    main()