import os
import sys
from functools import partial

from data_process.io_yaml import read_yaml
from . import CronTab
from .worker import run_command
from .log import logger


def prepare_dir(path):
    if not path.endswith("/"):
        path = os.path.dirname(path)

    if not os.path.isdir(path):
        os.makedirs(path)


def write_log(path, line):
    if not line or not line.strip():
        return
    prepare_dir(path)
    with open(path, "w") as f:
        f.write(line)


def expand_user_vars(text, user=True, variable=True):
    if not text:
        return text
    if user:
        text = os.path.expanduser(text)
    if variable:
        text = os.path.expandvars(text)
    return text


def run_command_and_write_log(
    command,
    stdout_path=None,
    stderr_path=None,
    redirect_stderr=False,
    cwd=None,
    env=None,
):
    return_code, stdout, stderr = run_command(
        command, redirect_stderr=redirect_stderr, cwd=cwd, environment=env
    )
    logger.info(
        f'[command "{command}"] return code result:\nreturn code: {return_code}\nstdout: {stdout}\nstderr: {stderr}'
    )

    if stdout_path:
        write_log(stdout_path, stdout)
    if stderr_path:
        write_log(stderr_path, stderr)


def parse_configs_and_run(path):
    configs = read_yaml(path)
    logger.debug(f"got crontab configs: {configs}")

    tab = CronTab()
    for cfg in configs:
        cfg["command"] = expand_user_vars(cfg["command"])
        cfg["directory"] = expand_user_vars(cfg["directory"])
        cfg["arguments"] = [expand_user_vars(x) for x in cfg.get("arguments", [])]
        cfg["stdout_logfile"] = expand_user_vars(cfg.get("stdout_logfile"))
        cfg["stderr_logfile"] = expand_user_vars(cfg.get("stderr_logfile"))

        try:
            cmd = [cfg["command"]] + cfg["arguments"]
            kwargs = dict(
                stdout_path=cfg["stdout_logfile"],
                stderr_path=cfg["stderr_logfile"],
                redirect_stderr=cfg.get("redirect_stderr"),
                cwd=cfg["directory"],
                env=cfg.get("environment"),
            )

            event = tab.add_task(
                cfg["name"],
                cfg["cron"],
                run_command_and_write_log,
                args=(cmd,),
                kwargs=kwargs,
            )
        except KeyError as key:
            logger.error(f"{key} is a required config")
            sys.exit(1)
        logger.info(f"added job {event.job}")

    tab.run()
