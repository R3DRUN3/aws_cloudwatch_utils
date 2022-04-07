"""This module contains utilities to interact with aws CloudWatch APIs"""

import random
import time
import boto3
import datetime

def create_log_group(log_group_name='log_group_test', retention_days=30, tags={'Type': 'Back end', 'Environment': 'Production','RetentionPeriod': '0'}):
    '''
    Creates a new CloudWatch log group.

            Parameters:
                    log_group_name (string): <default = test_group> log group name.

                    retention_days (int): <default = 30> log max retention days.

                    tags (dict): <default = {'Type': 'Back end', 'Environment': 'Production','RetentionPeriod': retention_days}> Optional metadata tags that you assign to a log group.
            Returns:
                    results (dict): results dictionary 
    '''
    results = {
        "operation_status": "ok",
        "resultset": ""
    }
    try: 
        client = boto3.client('logs')     
        tags['RetentionPeriod']=str(retention_days)
        response = client.create_log_group(
        logGroupName=log_group_name,
        tags=tags
        )
        results['resultset'] = response
        response = client.put_retention_policy(
          logGroupName=log_group_name,
          retentionInDays=retention_days
        )
        results['resultset'] = response
    except Exception as ex:
        results['operation_status'] = ex
    return results


def list_log_groups(group_name_filter=''):
    '''
    List all CloudWatch log groups for current region.

            Parameters:
                    group_name_filter (string): <default = ''> filter log group by name.
            Returns:
                    results (dict): results dictionary 
    '''
    results = {
        "operation_status": "ok",
        "resultset": ""
    }
    try:   
        client = boto3.client('logs')
        response = []
        if(group_name_filter != ''):   
            response = client.describe_log_groups(
                logGroupNamePrefix=group_name_filter
            )
        else:
            response = client.describe_log_groups()
        results['resultset'] = response['logGroups']
    except Exception as ex:
        results['operation_status'] = ex
    return results

def create_log_stream(log_stream_name='log_stream_test', log_group_name='log_group_test'):
    '''
    Create a new log stream.

            Parameters:
                    log_stream_name (string): <default = 'log_stream_test'> Name of the log stream.
                    log_group_name (string): <default = 'log_group_test'> Name of the log group.
            Returns:
                    results (dict): results dictionary 
    '''
    results = {
        "operation_status": "ok",
        "resultset": ""
    }
    try:   
        client = boto3.client('logs')
        response = client.create_log_stream(
        logGroupName = log_group_name,
        logStreamName = log_stream_name
        )
        results['resultset'] = response
    except Exception as ex:
        results['operation_status'] = ex
    return results

def list_log_streams(stream_name_filter='', log_group_name = 'log_group_test'):
    '''
    List all CloudWatch log streams for current region.

            Parameters:
                    stream_name_filter (string): <default = '> filter log stream by name.
            Returns:
                    results (dict): results dictionary 
    '''
    results = {
        "operation_status": "ok",
        "resultset": ""
    }
    try:   
        client = boto3.client('logs')
        response = []
        if(stream_name_filter != ''):   
            response = client.describe_log_streams(
                logGroupName = log_group_name,
                logStreamNamePrefix=stream_name_filter
            )
        else:
            response = client.describe_log_streams(logGroupName = log_group_name)
        results['resultset'] = response['logStreams']
    except Exception as ex:
        results['operation_status'] = ex
    return results



def publish_log_event(log_stream_name='log_stream_test', log_group_name='log_group_test',
                     message = 'Hello Log!', token =''):
    '''
    Publish new log event to a Group/Stream Tuple

            Parameters:
                    log_stream_name (string): <default = 'log_stream_test'> Name of the log stream.
                    log_group_name (string): <default = 'log_group_test'> Name of the log group.
                    message (string): <default = Hello Log!> Log body message.
                    token (string): <default = ''> You need a token for Publish log to a Stream more than one time
            Returns:
                    results (dict): results dictionary 
    '''
    results = {
        "operation_status": "ok",
        "resultset": ""
    }
    try: 
        response = None
        client = boto3.client('logs')
        log_events = [
            {
                'timestamp': int(round(time.time() * 1000)), 
                'message': message
            }
        ]
        if(token != ''):  
            response = client.put_log_events(
            logGroupName = log_group_name,
            logStreamName = log_stream_name,
            logEvents = log_events,
            sequenceToken = token
            )
        else:
            response = client.put_log_events(
            logGroupName = log_group_name,
            logStreamName = log_stream_name,
            logEvents = log_events
            )
        results['resultset'] = response
    except Exception as ex:
        try: 
            next_token = ex.response['expectedSequenceToken']
            client = boto3.client('logs')
            log_events = [
                {
                    'timestamp': int(round(time.time() * 1000)), 
                    'message': message
                }
            ]
            response = client.put_log_events(
            logGroupName = log_group_name,
            logStreamName = log_stream_name,
            logEvents = log_events,
            sequenceToken=next_token,
            )
            results['resultset'] = response
            return results
        except Exception as ex2:
            results['operation_status'] = ex2
        results['operation_status'] = ex
    return results

