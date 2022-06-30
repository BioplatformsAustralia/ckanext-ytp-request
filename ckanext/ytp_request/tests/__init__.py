from ckanext.ytp_request.model import tables_exist, init_tables


def ytp_request_db_setup():
    if not tables_exist():
        init_tables()
