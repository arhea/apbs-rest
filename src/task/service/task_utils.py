from flask import request
import os, time, sys
import requests
try:
    from simplejson import loads, dumps
except:
    from json import loads, dumps

EXEC_PROXY_HOST = os.getenv('TMP_EXEC_HOST', 'http://localhost:5005')
STORAGE_HOST = os.environ.get('STORAGE_HOST', 'http://localhost:5001')
STORAGE_URL  = os.environ.get('STORAGE_URL' , 'http://localhost:5001/api/storage')

END_STATES = ['complete', 'error']

class TaskHandler:
    def __init__(self):
        pass
    
    def get(self, job_id, task_name):
        if task_name in ['apbs', 'pdb2pqr']:
            progress   = None
            run_state  = None
            start_time = None
            end_time   = None
            input_files  = []
            output_files = []
            response   = {}
            wait_on_task = False

            if 'wait' in request.args.keys():
                if request.args['wait'].lower() == 'true':
                    # return {'args': request.args['wait']}
                    wait_on_task = True

            """
            # NOTE: can later optimize to only get end_time if state isn't 'running'
            start_time   = get_starttime(job_id, task_name)
            end_time     = get_endtime(job_id, task_name)
            run_state, progress = get_jobstatus_info(job_id, task_name)
            input_files  = get_input_files(job_id, task_name)
            output_files = get_output_files(job_id, task_name)
            """

            """
            if run_state not in END_STATES and wait_on_task:
                while run_state not in END_STATES:
                    time.sleep(1)
                    run_state = get_jobstatus_state(job_id, task_name)
                start_time   = get_starttime(job_id, task_name)
                end_time     = get_endtime(job_id, task_name)
                run_state, progress = get_jobstatus_info(job_id, task_name)
                input_files  = get_input_files(job_id, task_name)
                output_files = get_output_files(job_id, task_name)
            """

            # TODO: Get state, starttime, endtime, subtask details from Proxy service
            run_state, start_time, end_time, subtask_states = get_cluster_job_info(job_id, task_name)
            _, progress  = get_jobstatus_info(job_id, task_name)
            input_files  = get_input_files(job_id, task_name)
            output_files = get_output_files(job_id, task_name)
            # If run_state, is complete, check if *_exit_code.txt exists
            #   If exists and exit code != 0, run_state = 'failed'
            if run_state == 'complete':
                task_exit_code = get_subtask_exit_code(job_id, task_name, 'download')
                print('task_exit_code:',task_exit_code)
                if task_exit_code is not None and task_exit_code != 0:
                    run_state = 'failed'
                # else:
                #     task_exit_code = get_subtask_exit_code(job_id, task_name, 'exec')
                #     if task_exit_code is not None and task_exit_code != 0:
                #         run_state = 'failed'
                #     else:
                #         task_exit_code = get_subtask_exit_code(job_id, task_name, 'upload')
                #         if task_exit_code is not None and task_exit_code != 0:
                #             run_state = 'failed'

            response['jobid'] = job_id
            response['jobtype'] = task_name
            if run_state is None:
                response['error'] = 'Task does not exist'
                
            response[task_name] = {
                'status':      run_state,
                'files':       progress,
                'inputFiles':  input_files,
                'outputFiles': output_files,
                'startTime':   start_time,
                'endTime':     end_time,
                'subtasks':    subtask_states
            }

            http_status = 200
            # return response, 200
        else:
            response = {
                'status': None,
                'error': f"task type '{task_name}' does not exist or is not implemented"
            }
            http_status = 404
            # return response, 404

        return response, http_status        

    def post(self, job_id, task_name):
        user_headers = {
            'User-Agent': request.headers['User-Agent'],
            'X-Forwarded-For': request.headers['X-Forwarded-For']
        }
        if 'X-APBS-Client-ID' in request.headers:
            user_headers['X-APBS-Client-ID'] = request.headers['X-APBS-Client-ID']

        available_tasks = ['apbs', 'pdb2pqr']
        http_status = 202

        if task_name not in available_tasks:
            http_status = 400
            response = { 
                'error': 'invalid task'
            }
        else:

            '''
                Handler for using the TESK service.
                TODO: provide better checks for status codes/errors
            '''
            if task_name == 'apbs':
                # If 'infile' is in query-string and has value of true, proceed
                #     assuming the user intends to use an APBS input file
                if 'infile' in request.args.to_dict() and request.args['infile'].lower() == 'true':
                    data = request.get_json()
                    if 'filename' in data:
                        post_response = requests.post('%s/api/tesk/%s/%s?infile=true' % (EXEC_PROXY_HOST, job_id, task_name), json=data, headers=user_headers)
                        if post_response.status_code == 400:
                            http_status = post_response.status_code
                            response = post_response.json() # could probably just access/pass along raw data
                        elif post_response.status_code == 500:
                            http_status = post_response.status_code
                            response = post_response.json()
                    else:
                        '''Construct error response'''
                        http_status = 400
                        response = {
                            'error': "missing key 'filename' in JSON request"
                        }

                else:
                    form = request.get_json()
                    for key in list(form.keys()):
                        # unravels output parameters from form
                        if key == 'output_scalar':
                            for option in form[key]:
                                form[option] = option
                            form.pop('output_scalar')
                        else:
                            form[key] = str(form[key])

                    # Send task to placeholder executor service
                    post_response = requests.post('%s/api/tesk/%s/%s' % (EXEC_PROXY_HOST, job_id, task_name), json=form, headers=user_headers)
                    if post_response.status_code == 400:
                        http_status = post_response.status_code
                        response = post_response.json() # could probably just access/pass along raw data
                    elif post_response.status_code == 500:
                        http_status = post_response.status_code
                        response = post_response.json()


            elif task_name == 'pdb2pqr':
                form = request.get_json()
                # Send task to placeholder executor service
                print('%s/api/tesk/%s/%s' % (EXEC_PROXY_HOST, job_id, task_name))
                post_response = requests.post('%s/api/tesk/%s/%s' % (EXEC_PROXY_HOST, job_id, task_name), json=form, headers=user_headers)
                if post_response.status_code == 400 or post_response.status_code == 500:
                    http_status = post_response.status_code
                    response = post_response.json()
                print('tesk proxy response', post_response.status_code)
                

            # if http_status == 202:
            if 200 <= http_status < 300:
                response = { 
                    'accepted': f'task {task_name} accepted. Processing...'
                }

        return response, http_status

