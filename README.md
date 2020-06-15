# Django LinkModel
A few utilities for handling foreign key relations in Django.

## Why?
Can be hard to explain, though the [django-reverse-admin documentation](https://pypi.org/project/django-reverse-admin) explains well, in a Django way.

You have a model with a Foreign or OneToOne key. You bring the model up in admin. It will show the ModelChoiceField with a Select widget. This is a flexible and comprehensive setup, but not to everyone's taste. The only alternative is to make the field read-only. And, as documented elsewhere, ModelChoiceField can be heavy on SQL queries. 

In many scenarios, you may hope to replace a simple foreign key with a form for the linked model. Can't be done. Django documentation suggests 'inline' forms, but look closely at the [example of authors and books](https://docs.djangoproject.com/en/3.0/ref/contrib/admin/#django.contrib.admin.StackedInline). Inline forms only work from the addressed/data end of a foreign key. And they require that the relation is constructed with a definition of reverse lookup (personally, I hate anything that dictates data structures). The example is subtly distorted from the intuitive. Want you want to happen will not.

This app contains a few helpers for this scenario,

## Why the obscure name?
The names are inconsistent in this area. You found this module, good for you.
 
## Install
Drop the code into a webapp. Declare in installed apps,

    INSTALLED_APPS = [
        # added
        'model_link.apps.ModelLinkConfig',
        ...
    ]

The code needs to be an app because it declares template and static codebases. It needs no migration.


## Django ModelLinkAdmin
Render a foreignkey field as a form.

This is a light rework of [Django Reverse Admin](https://pypi.org/project/django-reverse-admin). It renamed, and adds templating to optionally move the inline forms to the top of the admin, rather than the usual position at bottom.

### Why Rename the code?
Reverse Admin was called 'reverse' because it works backwards from the usual Django Admin direction.

But Django Admin works backwards from the usual 'foreign key'-> DB table conception. For most people 'Reverse Admin'  describes the data structure as conceived in a forward direction. You understand me?

Nobodies fault, but too weird for me.


### Use
ModelLinkAdmin pretends a foreign key is a one-off InlineModelForm. You get a special Admin model, with an extra attribute to define the foreign keys to be rendered,

    from model_link.model_admin import ModelLinkAdmin

    class PageAdmin(ModelLinkAdmin):
        inline_type = 'stacked'
        inline_links = [
                          'img',
                          ]
                      
You can also define the fields on the rendered form,

    class PageAdmin(ModelLinkAdmin):
        inline_type = 'stacked'
        inline_links = [
                          ('img', {'fields': ['title']}),
                          ]
                          

### The inline_pos attribute
I make no claim to the above. An addition,

    class PageAdmin(ModelLinkAdmin):
        inline_type = 'stacked'
        inline_pos = 'top'    
        inline_links = [
                          ('img', {'fields': ['title']}),
                          ]
                          
Set 'inline_pos' to 'top' and the inline form will display at the top of the admin form, not the bottom, Which sometimes makes visual sense (remember, there will only be one form to represent a Foreign keys, they will not multiply like the usual inline forms).

### TODO
Yes, I'd like to target the foreign key inlines so they don't mix with regular inlines. But I don't have the time, so don't mix foreign key and regular inlines if using 'inline_pos'.


## Read-only Foreign key displays
Form fields and widgets to display foreign keys.

### Form Fields
Are based on a class ModelLinkGet. This passes the foreign key value untouched in a HiddenInput, thus satisfying validation (surely!). At the same time the field retrieves the Foreign key object and pokes it into the supplied widget.

#### Why a field
And why not a quick override of Django Admin's formfield_for_dbfield() method? Which many coders and their apps do? Because this is more general and simple, at the expense of an extra form element. Your choice.
 
#### LinkIntegerField
This is the form field most people need (most foreign keys link on an integer id key). Replace the form field in an Admin,

    from model_link.form_fields import LinkIntegerField
    from model_link.widgets import LinkViewWidget, LinkControlWidget

    class PageAdmin(admin.ModelAdmin):
        ...
        def formfield_for_dbfield(self, db_field, request, **kwargs):
            ff = super().formfield_for_dbfield(db_field, request, **kwargs)
            if (db_field.__class__ == SomeForeignKeyField):
                w = LinkControlWidget(
                    show_view=True,
                    show_add=True,
                    show_change=True,
                    show_delete=True,
                )
                #w = LinkViewWidget
                #w.is_inline = True
                ff = LinkIntegerField(db_field, widget=w, fields=['src','title'])
            return ff

For more on the widgets, go down a bit.

#### Field definitions
LinkFields require the database field from a model. This is rather an odd thing to ask for, but should be available or importable. With it, the field can retrieve the object a foreign key points to.

LinkFields require that you define fields and/or exclude parameters, for the same reason as Django requires this on forms. Without the options, you will see nothing. You could also pass fieldsets from Admin data.

#### If your foreign key is not on integer value...
Make your own form field using ModelLinkGet. It's only a couple of lines of code.


### Widgets
Two widgets for the field. They both have this attribute,

is_inline
    display in an inline style (default is stacked)
    
#### LinkViewWidget
View some data from the foreign key object. 

A little more flexible than a simple imline. To follow the Books/Author Django example, display the Author name and maybe their birthdate/country of origin?
  
#### LinkControlWidget
View some id data from the foreign key object. with links to Django Admin forms for the attached foreign key model.

An alternative to the ModelChoiceField/Select display. Of course, you cannot change the attached model with this, but you can CRUD edit the existing key.


# The end
Yep, that's it.
