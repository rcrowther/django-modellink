import copy

from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.urls.exceptions import NoReverseMatch
#from django.utils.safestring import mark_safe
from django.forms.widgets import Widget, Input, Media
from django.contrib import admin

        

class LinkViewWidget(Input):
    '''
    This widget presents a small/basic CRUD interface for a field.
    Since this suggests the field reprents a model, it is intended 
    for use on relation fields.
    The editing interface in this widget is links to appropriate 
    admin forms. But the view action will display a small table of 
    text renderable fields within the model.
    The widget is an interesting substitute for Django's default ModelCoosing
    widgets, more limited but clear in action and avoiding 
    potentially expensive db querying.
    
    model
        Class or instance
    mdata
        An iterable list of model-like data (the fields of which should
        themselves be iterables of field name/values)
    empty_vaLue
        A string to show if nothing else is rendered.
    url_format
        a callable of the form url_format(*args, action). USed to 
        provide the urls.
    '''
    input_type = 'hidden'
    template_name = 'model_link/widgets/view.html'
    data = {}
    related_model = None
    nodata_text = _("Unaccessable")
    is_inline = False
        
    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.attrs = self.attrs.copy()
        obj.data = copy.deepcopy(self.data)
        memo[id(self)] = obj      
        return obj
        
    @property
    def is_hidden(self):
        # Never hidden. It's a display. Overrrides detection of the 
        # 'hidden' attribute.
        return False

    def get_context(self, name, value, attrs):
        # widget -> nodata_text
        # widget -> data -> model_id -> mod4els/urls
        context = super().get_context(name, value, attrs)
        context['widget'].update({
            'is_inline' : self.is_inline,
            'data' : self.data,
            'nodata_text' : self.nodata_text 
         })
        return context

    class Media():
        css = {
            'screen': ('model_link/css/widgets.css',)
        }



class LinkControlWidget(Input):
    '''
    This widget presents a small/basic CRUD interface for a field.
    Since this suggests the field reprents a model, it is intended 
    for use on relation fields.
    The editing interface in this widget is links to appropriate 
    admin forms. But the view action will display a small table of 
    text renderable fields within the model.
    The widget is an interesting substitute for Django's default ModelCoosing
    widgets, more limited but clear in action and avoiding 
    potentially expensive db querying.
    
    This is a contrib.admin inclined widget---the urls are addressed 
    there.
    
    model
        Class, not instance
    mdata
        An iterable list of model data. The models should be iterables 
        of field name/values e.g. dicts.
    nodata_text
        A string to show if nothing  is rendered.
    '''
    # The idea here is to render the field as a hidden input, which
    # is unchanged on return. This means the form plays along with
    # all submission and save proceedure (rather than faffing with save
    # to make it a speciality). The display floats alongside.
    # I think rendering URLs belongs here, but conceed it is a faff, 
    # what with admin site and model both required.
    input_type = 'hidden'    
    template_name = 'model_link/widgets/control.html'
    data = {}
    related_model = None
    nodata_text = _('Unaccessible')
    is_inline = False

    def __init__(self, 
        admin_site=None,
        data={},
        show_add=False,
        show_view=False,
        show_change=False,
        show_delete=False,
        attrs=None
    ):
        if not(admin_site):
            admin_site = admin.site
        self.site_name = admin_site.name
        self.data = data
        self.show_add = show_add
        self.show_view = show_view
        self.show_change = show_change
        self.show_delete = show_delete
        super().__init__(attrs)
        
    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.attrs = self.attrs.copy()
        obj.data = copy.deepcopy(self.data)
        memo[id(self)] = obj      
        return obj
        
    @property
    def is_hidden(self):
        # Never hidden. It's a display. Overrides detection of the 
        # 'hidden' attribute.
        return False

    def get_related_url(self, app_label, model_name, action, *args):
        return reverse(
                "admin:{}_{}_{}".format(app_label, model_name, action),
                args=args,
                current_app=self.site_name
                )
                          
    def get_context(self, name, value, attrs):
        # Needed for URLs
        # if they throw errors, that's configuration
        # ---no interference.
        opts = self.related_model._meta
        app_label = opts.app_label
        model_name = opts.model_name
        
        # Generates:
        # widget -> nodata_text
        # widget -> data -> model_id -> models/urls
        context = super().get_context(name, value, attrs)
        modelctrls_data = {}         
        if (self.data):
            for mid, mdata in self.data.items():
                model_data = {}
                if self.show_view:
                    model_data = mdata
                urls = {}
                if self.show_add:
                    urls['add'] = self.get_related_url(
                    app_label, 
                    model_name,
                    'add', 
                    )
                if self.show_change:
                    urls['change'] = self.get_related_url(
                    app_label, 
                    model_name, 
                    'change',
                    mid
                    )
                if self.show_delete:
                    urls['delete'] = self.get_related_url(
                    app_label, 
                    model_name, 
                    'delete', 
                    mid
                    )
                if (model_data or urls):
                    modelctrls_data[mid] = {'models': model_data, 'urls': urls}
        context['widget'].update({
            'is_inline' : self.is_inline,
            'data' : modelctrls_data,
            'nodata_text' : self.nodata_text 
         })     
        return context
        
    class Media():
        css = {
            'screen': ('model_link/css/widgets.css',)
        }
