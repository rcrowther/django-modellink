from itertools import chain
from django.utils.translation import gettext, gettext_lazy as _
from django.forms.fields import Field, IntegerField
from django.forms.widgets import (
    HiddenInput,
)
from django.core.exceptions import ValidationError
from django.core.exceptions import ImproperlyConfigured

from .widgets import LinkViewWidget


                
class LinkModelModifier(Field):
    '''
    A field mixin that offers loading of related model data.
    Compare to forms.models.ModelChoiceField, which offers choices. 
    But this has no need of an adjustable queryset, it takes the model 
    field from which it can derive all necessary information.    
    
    In the same way as ModelChoiceField, the mixin transforms the object
    to a dict, which is pushed to the attached widget.
    
    model_field
        an instance, not the class
    fields
        fields to retrieve from the remote object
    exclude
        fields to exclude from the remote object
    '''
    model_field = None
    widget = LinkViewWidget
    fields = None
    exclude = None
    
    def __init__(self, 
            model_field,
            *,
            fields={},
            exclude={},
            **kwargs
        ):
        super().__init__(**kwargs)
        self.model_field = model_field
        
        # Contorted. The aim is to catch if the coder does nothing, so 
        # is baffled by output. Then substitute resonable defaults.
        self.fields=fields or self.fields
        self.exclude=exclude or self.exclude
        if (self.fields is None and self.exclude is None):
            raise ImproperlyConfigured(
                "Creating a RemoteModel Field without the 'fields' "
                "or 'exclude' attribute is prohibited; the %s "
                "needs updating." % self.__class__.__name__
            )    
        if (self.fields is None):
            self.fields = {}
        if (self.exclude is None):
            self.exclude = {}            
        
    # Helpers. Given the, ummm, luxurious nature of Django meta
    # information, needed.
    def _related_model(self):
        #NB admin contains utils.get_model_from_relation(model_field)
        # which uses field.get_path_info()[-1].to_opts.model
        # A variation is model_field.remote_field.
        # but this seems most direct?
        return self.model_field.target_field.model

    def qs_to_dict(self, instance, fields=[], exclude=[]):
        '''
        Generate a dictionary of displayable data from an model object.
        return
            A dict fieldname -> fieldvalue
        '''
        # Very like models.forms.model_to_dict, but it isn't.
        data = {}
        if (not (instance)):
            return data
        opts = instance._meta
        for f in chain(opts.concrete_fields, opts.many_to_many):
            if f.name not in fields:
                continue
            if f.name in exclude:
                continue
            data[f.name] = f.value_from_object(instance)
        return data
        
    def get_object(self, value, hints={}):
        '''
        Get the remote object referred to by the field value.
        Note this does some catches error if an object is not found. 
        Also note the return can be None, so for many uses needs testing.
        return
            the object (queryset result), or None.
        '''
        # See admin.options.get_object() for similar shenannigans
        model = self._related_model()
        remote_manager = model._base_manager.db_manager(hints=hints)
        remote_fieldname = self.model_field.target_field.name
        try:
            object_id = self.to_python(value)
            query = {remote_fieldname : object_id}
            return remote_manager.get(**query)
        except (model.DoesNotExist, ValidationError, ValueError):
            return None            

    def get_data(self, value, fields=[], exclude=[]):
        obj_dict = {}

        # if the field points at anything, generate data
        if (value):
            obj = self.get_object(value)
            obj_dict = self.qs_to_dict(obj, fields, exclude)
            
            # Now a trick. We here print one model, but 
            # the widget is set to iterate, so for the future make single object into
            # a dict.
            # This has it's advantages. Because the model data is keyed 
            # by the foreign key, unique and probably the pk, the key
            # can be used for URL generation. There is no need to 
            # carry non-display entries for the sake of URL generation. 
            # Clean separation, 
            obj_dict = {value : obj_dict}
        return obj_dict

    def get_bound_field(self, form, field_name):
        bf = super().get_bound_field(form, field_name)

        # A key moment in this field.
        # The field has bound data, so we can ask it what it's value is.
        # As a foreign key, this will be a value that points to model 
        # data in another table.
        # Like ModelChoiceField, attach data to the widget by pushing 
        # in.
        self.widget.data = self.get_data(bf.value(), self.fields, self.exclude)
        self.widget.related_model = self._related_model()
        return bf    



class LinkIntegerField(LinkModelModifier, IntegerField):
    '''
    A base field that offers access to related models.
    Compare to forms.models.ModelChoiceField, which offers choices. But 
    this has no need of an adjustable queryset, it takes the model field
    from which it can derive all necessary information.    
    
    fields
        fields in the rendered object to include
    exclude
        fields in the rendered object to exclude
    '''
    widget = LinkViewWidget

    