def get_starttime(jobid, task_name):
    """Returns the start time for the specified job id and type"""
    starttime = None

    object_name = '%s/%s_start_time' % (jobid, task_name)
    # starttime_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    starttime_url = '%s/%s?json=true' % (STORAGE_URL, object_name)
    response = requests.get( starttime_url )
    if response.status_code == 200:
        status_str = response.content
        # print(status_str)
        status_str = loads(status_str)[object_name]
        if status_str is not None:
            starttime = float(status_str.split('\n')[0].strip())
        else:
            print(status_str)
    else:
        print('    Start time retrieval status code: %d' % response.status_code, flush=True)
        print('    response content: %s' % response.content, flush=True)

    return starttime

def get_endtime(jobid, task_name):
    """Returns the end time for the specified job id and type"""
    endtime = None

    object_name = '%s/%s_end_time' % (jobid, task_name)
    # endtime_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    endtime_url = '%s/%s?json=true' % (STORAGE_URL, object_name)
    response = requests.get( endtime_url )
    if response.status_code == 200 and get_jobstatus_state(jobid, task_name) in END_STATES:
        status_str = response.content
        status_str = loads(status_str)[object_name]
        if status_str is not None:
            endtime = float(status_str.split('\n')[0].strip())
        else:
            print(status_str)

    elif response.status_code == 404:
        print('    %s job still running' % jobid)
    else:
        print('    Error in retrieving endtime. Investigate.', flush=True)
        print('    Status code: %d' % (response.status_code), flush=True)
        print('    response: %s' % (response.content), flush=True)

    return endtime

