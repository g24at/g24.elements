from Products.Five.browser import BrowserView
from plone.uuid.interfaces import IUUID
from zope.interface import Interface
from zope.interface import implements
from zope.component import adapts
from zope.publisher.interfaces.browser import IBrowserRequest
from zope.publisher.interfaces.browser import IBrowserView
from zope.contentprovider.interfaces import IContentProvider
from zope.security import checkPermission
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from g24.elements import behaviors

from plone.app.event.interfaces import IRecurrence
from plone.app.event.interfaces import IEventAccessor
from plone.app.event.browser.event_view import prepare_for_display
def format_event_dates(context, start, end, whole_day=False):
    formated_dates = prepare_for_display(context, start, end, whole_day)
    if formated_dates['same_day'] and whole_day:
        return '%s' % formated_dates['start_date']
    elif formated_dates['same_day'] and formated_dates['same_time']:
        return '%s %s' % (formated_dates['start_date'],
                          formated_dates['start_time'])
    elif formated_dates['same_day']:
        return '%s %s - %s' % (formated_dates['start_date'],
                               formated_dates['start_time'],
                               formated_dates['end_time'])
    elif whole_day:
        return '%s - %s' % (formated_dates['start_date'],
                            formated_dates['end_date'])
    else:
        return '%s %s - %s %s' % (formated_dates['start_date'],
                                  formated_dates['start_time'],
                                  formated_dates['end_time'],
                                  formated_dates['end_time'])


# TODO: why does robert inherit vom Acquisition.Explicit?
class ElementProvider(BrowserView):
    implements(IContentProvider)
    adapts(Interface, IBrowserRequest, IBrowserView)
    template = ViewPageTemplateFile(u'element_provider.pt')

    def __init__(self, context, request, view):
        #self.__parent__ = view # TODO: from roberts Explicit example
        self.view = view
        self.context = context
        self.request = request

    def format_event_dates(self, start, end):
        if not self.is_event: return None
        self.data = IEventAccessor(self.context)
        return format_event_dates(self.context, start, end, self.context.whole_day)

    def occurrences(self):
        if not self.is_event: return None
        rec = IRecurrence(self.context, None)
        if rec:
            return rec.occurrences()
        else:
            return None

    @property
    def uuid(self):
        # TODO: do i need aq_base here? (see uuid example in collective-docs
        #context = self.context.aq_base # make, context isn't on parent
        uuid = IUUID(self.context, None)
        return uuid

    @property
    def is_title(self):
        return behaviors.is_title(self.context)

    @property
    def is_event(self):
        return behaviors.is_event(self.context)

    @property
    def is_place(self):
        return behaviors.is_place(self.context)

    @property
    def can_add(self):
        return checkPermission('g24.AddBasetype', self.context)

    @property
    def can_edit(self):
        return checkPermission('g24.ModifyBasetype', self.context)

    def update(self): pass

    def render(self):
        return self.template(self)
