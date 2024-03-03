#!/usr/bin/env python

import xml.etree.cElementTree as et

from urllib.request import urlopen
from re import sub as re_sub

from .Output import message, info, debug, extra, error

def get_external_ip(verbosity=0):
    v = verbosity
    url = "http://checkip.dyndns.org"
    info(v, "Retreiving current external ip from %s" % url)

    # Open URL
    try:
        html_result = urlopen(url)
    except Exception as e:
        error("Url(%s) - %s" % (url, e))
        return None

    # Read result
    ip_bytes = html_result.read().strip()
    extra(v, "Full HTML Result: %s" % ip_bytes)
    ip_string = ip_bytes.decode("utf-8")

    # Parse out IP
    ip = None
    if ip_string is not None:
        regex = '^.*Current IP Address: ([0-9.]*).*$'
        ip = re_sub(regex, r'\1', ip_string)
        extra(v, "Retreived IP: %s" % ip)

    return ip



class Record:
    def __init__(self, record_dict=None):
        self.host = ''
        self.address = ''
        self.url = ''

        if record_dict is not None:
            self.initialize(record_dict)

    def updateKey(self):
        key = ''
        if self.url != '':
            # Use regex to extract update_key
            regex = r"^.*update.php\?([0-9A-Za-z=]*)$"
            key = re_sub(regex, r'\1', self.url)

        return key

    def initialize(self, record_dict):
        self.host = record_dict['host']
        self.address = record_dict['address']
        self.url = record_dict['url']


    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        args = (self.host, self.address, self.url, self.updateKey())
        return "-Record-\nHost: %s\nAddr: %s\nUrl: %s\nUpdate Key: %s\n" % args


def get_records(api_key, verbosity=0):
    v = verbosity
    url = "https://freedns.afraid.org/api/?action=getdyndns&sha=%s&style=xml"
    url = url % api_key
    info(v, "Retreiving records from %s" % url)

    # Open URL
    try:
        html_result = urlopen(url)
    except Exception as e:
        error("url(%s) - %s" % (url, e))
        return None

    # Read result
    raw_xml = html_result.read().strip()
    extra(v, "Full XML Result: %s" % raw_xml)

    # Check for authentication error
    if raw_xml == 'ERROR: Could not authenticate.':
        error("Could Not Authenticate")
        return None

    # Parse XML
    try:
        xml = et.fromstring(raw_xml)
    except Exception as e:
        error("XML Parsing Error - %s\nRaw XML: %s" % (e, raw_xml))
        return None

    # Parse xml object into array of dicts
    all_items = xml.findall('item')
    records = [Record(z) for z in [
              {y.tag: y.text for y in x} for x in all_items]]

    extra(v, "Retreived Records: %s" % records)

    # Return records if they exist, else return none
    return records if records != [] else None


def update_record(record, ip, verbosity=0):
    v = verbosity
    url = "https://freedns.afraid.org/dynamic/update.php?%s&address=%s"
    url = url % (record.updateKey(), ip)
    info(v, "Updating Record %s" % url)

    # Open URL
    try:
        html_result = urlopen(url)
    except Exception as e:
        error("url(%s) - %s" % (url, e))
        return

    # Read result
    result_str = html_result.read().strip()
    extra(v, "Full HTML Result: %s" % result_str)

    if "Error" in result_str:
        error(result_str)
        return

    # Success, print timestamp and success message
    from datetime import datetime
    time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    message("Updated On: %s" % time)
    message(result_str)
