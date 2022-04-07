import datetime
from datetime import datetime as dt
import random
import time as tm
import aws_cloudwatch_utils as acu

LOG_GROUP_NAME = 'log_group_test'
LOG_STREAM_NAME = 'log_stream_test'
TEST_METRIC_NAMESPACE = 'test_metrics'
TEST_METRIC_DATA = [
    {
        'MetricName': 'cpu_load_test_metric', 
        'Dimensions': 
        [
            {
                'Name': 'test_probe',
                'Value': 'Ubuntu22.04'
            }
        ],
        'Value': random.randint(1, 99),
        'Unit': 'Count'
    }
]


#Create New Log Group
print("Creating new log group...")
new_log_group_result = acu.create_log_group(LOG_GROUP_NAME)
print("New log group creation result: {} \n".format(new_log_group_result['operation_status']))

#List Existing Log Groups
print("List existing log groups...")
log_groups = acu.list_log_groups(LOG_GROUP_NAME) #leave without arguments to list ALL log groups in region
if log_groups['operation_status'] == 'ok':
   for group in log_groups['resultset']:
       print(group)
print("")


#Create New Log Stream
print("Create new log stream...")
new_log_stream_result = acu.create_log_stream(LOG_STREAM_NAME, LOG_GROUP_NAME)
print("New log stream creation result: {} \n".format(new_log_stream_result['operation_status']))

#List Existing Log Streams
tm.sleep(1)
print("List existing log streams...")
log_streams = acu.list_log_streams(LOG_STREAM_NAME) #leave without arguments to list ALL log streams in region
if log_streams['operation_status'] == 'ok':
   for stream in log_streams['resultset']:
       print(stream)
       try:
          stream_next_sequence_token = stream['uploadSequenceToken']
          print('Next Sequence Token for this stream is {}'.format(stream_next_sequence_token)) # IMPORTANT! YOU NEED THIS TOKEN TO PUBLISH MORE THAN ONE TIME TO A STREAM!!!
       except:
           pass
print("")

#Publish Default Log
print("Publish custom log...")
log_message ='{} - Published From Python !'.format(dt.now())
default_log_publish_result = acu.publish_log_event(LOG_STREAM_NAME, 
                                                   LOG_GROUP_NAME,
                                                   log_message)
print("Publish Custom log result: {} \n".format(default_log_publish_result['operation_status']))

#Get CloudWatch Log Events
tm.sleep(1)
print("Getting Log events...")
start_time = int(datetime.datetime(2022, 1, 1, 0, 0).strftime('%s'))*1000
end_time = int(datetime.datetime(2022, 5, 20, 0, 0).strftime('%s'))*1000
limit = 200
log_events = acu.get_log_events(LOG_STREAM_NAME, LOG_GROUP_NAME, 
                                start_time, end_time, limit)
if log_events['operation_status'] == 'ok':
   for log in log_events['resultset']:
       print(log)
print("")

#Delete Log group
print("Deleting log group...")
delete_result = acu.delete_log_group(LOG_GROUP_NAME)
print("Deleting operation result: {} \n".format(delete_result['operation_status']))

#Create New Metrics
print("Creating new metrics...")
for i in range (10):
    metric_creation_result = acu.publish_metric(TEST_METRIC_NAMESPACE, TEST_METRIC_DATA)
    print("Metric creation result: {} \n".format(metric_creation_result['operation_status']))
    tm.sleep(20)

#Get Metric List
print("List existing metrics...")
metric_list = acu.list_metric(TEST_METRIC_NAMESPACE)
if metric_list['operation_status'] == 'ok':
   for group in metric_list['resultset']:
       print(group)
print("")

