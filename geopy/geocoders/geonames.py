import xml.dom.minidom
from urllib import urlencode
from urllib2 import urlopen
import sys
from geopy import util

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json

from geopy.geocoders.base import Geocoder

class GeoNames(Geocoder):
    def __init__(self, format_string=None, output_format=None, country_bias=None):
        if format_string != None:
            from warnings import warn
            warn('geopy.geocoders.geonames.GeoNames: The `format_string` parameter is deprecated.'+
                ' (It has always been ignored for GeoNames.)', DeprecationWarning)
        if output_format != None:
            from warnings import warn
            warn('geopy.geocoders.geonames.GeoNames: The `output_format` parameter is deprecated '+
                 'and now ignored.', DeprecationWarning)
        
        self.country_bias = country_bias
        self.url = "http://ws.geonames.org/searchJSON?%s"
    
    def geocode(self, string, exactly_one=True, timeout=None):
        params = {
            'q': string
        }
        if self.country_bias:
            params['countryBias'] = self.country_bias
        
        url = self.url % urlencode(params)
        return self.geocode_url(url, exactly_one, timeout=None)
    
    def geocode_url(self, url, exactly_one=True, timeout=None):

        kwargs = dict(url=url)
        if timeout and sys.version_info > (2,6,0): kwargs['timeout'] = timeout
        page = urlopen(**kwargs)

        return self.parse_json(page, exactly_one)

    def _parse_result(self, place):
        latitude = place.get('lat', None)
        longitude = place.get('lng', None)
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)
        else:
            return None

        placename = place.get('name')
        state = place.get('adminCode1', None)
        country = place.get('countryCode', None)

        location = ', '.join(filter(lambda x: bool(x),
            [placename, state, country]
        ))

        return (location, (latitude, longitude))


    def parse_json(self, page, exactly_one):
        if not isinstance(page, basestring):
            page = util.decode_page(page)
            
        doc = json.loads(page)
        places = doc.get('geonames', [])
        
        if not places:
            return None
        
        if exactly_one and len(places) != 1:
            raise ValueError("Didn't find exactly one result! " \
                             "(Found %d.)" % len(places))

        if exactly_one:
            return self._parse_result(places[0])
        else:
            return [self._parse_result(place) for place in places]
