#!/usr/bin/env python3

# Copyright 2020 Jerry Ibrahim
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import sys
import uuid
import requests
import threading
import time
import queue


q = queue.Queue()
verbose = False

def get_url(url, count):
	iterations = [0, 0]
	for i in range(count):
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'ThreadID': str(uuid.uuid4())
		}
		try:
			r = requests.get(url, headers=headers)
			if verbose:
				print(r.content)

			# Success Count
			if (r.status_code == requests.codes.ok):
				iterations[0] = iterations[0] + 1

		except Exception as ex:
			if verbose:
				print("Can not connect: %s" % (url) )

		# Total count
		iterations[1] = iterations[1] + 1

	q.put(iterations)


def defaults(i, t, d):
	if (t == "int"):
		r = d
		try:
			r = int(i)
		except Exception as ex:
			r = d
		return r

	elif (t == "bool"):
		r = d
		if (i.lower() == "true"):
			r = True
		elif (i.lower() == "false"):
			r = False
		return r

	return 0

def printUsage():
	print("usage:")
	print("perfTest <loops> <threads> <URL_INDEX> [verbose=(true | false)]")

if __name__ == "__main__":

	URL = []
	URL.append('http://google.com/')
	URL.append('http://localhost/')
	URL.append('http://localhost:8080/dnextid?k=PID')
	URL.append('https://jerry-kv.herokuapp.com/dnextid?k=PID')
	URL.append('https://jerry-kv-eu.herokuapp.com/dnextid?k=PID')
	URL.append('https://jerry-green.herokuapp.com/color')
	URL.append('https://jerry-green.herokuapp.com/size?k=1')
	URL.append('https://jerry-green.herokuapp.com/time?k=1')


	if (len(sys.argv) < 4):
		printUsage()
		sys.exit()
	elif(len(sys.argv) == 4):
		verbose = False
	else:
		verbose = defaults(sys.argv[4], "bool", False)


	loop_count = defaults(sys.argv[1], "int", 0)
	thread_count = defaults(sys.argv[2], "int", 0)
	urlIndex = defaults(sys.argv[3], "int", 0)

	urlTarget = URL[urlIndex]

	print("Iterations: {:,d}".format(loop_count))
	print("Threads: {:,d}".format(thread_count))
	print("URL: {:s}\n".format(urlTarget))

	t = []

	startTime = time.time()

	# create and start all threads
	for i in range(thread_count):
		# print("Starting Thread: %d" % (i))
		thread = threading.Thread(target=get_url, args=(urlTarget, loop_count,))
		t.append(thread)
		thread.start()

	# wait for all threads to finish
	for i in t:
		i.join()

	goodRuns = 0
	totalRuns = 0
	while not q.empty():
		iteration = q.get()
		goodRuns = goodRuns + iteration[0]
		totalRuns = totalRuns + iteration[1]


	# Calculate the total execution time
	endTime = time.time()
	totalTime = endTime - startTime

	# output
	print("\nTotal:\t{:,d}".format(totalRuns))
	print("Good:\t{:,d}".format(goodRuns))
	print("Bad:\t{:,d}".format(totalRuns - goodRuns))

	print("\nTime:\t{:,.3f}".format(totalTime))
	print("RPS:\t{:,.3f}".format(goodRuns / totalTime))

