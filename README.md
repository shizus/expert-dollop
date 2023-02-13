
# Products Manager

# Pre-requisites
- virtualenv
- python3
- pip 19.0.3

# Installation - dev

```
virtualenv venv -p /location/to/python3
pip install -r requirements.txt
```

# Running migrations
```shell script
python manage.py migrate
```

# Running dev environment

```
python manage.py runserver
```

# Amazon SES

With amazon cli, use the command `aws configure` to setup your credentials for Amazon SES.
When the `DEBUG` is False the app will use boto3 to connect with Amazon SES and use it
to notify all the available admins when one changes a product, except the admin that
trigger the notification in the first time.
If `DEBUG` is True, then it will just log a message in the console to prevent spamming
emails in development or testing.

Make sure DEFAULT_FROM_EMAIL environment variable is setup with a valid email for
the amazon SES authentications keys provided on the previous step.

# Tests

```
python manage.py test
```

# Setting up the app

This app requires a group named admin with add, change, view and delete
permissions over Product and Brand model. This can be done manually with a 
django superuser. But I provided a django command to make it easier.

```shell script
python manage.py createadmingroup
```

Using this is one of the easiest ways to keep deploy automatic and to be sure
admin group is correctly setup in every environment even when new models are added.

# Types of users

## Super user
A django superuser with admin privileges over all the app.

## Staff
A django staff with access to the admin site but with privileges that
need to be set up individually or by group.

## Admin
An API app user with the admin group assigned. This gives them access to
create, update, delete and view(retrieve) Products and Brands.
All members of this group will be trigger a notification when they modify a
product.

## Fixtures

To make easier to try the app out of the box this repository has a 
fixture located in `products_data.json` in the `fixtures` directory.
To run it:

```shell script
python manage.py loaddata products_data.json
```

# Documentation

When the project is running an automatic documentation is available in: 
http://127.0.0.1:8000/redoc/
