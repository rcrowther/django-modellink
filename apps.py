from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _



# NB It would be custom to test for operation of depend libraries
# here, primarily Pillow. However, Django now does this for ImageFile.
# Also, the Wand files are all boxed and optional import. So, not a 
# concern.
class ModelLinkConfig(AppConfig):
    name = 'model_link'
    label = 'model_link'
    verbose_name = _("Display of Foreign (and OneToOne) keys")
