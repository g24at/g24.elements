import logging
#from Acquisition import aq_base
from Acquisition import aq_parent
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

from g24.elements.behaviors import ITitle
from g24.elements.interfaces import IBasetype, IBasetypeAccessor

logger = logging.getLogger(__name__)

from plone.app.event.interfaces import IRecurrence
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
        if not self.data.is_event: return None
        return format_event_dates(self.context, start, end, self.data.whole_day)

    def occurrences(self):
        if not self.data.is_event: return None
        rec = IRecurrence(self.context, None)
        if rec:
            return rec.occurrences()
        else:
            return None

    def get_parent_thread(self):

        def _get_parent_thread(ctx):
            parent = aq_parent(ctx)
            if not IBasetype.providedBy(parent):
                return None
            elif ITitle.providedBy(parent):
                return parent
            else:
                return _get_parent_thread(parent)

        parent = _get_parent_thread(self.context)
        return IBasetypeAccessor(parent, None)

    @property
    def uuid(self):
        # TODO: do i need aq_base here? (see uuid example in collective-docs
        # doing aq_base(context) in __init__ breaks permission checks.
        #context = self.context.aq_base # make, context isn't on parent
        uuid = IUUID(self.context, None)
        if not uuid:
            logger.warn('Element with id %s has no uuid.' % self.context.id)
        return uuid

    @property
    def data(self):
        return IBasetypeAccessor(self.context)

    @property
    def can_add(self):
        return checkPermission('g24.AddBasetype', self.context)

    @property
    def can_edit(self):
        return checkPermission('g24.ModifyBasetype', self.context)

    def update(self): pass

    def render(self):
        return self.template(self)
