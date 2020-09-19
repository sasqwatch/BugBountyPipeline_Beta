import subprocess
import logging

logger = logging.getLogger('luigi-interface')


def execute_command_chain(command: str):
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = process.communicate()
    if output:
        return output.decode('utf8').split('\n')
    if errors:
        logger.error(f"Command Error: {errors}")
        raise Exception


def chain(command):
    return execute_command_chain(command)
