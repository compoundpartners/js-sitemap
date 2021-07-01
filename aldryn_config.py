from aldryn_client import forms

class Form(forms.BaseForm):
    show_alternatives = forms.CheckboxField(
        "Show language alternatives",
        required=False,
        initial=False)

    def to_settings(self, data, settings):
        if data['show_alternatives']:
            settings['SITEMAP_SHOW_ALTERNATIVES'] = int(data['show_alternatives'])

        return settings
