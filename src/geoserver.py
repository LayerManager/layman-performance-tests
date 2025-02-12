import requests
from owslib import wms as owslib_wms

WMS_VERSION = '1.3.0'


def wms_direct(wms_url, xml=None, version=None, headers=None):
    version = version or WMS_VERSION
    try:
        wms = owslib_wms.WebMapService(wms_url, xml=xml.encode('utf-8') if xml is not None else xml, version=version, headers=headers)
    except requests.exceptions.HTTPError as exc:
        if exc.response.status_code == 404:
            return None
        raise exc
    except AttributeError as exc:
        if exc.args == ("'NoneType' object has no attribute 'find'",):
            return None
        raise exc
    return wms