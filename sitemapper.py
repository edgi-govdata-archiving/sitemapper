import sys, os, requests, json, time

class SiteMapper:
  """
  needs to call a web service to confirm upload
  also will unzip the file

  TODO document CLI and POLL methods

  TODO comments
  """

  def __init__(self, domain, useHttps, verbose, cli):
    """
    timestamp should be obtained from the redis web service: http://openciti.ca/cgi-bin/jobs
    its used as an identifier so multiple sitemaps may be performed for the same site moving forward
    """
    self.verbose = verbose

    self.https = 'https://'
    self.http = 'http://'
    self.protocol = self.https if useHttps else self.http

    service_root = 'http://openciti.ca/cgi-bin/'
    self.peek = service_root + 'peek'
    self.jobs = service_root + 'jobs'


    DATA_DIR = 'data'

    # query web service to get job
    if cli:
      self.timestamp = str(time.time()).split('.')[0]
      self.reqby = 'cli'
      self.domain = self.set_domain(domain)
    else:
      self.timestamp, self.reqby, job = self.poll()
      self.domain = self.set_domain(job)

    upload_file = self.timestamp + '_up.zip'
    self.upload_path = os.path.join(DATA_DIR, upload_file)

    outFromDomain = self.strip_protocol(self.domain).replace('.', '_')

    outPrefix = self.timestamp + '_' + outFromDomain
    outFile = outPrefix + '.xml'
    jsonFile = outPrefix + '.json'
    csvFile = outPrefix + '.csv'

    self.outputXml = os.path.join(DATA_DIR, outFile)
    self.outputJson = os.path.join(DATA_DIR, jsonFile)
    self.outputCsv = os.path.join(DATA_DIR, csvFile)

    if verbose:
      stemplate = '\ndomain: {}\nxml: {}\ncsv: {}\njson: {}\nzip: {}\n\n'
      showFileNames = stemplate.format(self.domain, self.outputXml, self.outputCsv, self.outputJson, self.upload_path)
      print(showFileNames)

    self.file_collection = []



  def strip_protocol(self, url):
    return url.replace(self.http, '').replace(self.https, '')

  def set_domain(self, domain):
    # ensure the domain has a valid protocol
    if not domain.startswith(self.protocol):
      domain = self.protocol + domain
    return domain.lower().strip()

  def rip(self):
    """

    """
    try:
      exeTemplate = 'python3 python-sitemap/main.py --domain {} --output {}'
      cmd = exeTemplate.format(self.domain, self.outputXml)
      os.system(cmd)
      self.file_collection.append(self.outputXml)
      if self.verbose:
        print('DONE: ' + self.outputXml)
    except Exception as ex:
      sys.stderr.write(ex)
      sys.exit(2)


  def zip(self):
    """
    compresses files for uploading using the zip utility
    """
    file_list = ' '.join(self.file_collection)
    zipcmd = 'zip {} {}'.format(self.upload_path, file_list)
    os.system(zipcmd)

    return self.file_exists(self.upload_path)

  def scp(self):
    """
    TEMP untill a POST service is worked out

    make sure to call zip() first in order to collect the files
    uploads file or files to cloud
    uses a system script along with private AWS credentials

    it must be in a directory on the PATH such as /usr/bin

    e@epc:~/sitemapper$ cat `which scpzip`
    #!/bin/bash
    if [ $# -lt 1 ]
    then
      exit 2
    fi

    scp -i "/path/to/creds.pem" $1 aws-id-com:~/public_html/openciti.ca/upload

    """
    scpcmd = 'scpzip ' + self.upload_path
    try:
      os.system(scpcmd)
    except Exception as ex:
      print('scp fail\n' + ex)
    #todo get return value by subprocess


  def file_exists(self, fn):
    exists = os.path.isfile(fn)
    if self.verbose:
      fout = '{} exists: {}'.format(fn, str(exists))
      print(fout)
    return exists

  def poll(self):
    """
    This method will be called if no paramaters are sent on the CLI
    domain, timestamp and requested by are obtained by a web service instead
    of being specified by the command line user
    """
    r = requests.get(self.peek)

    # convert to dict
    rdict = json.loads(r.text)

    ts = rdict['timestamp'].lower().strip()
    reqby = rdict['reqby'].lower().strip()
    job = rdict['job'].lower().strip()
    if self.verbose:
      print('timereq: {}, reqby: {}, job: {}\n\n'.format(ts, reqby, job))
    return ts, reqby, job

  def tocsv(self):
    """
    converts an xml file to a csv file
    """
    final = []
    header_line = 'url, lastmod\n'
    with open(self.outputXml, 'r') as f:
      lines = f.readlines()
      for line in lines:
        if (line.startswith("<url>")):
          clean = line.replace("<url><loc>", "")
          clean = clean.replace("</loc><lastmod>", ", ")
          clean = clean.replace("</lastmod></url>", "")
          final.append(clean)

    with open(self.outputCsv, 'w') as csv:
      csv.write(header_line)
      for line in sorted(final):
        csv.write(line)
    self.file_collection.append(self.outputCsv)
    if self.verbose:
      print('DONE: ' + self.outputCsv)


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

  def toJson(self):
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
    d = {}
    jsonDict = {}

    # a list containing a list for each url
    splitUrlsArray = []

    # marks the longest url in terms of path units
    # ie www.epa.org/abc/def/egc would have a length of 4
    maxUrlLen = 0
    with open(self.outputCsv, 'r') as csv:
      lines = csv.readlines()
      for line in lines:
        url, lastmod = line.split(',')

        # skip header
        if url.strip().startswith('url'):
          continue

        lastmod = lastmod.strip()
        url = self.strip_protocol(url)
        url = url.lower()
        url = url.split('?')[0]

        spliturl = url.split('/')

        #STORE MAX
        slen = len(spliturl)
        if slen > maxUrlLen:
          maxUrlLen = slen

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

    with open(self.outputJson, 'w') as xml:
      xml.write(j)
    self.file_collection.append(self.outputJson)

    if self.verbose:
      print('DONE: ' + self.outputJson)

if __name__ == '__main__':
  if len(sys.argv) < 2:
    cli = False
    domain = None
  else:
    domain = sys.argv[1]
    cli = True
  verbose = True

  https = False
  if len(sys.argv) == 3 and sys.argv[2].lower(strip) == 'https':
     https = True

  s = SiteMapper(domain, https, verbose, cli)
  s.rip()
  s.tocsv()
  s.toJson()
  goodzip = s.zip()
  if not goodzip:
    print ('\nZIP FAILED. NOT UPLOADING')
  else:
    s.scp()
  if verbose: print('\nDONE')
