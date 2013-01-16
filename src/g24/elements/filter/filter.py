from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from yafowil.controller import Controller
from yafowil.base import UNSET
from yafowil.yaml import parse_from_YAML
from zExceptions import Unauthorized
from g24.elements.browser.vocabularies import keywords, timezones, locations
from g24.elements import messageFactory as _


IGNORES = ['save', 'cancel']

class Filter(BrowserView):
    template = ViewPageTemplateFile('filter.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.ignores = IGNORES

    def _fetch_form(self):
        return parse_from_YAML('g24.elements.filter:filter.yaml', self, _)

    def __call__(self):
        form = self._fetch_form()
        self.controller = Controller(form, self.request)
        if not self.controller.next:
            return self.template()
        if "location" not in self.request.RESPONSE.headers:
            self.request.RESPONSE.redirect(self.controller.next)

    def next(self, request):
        return self.context.absolute_url()

    @property
    def action(self):
        url = self.context.absolute_url()
        return '%s/@@filter' % url

    def save(self, widget, data):
        if self.request.method != 'POST':
            raise Unauthorized('POST only')
        obj = self._save(data.extracted)
        # return the rendered element html snippet
        self.request.response.redirect('%s%s' % (obj.absolute_url(), '/element'))

    def _save(self, data):
        _filter = data.filter
        self.request.set('_filter', _filter)
        return _filter

    def get(self):
        return UNSET


    @property
    def vocabulary_keywords(self):
        return keywords(self.context)

    @property
    def vocabulary_timezones(self):
        return timezones()

    @property
    def vocabulary_locations(self):
        return locations(self.context)
