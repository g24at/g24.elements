from Acquisition import aq_inner
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from g24.elements.behaviors import IBase
from g24.elements.behaviors import IEventLocation
from plone.app.event.dx.behaviors import IEventBasic
from plone.app.event.dx.behaviors import IEventRecurrence
from g24.elements.behaviors import IFeatures
from g24.elements.behaviors import IPlace
from g24.elements.interfaces import IBasetype
from g24.elements.sharingbox.crud import add
from g24.elements.sharingbox.crud import create
from g24.elements.sharingbox.crud import edit
from plone.app.event.dx.behaviors import first_weekday_sun0
from plone.dexterity.events import AddCancelledEvent
from plone.dexterity.events import EditCancelledEvent
from plone.dexterity.events import EditFinishedEvent
from plone.z3cform.layout import wrap_form
from z3c.form import button
from z3c.form import field
from z3c.form import form
from z3c.form import subform
from zope.event import notify

from g24.elements import messageFactory as _
from z3c.form.i18n import MessageFactory as __
from plone.dexterity.i18n import MessageFactory as ___

import os


template_path = os.path.dirname(__file__)

G24_BASETYPE = 'g24.elements.basetype'
FEATURES = [
    'is_thread',
    'is_event',
    'is_place'
]


class ASubForm(subform.EditSubForm):
    template = ViewPageTemplateFile('subform.pt', template_path)
    behaviors = []

    def __init__(self, context, request, form, ignore_ctx):
        # TODO: allow self.fields to be made of multiple interfaces
        fields = None
        for behavior in self.behaviors:
            morefields = field.Fields(behavior)
            if fields:
                fields = fields + morefields
            else:
                fields = morefields
            if not ignore_ctx:
                # Check if the context really provides any of the behaviors.
                # If not, we have to ignore the context for the whole subform.
                ignore_ctx = ignore_ctx or not behavior.providedBy(context)

        self.fields = fields
        self.ignoreContext = ignore_ctx
        super(ASubForm, self).__init__(context, request, form)


class FeaturesSubForm(ASubForm):
    """z3cform based Features subform"""
    title = u"Features"
    prefix = 'features'
    behaviors = [IFeatures, ]

class BaseSubForm(ASubForm):
    """z3cform based Place subform"""
    title = u"Base"
    prefix = 'base'
    behaviors = [IBase, ]


class EventSubForm(ASubForm):
    title = u"Event"
    prefix = 'event'
    behaviors = [IEventBasic, IEventRecurrence, IEventLocation, ]

    def update(self):
        super(EventSubForm, self).update()
        # Set widget parameters, as plone.autoform doesn't support subforms yet
        # (not: ObjectSubForm, which is something else).
        widgets = self.widgets
        widgets['start'].first_day = first_weekday_sun0
        widgets['end'].first_day = first_weekday_sun0
        widgets['recurrence'].first_day = first_weekday_sun0
        widgets['recurrence'].start_field = 'start'  # Plain z3cform seems not
                                                     # to prefix schema fields


class PlaceSubForm(ASubForm):
    title = u"Place"
    prefix = 'place'
    behaviors = [IPlace, ]


class ASharingboxForm(form.Form):
    """z3cform Sharingbox"""
    template = ViewPageTemplateFile('form.pt', template_path)
    fields = field.Fields(IBasetype)
    prefix = 'shbx'
    subforms = []
    portal_type = G24_BASETYPE
    immediate_view = None

    def update(self):
        super(ASharingboxForm, self).update()
        context = self.context
        request = self.request
        ignore_ctx = self.ignoreContext
        self.update_subforms(context, request, ignore_ctx)

    def update_subforms(self, context, request, ignore_ctx):
        self.subforms = [
            FeaturesSubForm(context, request, self, ignore_ctx),
            BaseSubForm(context, request, self, ignore_ctx),
            EventSubForm(context, request, self, ignore_ctx),
            PlaceSubForm(context, request, self, ignore_ctx),
        ]
        [subform.update() for subform in self.subforms]

    def nextURL(self):
        if self.immediate_view is not None:
            return self.immediate_view
        else:
            return self.context.absolute_url()

    def extractData(self):
        # update_subforms - self.update is called on rendering.
        self.update_subforms(self.context, self.request, self.ignoreContext)
        data = {}
        errors = []
        main_data, main_errors = super(ASharingboxForm, self).extractData()
        data.update(main_data)
        errors += list(main_errors)
        for subform in self.subforms:
            sub_data, sub_errors = subform.extractData()
            data.update(sub_data)
            errors += list(sub_errors)
        return [data, errors]


class SharingboxEditForm(ASharingboxForm):
    """z3cform Sharingbox"""
    ignoreContext = False

    @button.buttonAndHandler(___(u'Save'), name='save')
    def handleApply(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        content = self.getContent()
        edit(content, data)
        IStatusMessage(self.request).addStatusMessage(___(u"Changes saved"), "info")
        self.request.response.redirect(self.nextURL())
        notify(EditFinishedEvent(self.context))

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(___(u"Edit cancelled"), "info")
        self.request.response.redirect(self.nextURL())
        notify(EditCancelledEvent(self.context))

SharingboxEditFormView = wrap_form(SharingboxEditForm)


class SharingboxAddForm(ASharingboxForm):
    """z3cform Sharingbox add form"""
    ignoreContext = True

    @button.buttonAndHandler(___('Add'), name='add')
    def handleAdd(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        obj = self.create()
        self.add(obj, data)
        if obj is not None:
            # mark only as finished if we get the new object
            self._finishedAdd = True
            IStatusMessage(self.request).addStatusMessage(___(u"Item created"), "info")
        self.request.response.redirect(self.nextURL())

    @button.buttonAndHandler(___(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(___(u"Add New Item operation cancelled"), "info")
        self.request.response.redirect(self.nextURL())
        notify(AddCancelledEvent(self.context))

    def create(self):
        obj = create(self.context, self.portal_type)
        return obj

    def add(self, obj, data):
        container = aq_inner(self.context)
        obj = add(obj, container)
        edit(obj, data, order=FEATURES)
        self.immediate_view = obj.absolute_url()
SharingboxAddFormView = wrap_form(SharingboxAddForm)
