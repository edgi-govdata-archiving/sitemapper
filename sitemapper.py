"""
Copyright (C) 2017 Eli Tabello

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, os, json, time

class SiteMapper:
  def __init__(self):
    self.DATA_DIR = 'data'
    self.https = 'https://'
    self.http = 'http://'
    self.protocol = self.http

  def strip_protocol(self, url):
    return url.replace(self.http, '').replace(self.https, '')

  def set_domain(self, domain):
    if not domain.startswith(self.protocol):
      domain = self.protocol + domain
    return domain.lower().strip()

  def rip(self, domain):
    timestamp = str(time.time()).split('.')[0]
    domain = self.set_domain(domain)
    outFromDomain = self.strip_protocol(domain).replace('.', '_')
    outFile = '{}_{}.xml'.format(timestamp, outFromDomain)
    outputXml = os.path.join(self.DATA_DIR, outFile)

    try:
      exeTemplate = 'python3 python-sitemap/main.py --domain {} --output {}'
      cmd = exeTemplate.format(domain, outputXml)
      os.system(cmd)

    except Exception as ex:
      sys.stderr.write(ex)
      sys.exit(2)

  def file_exists(self, fn):
    exists = os.path.isfile(fn)
    return exists

  def tocsv(self, xmlFile):
    if not self.file_exists(xmlFile):
      raise FileNotFoundError(xmlFile)
    
    outputCsv = xmlFile.replace('.xml', '.csv')

    final = []
    header_line = 'url, lastmod\n'
    
    with open(xmlFile, 'r') as f:
      lines = f.readlines()
      for line in lines:
        if (line.startswith("<url>")):
          clean = line.replace("<url><loc>", "")
          clean = clean.replace("</loc><lastmod>", ", ")
          clean = clean.replace("</lastmod></url>", "")
          final.append(clean)

    with open(outputCsv, 'w') as csv:
      csv.write(header_line)
      for line in sorted(final):
        csv.write(line)

    return outputCsv

  def getNth(self, listOfLists, n):
    """
    input: a list of lists and n
    returns a list containing of only the nth element of each list
    """
    return [element[n] for element in listOfLists]

  def getNthWithValue(self, listOfLists, n, value):
    """
    input: a list of lists, n and value
    returns a list containing of only the nth element of each list
    where the nth element is equal to value`
    """
    return [element for element in listOfLists if element[n] == value]

  def tojson(self, csvFile):
    """
    Just going to produce a nested dict of 'domain', 'sites' and 'leafs'
    'domain' is the main website: http://abc.agency.gov
    'sites' are the first path after the domain
    'leafs' are objects that contain the full url (minus protocol) and last modified timestamp

    example:

    "www.epa.gov": {
        "aboutepa": [
            {
                "lastmod": "2016-12-17T19:04:40+00:00",
                "url": "www.epa.gov/aboutepa/about-environmental-appeals-board-eab"
            },
            {
                "lastmod": "2016-12-17T19:56:43+00:00",
                "url": "www.epa.gov/aboutepa/about-epas-campus-research-triangle-park-rtp-north-carolina"
            }
            ...

    """
    #check to see if the csv file is present
    if not self.file_exists(csvFile):
      raise FileNotFoundError(csvFile)

    jsonFile = csvFile.replace('.csv', '.json')
    # used for quick lookup of lastmod
    d = {}

    # dict to be rendered to json
    jsonDict = {}

    # a list containing a list for each url
    splitUrlsArray = []

    with open(csvFile, 'r') as csv:
      lines = csv.readlines()
      for line in lines:
        # some urls have commas so use rplit,1 to split only the first comma from the RHS
        url, lastmod = line.rsplit(',', 1)

        # skip header
        if url.strip().startswith('url'):
          continue

        lastmod = lastmod.strip()
        url = self.strip_protocol(url)
        url = url.lower()
        url = url.split('?')[0]

        spliturl = url.split('/')
        slen = len(spliturl)
        # store root last mod separately TODO
        if slen == 1:
          continue

        if url not in d:
          d[url] = {}
          d[url]['lastmod'] = lastmod

        splitUrlsArray.append(spliturl)

    # get unique keys first token ie: domain
    # init as a dict
    first = self.getNth(splitUrlsArray, 0)

    # convert to set and back to list to eliminate duplicates
    firstSet = set(first)
    firstUniq = list(firstSet)
    
    rootDomain = ''
    if len(firstUniq) == 1:
      rootDomain = firstUniq[0]
      jsonDict[rootDomain] = {}
    else:
      for domain in firstUniq:
        if domain not in jsonDict:
          jsonDict[domain] = {}

    # get list of uniq second keys
    seconds = self.getNth(splitUrlsArray, 1)

    # convert to set and back to list to eliminate duplicates
    secondSet = set(seconds)
    secondList = list(secondSet)

    for s in secondList:
      jsonDict[rootDomain][s] = []

      try:
        allNth = self.getNthWithValue(splitUrlsArray, 1, s)
      except:
        continue

      # append leafs
      for tokens in allNth:
        url = '/'.join(tokens)
        lastmod = d[url]['lastmod']
        leaf = {'url': url, 'lastmod': lastmod}
        jsonDict[rootDomain][s].append(leaf)

    j = json.dumps(jsonDict)

    with open(jsonFile, 'w') as xml:
      xml.write(j)

if __name__ == '__main__':
  """
  sending a domain alone will produce, xml, csv and json

  xml generation sometimes does not terminate, so run the csv and json options manually

  send an xml filename followed by --csv converts it to csv and json
  send a csv filename followed by --json converts it to json
  """

  def has_arg(argList):
    return [e in sys.argv for e in argList]

  csvArgs = ['--csv', '-c']
  jsonArgs = ['--json', '-j']
  
  domainOrFile = sys.argv[1]

  jsn =  True in has_arg(jsonArgs)
  csv =  True in has_arg(csvArgs)
  
  s = SiteMapper()

  if csv:
    csvFile = s.tocsv(domainOrFile)
    s.tojson(csvFile)
  elif jsn:
    s.tojson(domainOrFile)
  else:
    xmlfile = s.rip(domainOrFile)
    csvfile = s.tocsv(xmlfile)
    s.tojson(csvfile)