def get_input_files(jobid, task_name):
    input_files = []

    object_name = '%s/%s_input_files' % (jobid, task_name)
    # inputfile_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    inputfile_url = '%s/%s?json=true' % (STORAGE_URL, object_name)
    response = requests.get( inputfile_url )

    if response.status_code == 200:
        obj_content = loads(response.content)[object_name]
        input_files = obj_content.split()
    
    return input_files


def get_output_files(jobid, task_name):
    output_files = []

    object_name = '%s/%s_output_files' % (jobid, task_name)
    # outputfile_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    outputfile_url = '%s/%s?json=true' % (STORAGE_URL, object_name)
    response = requests.get( outputfile_url )

    if response.status_code == 200:
        obj_content = loads(response.content)[object_name]
        output_files = obj_content.split()
    
    return output_files

def get_jobstatus_state(jobid, task_name):
    job_status = None

    object_name = '%s/%s_status' % (jobid, task_name)
    # status_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    status_url = '%s/%s?json=true' % (STORAGE_URL, object_name)
    response = requests.get( status_url )
    if response.status_code == 200:
        status_str = response.content
        status_str = loads(status_str)[object_name]
        if status_str is not None:
            job_status = status_str.split('\n')[0].strip()
        else:
            print(status_str)



    return job_status


def get_jobstatus_info(jobid, task_name):
    """Returns the status and potential output files for the specified job id and type"""
    job_status = None
    job_progress = []

    object_name = '%s/%s_status' % (jobid, task_name)
    # status_url = '%s/api/storage/%s?json=true' % (STORAGE_HOST, object_name)
    status_url = '%s/%s?json=true' % (STORAGE_URL, object_name)
    # print('status_url: \n    %s'%status_url)
    response = requests.get( status_url )
    if response.status_code == 200:
        status_str = response.content
        status_str = loads(status_str)[object_name]
        if status_str is not None:
            job_status_text = status_str.split('\n')
            job_status = job_status_text[0]
            for line in job_status_text[1:]:
                line_stripped = line.strip()
                if len(line_stripped) > 0:
                    # print('name: '+line.strip())
                    # print(len(line))
                    job_progress.append(line.strip())
        else:
            print(status_str)

        # Converts the retrieved files to URL-friendly versions
        for i in range(len(job_progress)):
            filename = job_progress[i].split('/')[-1]
            job_progress[i] = '%s/%s' % (jobid, filename)
    
    return job_status, job_progress

def get_cluster_job_info(job_id: str, task_name: str):
    # Return: 
    response = requests.get('%s/api/tesk/%s/%s' % (EXEC_PROXY_HOST, job_id, task_name))
    data = response.json()
    if response.ok:
        state = data['status']
        start_time = data['startTime']
        end_time = data['endTime']
        subtask_states = data['taskStatus']
        # subtask_states = []
        # for subtask in data['taskStatus']:
        #     subtask_states.append()

    elif response.status_code == 404:
        state = None
        start_time = None
        end_time = None
        subtask_states = None

    else:
        response.raise_for_status()

    return state, start_time, end_time, subtask_states

def get_subtask_exit_code(job_id: str, task_name: str, step_name: str) -> int:
    exit_code = None
    exit_code_filename = '%s_%s_exit_code.txt' % (task_name, step_name)
    # exit_code_response = requests.get('%s/%s/%s_end_time?json=true' % (STORAGE_URL, job_id, task_name))
    exit_code_response = requests.get('%s/%s/%s?json=true' % (STORAGE_URL, job_id, exit_code_filename))
    if exit_code_response.ok:
        data = exit_code_response.json()
        object_name = '%s/%s' % (job_id, exit_code_filename)
        exit_code = int( data[object_name].strip() )
        # if task_exit_code != 0:
        #     run_state = 'failed'
    # else:
    #     print( 'Could not find', exit_code_filename )

    return exit_code