#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import json
import argparse
import multiprocessing as mp
from tqdm import tqdm
from timeit import default_timer as timer
from datetime import timedelta
from lxml import etree

def cleanTag(tag,ns):
    nsl = len(ns)
    if ns in tag:
       return appt.tag[nsl:]
    else:
       return tag

def parseLine(xmlLine):
    """
    Remove syslog header and convert xml data to json
    """
    if not 'Event' in xmlLine:
        return None
    xmlLine = "<Event>" + xmlLine.split("<Event>")[1]
    root = etree.fromstring(xmlLine)
    ns = u'http://schemas.microsoft.com/win/2004/08/events/event'
    child = {"#attributes": {"xmlns": ns}}
    for appt in root.getchildren():
        nodename = cleanTag(appt.tag,ns)
        nodevalue = {}
        for elem in appt.getchildren():
            if not elem.text:
                text = ""
            else:
                try:
                    text = int(elem.text)
                except:
                    text = elem.text
            if elem.tag == 'Data':
                childnode = elem.get("Name")
            else:
                childnode = cleanTag(elem.tag,ns)
                if elem.attrib:
                    text = {"#attributes": dict(elem.attrib)}
            obj={childnode:text}
            nodevalue = {**nodevalue, **obj}
        node = {nodename: nodevalue}
        child = {**child, **node}
    event = { "Event": child }
    return event

###### Main ######
if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", '-i', help="Linux Sysmon log file to convert", type=str, required=True)
    parser.add_argument("--output", '-o', help="JSONL output file", type=str)
    parser.add_argument("--core", '-n', help="Nomber of core", type=int, default=mp.cpu_count())
    parser.add_argument("--array", '-a', help="Print an JSON array instead of a JSONL list", action="store_true")
    args = parser.parse_args()
    
    file = args.input
    
    start = timer()

    with open(file, "r", encoding="ISO-8859-1") as fp:
        data = fp.readlines()

    pool = mp.Pool(args.core)
    result = list(tqdm(pool.map(parseLine, data), total=len(data), colour="green"))
    pool.close()
    pool.join()
    
    if args.output:
        with open(args.output, "w", encoding="UTF-8") as fp:
            if args.array:
                json.dump(result, fp)
            else:
                for element in result:
                    if element is not None:
                        fp.write(json.dumps(element) + '\n')
    else:
        if args.array:
            print(json.dumps(result))
        else:
            [print(json.dumps(element)) for element in result]

    end = timer()
    print(timedelta(seconds=end-start))
