import sys

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json
try:
    from django.utils.http import urlencode
except ImportError:
    from urllib import urlencode

from urllib2 import urlopen

from geopy.geocoders.base import Geocoder
from geopy.util import logger, decode_page, join_filter

class Bing(Geocoder):
    """Geocoder using the Bing Maps API."""

    def __init__(self, api_key, format_string='%s', output_format=None):
        """Initialize a customized Bing geocoder with location-specific
        address information and your Bing Maps API key.

        ``api_key`` should be a valid Bing Maps API key.

        ``format_string`` is a string containing '%s' where the string to
        geocode should be interpolated before querying the geocoder.
        For example: '%s, Mountain View, CA'. The default is just '%s'.

        ``output_format`` (DEPRECATED) is ignored
        """
        if output_format != None:
            from warnings import warn
            warn('geopy.geocoders.bing.Bing: The `output_format` parameter is deprecated '+
                 'and ignored.', DeprecationWarning)

        self.api_key = api_key
        self.format_string = format_string
        self.include_neighborhood = False
        self.url = "http://dev.virtualearth.net/REST/v1/Locations?%s"

    def geocode(self, string, exactly_one=True, region=None, include_neighborhood=False,
                timeout=None):

        self.search_string = string
        params = {'query': self.format_string % self.search_string,
                  'key': self.api_key
                  }
        if region:
            params['countryRegion'] = region
        if include_neighborhood: params['inclnb'] = 1
        self.url = self.url % urlencode(params)
        return self.geocode_url(self.url, exactly_one, timeout=timeout)

    def geocode_url(self, url, exactly_one=True, timeout=None):
        logger.debug("Fetching %s..." % url)

        kwargs = dict(url=url)
        if timeout and sys.version_info > (2,6,0): kwargs['timeout'] = timeout
        page = urlopen(**kwargs)

        return self.parse_json(page, exactly_one)

    def _parse_result(self, resource):
        stripchars = ", \n"
        a = resource['address']

        address = a.get('addressLine', '').strip(stripchars)
        city = a.get('locality', '').strip(stripchars)
        state = a.get('adminDistrict', '').strip(stripchars)
        zipcode = a.get('postalCode', '').strip(stripchars)
        country = a.get('countryRegion', '').strip(stripchars)

        city_state = join_filter(", ", [city, state])
        place = join_filter(" ", [city_state, zipcode])
        location = join_filter(", ", [address, place, country])

        latitude = resource['point']['coordinates'][0] or None
        longitude = resource['point']['coordinates'][1] or None
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)

        return (location, (latitude, longitude))

    def parse_json(self, page, exactly_one=True):
        """Parse a location name, latitude, and longitude from an JSON response."""
        if not isinstance(page, basestring):
            page = decode_page(page)
        doc = json.loads(page)
        resources = doc['resourceSets'][0]['resources']

        if exactly_one and len(resources) != 1:
            raise ValueError("Didn't find exactly one resource! " \
                             "(Found %d.)" % len(resources))

        if exactly_one:
            return self._parse_result(resources[0])
        else:
            return [self._parse_result(resource) for resource in resources]
