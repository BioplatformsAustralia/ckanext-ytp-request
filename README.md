ckanext-ytp-request
===================

CKAN extension providing means to control organization member requests, requests history and related operations.

Features
--------

- Users can request to be part of organization
- Organization admins and global admins can approve or reject request
- Selected organizations can be configured to automatically approve requests
- Users can review their current memberships and requests
- Request history log

## Compatibility

Tested with CKAN 2.8

## Installation

Install to your ckan virtual environment

```
pip install -e  git+https://github.com/BioplatformsAustralia/ckanext-ytp-request.git#egg=ckanext-ytp-request
```

Add to ckan.ini.  As the extension extends themes and other extensions, it will need to be
at the start of the list

```
ckan.plugins = ytp_request ...
```

## Include / Exclude Organizations in listing

In your ckan.ini file, you can set which organisations are to be included or excluded from the
member request selector

```
## Member Request Settings
# If empty, all organisations are included.  If not, only those listed are included
# Entries are seperated by whitespace
ckanext.ytp_request.include =
ckanext.ytp_request.exclude = grasslands bpa-barcode2
```

## Override email destination for membership request emails

In your ckan.ini file, you can set a series of email addresses as destinations
to which you can send the membership request emails to.   This will override the default
behaviour of sending to all the relevant admin users.

```
## Member Request Email Settings
# If empty or not present, request emails will be sent to the relevant admin users
# If not, emails will only be sent to these email addresses
# Entries are seperated by whitespace
ckanext.ytp_request.override = a@example.com b@example.com
```


## Bioplatforms Australia Data Portal Specifics

This CKAN extension is deployed on the BPA Data Portal.  The following are notes in that context.

### Email address used for emails

The environment variable BIOPLATFORMS_HELPDESK_ADDRESS is used as the site email address that 
messages sent by this plug are sent from.

### ckanext-initiatives

This extension overrides the "Request Access" button from ckanext-initiatives

### BPA Development Environment setup

```
docker exec -it dockercompose-bpa-ckan_ckan_1 /bin/bash
```

```
source /env/bin/activate
/docker-entrypoint.sh paster --plugin=ckanext-ytp-request initdb --config=/etc/ckan/default/ckan.ini
```

