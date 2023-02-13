import boto3
from django.conf import settings
from django.contrib.auth.models import User

import logging

logger = logging.getLogger(__name__)

class NotificationsManager:
    """ Handles emails notifications"""

    @staticmethod
    def notify_admins(trigger_user, product):
        """
        Sends an email to all the admin except the one received by parameter to notify them about a product change.
        """

        if settings.DEBUG:
            response = NotificationsManager._development_behaviour(trigger_user, product)
        else:
            response = NotificationsManager._production_behaviour(trigger_user, product)

        return response

    @staticmethod
    def _development_behaviour(trigger_user, product):

        recipient_emails = [user.email for user in
                            User.objects.filter(groups__name="admin").exclude(email=trigger_user.email)]

        logger.info('Destination: ', {
                "ToAddresses": recipient_emails
            })

        logger.info('Message', {
                "Subject": {
                    "Data": f"Product {product.name} has been modified",
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": f"User {trigger_user.get_full_name()} modified this product.",
                        "Charset": "UTF-8"
                    }
                }
            })

        return None

    @staticmethod
    def _production_behaviour(trigger_user, product):
        client = boto3.client("ses", region_name=settings.AWS_REGION)

        recipient_emails = [user.email for user in
                            User.objects.filter(groups__name="admin").exclude(email=trigger_user.email)]

        if not recipient_emails:
            return None

        response = client.send_email(
            Source=settings.DEFAULT_FROM_EMAIL,
            Destination={
                "ToAddresses": recipient_emails
            },
            Message={
                "Subject": {
                    "Data": f"Product {product.name} has been modified",
                    "Charset": "UTF-8"
                },
                "Body": {
                    "Text": {
                        "Data": f"User {trigger_user.get_full_name()} modified this product.",
                        "Charset": "UTF-8"
                    }
                }
            }
        )
        return response
