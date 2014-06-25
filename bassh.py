#!/usr/bin/env python

"""
Execute bash script on a remote machine via SSH from the local machine
"""

__author__ = "Cam Wright"

from fabric.api import run, sudo, cd, put
from fabric.context_managers import settings, hide
import argparse, datetime, time, os, signal, sys

FAIL_STRING = "--- Failed to run"

parser = argparse.ArgumentParser(description="Run a script over SSH")
parser.add_argument("host",
		            help="The remote machine")
parser.add_argument("-e",
                    "--execute",
		            help="Execute an inline command",
					type=str)
parser.add_argument("-f",
		            "--file",
					help="Execute a bash file",
					type=str)
parser.add_argument("-p",
		            "--password",
					help="The password of the remote machine",
					type=str)
parser.add_argument("-o",
		            "--port",
					help="The remote port on which SSH is listening",
					type=str)
parser.add_argument("-s",
		            "--sudo",
					help="Run command with sudo",
					action="store_true")
parser.add_argument("-d",
		            "--directory",
					help="The remote directory to run the command",
					type=str)
args = parser.parse_args()

with settings(host_string=args.host,
		      password=args.password,
			  cwd=args.directory,
			  port=args.port,
			  warn_only=True):
	with hide("warnings", "running"):
		if args.execute:
			if args.sudo:
				if sudo(args.execute).failed:
					print FAIL_STRING, args.execute
					sys.exit(1)
			else:
				if run(args.execute).failed:
					print FAIL_STRING, args.execute
					sys.exit(1)

		if args.file:
			if not os.path.isfile(args.file): 
				print "Could not find file", args.file
				sys.exit(1)
			time_now = int(time.mktime(
				datetime.datetime.now().timetuple())
			)
			filename = '.bassh_tmp.{0}_{1}'.format(
					str(time_now),
					"_".join(args.file.split(".")))

			#: allow for graceful exit on Ctrl+C
			def signal_handler(sig, frame):
				print "\nCleaning Up..."
				run('rm ' + filename) #: remove the file
				sys.exit(1)
			signal.signal(signal.SIGINT, signal_handler)

			put(args.file, filename) #: upload the file
			run('sh ' + filename)    #: run the file 
			run('rm ' + filename)    #: remove the file

