#!/usr/bin/env python
# coding=utf-8
#
# Copyright © 2015-2016 VMware, Inc. All Rights Reserved.
#
# Licensed under the X11 (MIT) (the “License”) set forth below;
#
# you may not use this file except in compliance with the License. Unless required by applicable law or agreed to in
# writing, software distributed under the License is distributed on an “AS IS” BASIS, without warranties or conditions
# of any kind, EITHER EXPRESS OR IMPLIED. See the License for the specific language governing permissions and
# limitations under the License. Permission is hereby granted, free of charge, to any person obtaining a copy of this
# software and associated documentation files (the "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# "THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
# AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.”

from flask import Flask, render_template, request, Response
import commands
import netifaces
import socket
from netaddr import IPNetwork

__author__ = 'yfauser'

app = Flask(__name__)
HOSTNAME = commands.getoutput("hostname")


def host_scan(host, start_port, end_port):
    open_ports = []
    for port in range(start_port, end_port):
        try:
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.settimeout(0.01)
            tcp_socket.connect((host, port))
            tcp_socket.close()
            open_ports.append(port)
        except (socket.timeout, socket.error) as e:
            tcp_socket.close()

    return open_ports


def ping_host(host):
    return commands.getoutput('ping -c5 {}'.format(host))


PING_HOST = '10.114.209.73'
PING_RESULT = ping_host(PING_HOST)


def get_ip():
    for iface in netifaces.interfaces():
        if iface in ['nsx0', 'eth0', 'en5']:
            return netifaces.ifaddresses(iface)[netifaces.AF_INET][0]['addr']

IP = get_ip()


@app.route("/")
@app.route("/index")
def hello():

    host = {'hostname': HOSTNAME, 'ip': IP}
    return render_template('index.html', title='Home', host=host)

@app.route("/scan")
def port_scan():
    return render_template("port-scan.html")


@app.route("/scan", methods=['POST'])
def port_scan_post():

    network = request.form.get('network')
    host_range = IPNetwork(network).iter_hosts()
    start_port = int(request.form.get('start_port'))
    end_port = int(request.form.get('end_port'))

    def scan_hosts():
        scan_result = []
        for host in host_range:
            host_result = host_scan(str(host), start_port, end_port)
            scan_result.append({'host_ip': str(host), 'open_ports': host_result})
            yield 'Scan of Host: {}, open ports: {} \n\n'.format(host, host_result)

    return Response(scan_hosts(), mimetype= 'text/event-stream',
                    headers={'Cache-Control': 'no-cache, no-store, must-revalidate'})


@app.route("/debug")
def debug_get():
    output = 'Result of startup Ping:\n\n {}'.format(PING_RESULT)

    return Response(output, mimetype='text')


if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=False, threaded=True, port=80)
