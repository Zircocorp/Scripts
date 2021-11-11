#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from lxml import etree

def remove_namespace(doc, namespace):
    """Remove namespace in the passed document in place."""
    ns = u'{%s}' % namespace
    nsl = len(ns)
    for elem in doc.getiterator():
        if elem.tag.startswith(ns):
            elem.tag = elem.tag[nsl:]

def parseLine(xmlLine):
    """
    Remove syslog header and convert xml data to json
    """
    if not 'Event' in xmlLine:
    	return None
    xmlLine = "<Event>" + xmlLine.split("<Event>")[1]
    root = etree.fromstring(xmlLine)
    remove_namespace(root,u'http://schemas.microsoft.com/win/2004/08/events/event')
    child = {"#attributes": {"xmlns":"http://schemas.microsoft.com/win/2004/08/events/event"}}
    for appt in root.getchildren():
        nodename = appt.tag
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
            	childnode = elem.tag
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

    import sys
    import json
    import argparse
    import multiprocessing as mp
    from tqdm import tqdm
    from timeit import default_timer as timer
    from datetime import timedelta
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", '-i', help="Syslog file to convert", type=str, required=True)
    parser.add_argument("--output", '-o', help="Json output file", type=str)
    args = parser.parse_args()
    
    file = args.input
    
    start = timer()

    with open(file, "r", encoding="ISO-8859-1") as fp:
    	data = fp.readlines()

    pool = mp.Pool(mp.cpu_count())
    result = list(tqdm(pool.map(parseLine, data), total=len(data), colour="green"))
    pool.close()
    pool.join()
    outputData = json.dumps(result)
    end = timer()
    print(timedelta(seconds=end-start))
    
    if args.output:
       json.dump(result,open(args.output, 'w'))
    #else:
    #   print(result)