def get_log_events(log_stream_name='log_stream_test', log_group_name='log_group_test',
                   start_time = int(datetime.datetime(2022, 1, 1, 0, 0).strftime('%s'))*1000, 
                   end_time = int(datetime.datetime(2023, 1, 1, 0, 0).strftime('%s'))*1000,
                   max_log=100, start_from_head = True):
    '''
    Get log events from CloudWatch

            Parameters:
                    log_stream_name (string): <default = 'log_stream_test'> Name of the log stream.
                    log_group_name (string): <default = 'log_group_test'> Name of the log group.
                    start_time (int): <default = int(datetime.datetime(2022, 1, 1, 0, 0).strftime('%s'))*1000> Start Time
                    end_time (int): <default = int(datetime.datetime(2023, 1, 1, 0, 0).strftime('%s'))*1000> End Time
                    max_log (int): <default = 100> Max log to retrieve
                    start_from_head (bool): <default = True> Order by Datetime desc
            Returns:
                    results (dict): results dictionary 
    '''
    results = {
        "operation_status": "ok",
        "resultset": ""
    }
    try:   
        client = boto3.client('logs')
        response = client.get_log_events(
        logGroupName=log_group_name,
        logStreamName=log_stream_name,
        startTime=start_time,
        endTime=end_time,
        limit=max_log,
        startFromHead=start_from_head
        )
        results['resultset'] = response['events']
    except Exception as ex:
        results['operation_status'] = ex
    return results

def delete_log_group(log_group_name='log_group_test'):
    '''
    Delete CloudWatch log group

            Parameters:
                    log_group_name (string): <default = 'log_group_test'> Name of the log group to delete.
            Returns:
                    results (dict): results dictionary 
    '''
    results = {
        "operation_status": "ok",
        "resultset": ""
    }
    try:   
        client = boto3.client('logs')
        response = client.delete_log_group(
        logGroupName=log_group_name
        )
        results['resultset'] = response
    except Exception as ex:
        results['operation_status'] = ex
    return results

def publish_metric(metric_namespace='test_metrics', metric_data=
[
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
]):
    '''
     Publish a CloudWatch metric

            Parameters:
                    metric_namespace (string): <default = 'test_metrics'> Metric namespace
                    metric_data (list<dict>): <default = '[{'MetricName': 'cpu_load_test_metric','Dimensions': [{'Name': 'test_probe','Value': 'Ubuntu22.04'}],'Value': random.randint(1, 99),'Unit': 'Count'}]'> Metric Dto.
            Returns:
                    results (dict): results dictionary 
    '''
    results = {
        "operation_status": "ok",
        "resultset": ""
    }
    try:   
        client = boto3.client('cloudwatch')
        response = client.put_metric_data(
        Namespace=metric_namespace,
        MetricData=metric_data    
        )
        results['resultset'] = response
    except Exception as ex:
        results['operation_status'] = ex
    return results

def list_metric(filter_metric_namespace=''):
    '''
     Get CloudWatch metrics list

            Parameters:
                    filter_metric_namespace (string): <default = ''> Filter metric by namespace name
            Returns:
                    results (dict): results dictionary 
    '''
    results = {
        "operation_status": "ok",
        "resultset": ""
    }
    try:   
        response = None
        client = boto3.client('cloudwatch')
        if(filter_metric_namespace !=''):
            response = client.list_metrics(
                Namespace=filter_metric_namespace
            )
        else:
            response = client.list_metrics()
        results['resultset'] = response['Metrics']
    except Exception as ex:
        results['operation_status'] = ex
    return results




    