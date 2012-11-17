import urllib2
from urllib2 import HTTPError
from Products.Five import BrowserView

class OembedProxy(BrowserView):

    def __call__(self):

        host = 'http://api.embed.ly/1/oembed'
        #host = 'http://api.embed.ly/v1/api/oembed'
        key = 'ac25fbba94af11e1a1394040aae4d8c9'
        req = self.request
        req.response.setHeader("Content-type", "application/json")

        url = req.get('url', None)
        if not url:
            self.request.response.setStatus(500, "url parameter missing.")
            return
        qurl = urllib2.quote(url)
        force = req.get('force', 'false')
        frame = req.get('frame', 'false')

        try:
            fetch_url = '%s?%s&url=%s&format=json' % (host, key, qurl)
            #fetch_url = '%s?%s&url=%s&frame=%s&force=%s&format=json' % (
            #        host, key, qurl, frame, force)
            json_string = urllib2.urlopen(fetch_url).read()
            return json_string
        except HTTPError:
            self.request.response.setStatus(500, "Error while requesting oembed from server.")
