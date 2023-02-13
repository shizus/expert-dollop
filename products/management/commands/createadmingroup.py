from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from products.models import Brand, Product


class Command(BaseCommand):
    help = 'Creates the admin group with all the permissions it needs'

    # def add_arguments(self, parser):
    #     pass

    def handle(self, *args, **options):

        admin_group, created = Group.objects.get_or_create(name='admin')

        brand_content_type = ContentType.objects.get_for_model(Brand)
        brand_permissions = Permission.objects.filter(content_type=brand_content_type)
        product_content_type = ContentType.objects.get_for_model(Product)
        product_permissions = Permission.objects.filter(content_type=product_content_type)

        admin_group.permissions.set(brand_permissions | product_permissions)

        self.stdout.write(self.style.SUCCESS('admin group successfully created!'))
