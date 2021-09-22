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


## BPA Development Environment setup

```
docker exec -it dockercompose-bpa-ckan_ckan_1 /bin/bash
```

```
source /env/bin/activate
/docker-entrypoint.sh paster --plugin=ckanext-ytp-request initdb --config=/etc/ckan/default/ckan.ini
```

