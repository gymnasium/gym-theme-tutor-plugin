# Assign theme automatically via @https://github.com/aulasneo/tutor-contrib-branding/blob/master/tutorbranding/templates/tasks/lms/init
./manage.py lms shell -c "
import sys
from django.contrib.sites.models import Site
def assign_theme(name, domain):
    print('Assigning theme', name, 'to', domain)
    if len(domain) > 50:
            sys.stderr.write(
                'Assigning a theme to a site with a long (> 50 characters) domain name.'
                ' The displayed site name will be truncated to 50 characters.\\n'
            )
    site, _ = Site.objects.get_or_create(domain=domain)
    if not site.name:
        name_max_length = Site._meta.get_field('name').max_length
        site.name = domain[:name_max_length]
        site.save()
    site.themes.all().delete()
    if name != 'default':
        site.themes.create(theme_dir_name=name)
domain_names = [
    '{{ LMS_HOST }}',
    '{{ CMS_HOST }}',
    '{{ PREVIEW_LMS_HOST }}',
    '{{ LMS_HOST }}:8000',
    '{{ CMS_HOST }}:8001',
    '{{ PREVIEW_LMS_HOST }}:8000',
]
for domain_name in domain_names:
    assign_theme('gym-theme', domain_name)
"

# Force enable `courseware.enable_navigation_sidebar`
{% if is_mfe_enabled("learning") %}
echo "DEBUG: enabling waffle flag: courseware.enable_navigation_sidebar"
(./manage.py lms waffle_flag --list | grep courseware.enable_navigation_sidebar) || ./manage.py lms waffle_flag --create --everyone courseware.enable_navigation_sidebar 

echo "DEBUG: enabling waffle flag: user_tours.tours_disabled"
(./manage.py lms waffle_flag --list | grep user_tours.tours_disabled) || ./manage.py lms waffle_flag --create --everyone user_tours.tours_disabled 
{% else %}
./manage.py lms waffle_delete --flags courseware.enable_navigation_sidebar
{% endif %}

echo "DEBUG: enabling waffle switch: certificates.auto_certificate_generation"
(./manage.py lms waffle_switch --list | grep certificates.auto_certificate_generation) || ./manage.py lms waffle_switch --create certificates.auto_certificate_generation on
