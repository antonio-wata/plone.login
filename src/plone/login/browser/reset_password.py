# -*- coding: utf-8 -*-
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName
from AccessControl import Unauthorized
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from plone.login import MessageFactory as _
from plone.login.interfaces import IResetPasswordForm
from plone.z3cform import layout
from zope.component import getMultiAdapter
from z3c.form import button
from z3c.form import field
from z3c.form import form


class ResetPasswordForm(form.EditForm):
    """ Implementation of the reset password form """

    fields = field.Fields(IResetPasswordForm)

    id = "ResetPasswordForm"
    label = _(u"Reset password")
    description = _(u"Reset")

    ignoreContext = True

    render = ViewPageTemplateFile('templates/reset_password.pt')

    prefix = ""

    def updateWidgets(self):

        super(ResetPasswordForm, self).updateWidgets(prefix="")

        self.widgets['password'].tabindex = 1
        klass = getattr(self.widgets['password'], 'klass', '')
        if klass:
            self.widgets['password'].klass = ' '.join([klass, _(u'stretch')])
        else:
            self.widgets['password'].klass = _(u'stretch')
        self.widgets['password'].placeholder = _(u'Super secure password')
        self.widgets['password_confirm'].tabindex = 2
        klass = getattr(self.widgets['password_confirm'], 'klass', '')
        if klass:
            self.widgets['password_confirm'].klass = ' '.join(
                [klass, _(u'stretch')])
        else:
            self.widgets['password_confirm'].klass = _(u'stretch')
        self.widgets['password_confirm'].placeholder = _(u'Confirm password')

    @button.buttonAndHandler(_('Reset Password'), name='reset_password')
    def handlePasswordReset(self, action):

        authenticator = getMultiAdapter((self.context, self.request),
                                        name=u"authenticator")
        if not authenticator.verify():
            raise Unauthorized
        data, errors = self.extractData()

        if errors:
            self.status = self.formErrorsMessage
            return

        password = str(data.get('password'))
        password2 = str(data.get('password_confirm'))
        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                raise WidgetActionExecutionError(
                    'password',
                    Invalid(u"Passwords must match."))

        current = api.user.get_current()

        # Try traverse subpath first:
        try:
            key = self.request['TraversalRequestNameStack'][:0]
        except IndexError:
            key = None

        # Fall back to request variable for BW compat
        if not key:
            key = self.request.get('key', None)

        # key is the value for arg randomstring
        pw_tool.resetPassword(current, key, password)

        IStatusMessage(self.request).addStatusMessage(
            _(u"Your password has been reset."), "info")

        self.request.response.redirect(self.context.absolute_url())


class ResetPasswordFormView(layout.FormWrapper):
    form = ResetPasswordForm
