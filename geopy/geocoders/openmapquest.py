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

class OpenMapQuest(Geocoder):
    """Geocoder using the MapQuest Open Platform Web Services."""

    def __init__(self, api_key='', format_string='%s'):
        """Initialize an Open MapQuest geocoder with location-specific
        address information, no API Key is needed by the Nominatim based
        platform.

        ``format_string`` is a string containing '%s' where the string to
        geocode should be interpolated before querying the geocoder.
        For example: '%s, Mountain View, CA'. The default is just '%s'.
        """

        self.api_key = api_key
        self.format_string = format_string
        self.url = "http://open.mapquestapi.com/nominatim/v1/search?format=json&%s"

    def geocode(self, string, exactly_one=True, timeout=None):

        self.search_string = string
        params = {
            'q': self.format_string % self.search_string,
            'addressdetails': 1

        }
        self.url = self.url % urlencode(params)
        logger.debug("Fetching %s..." % self.url)

        kwargs = dict(url=self.url)
        if timeout and sys.version_info > (2,6,0): kwargs['timeout'] = timeout
        page = urlopen(**kwargs)

        return self.parse_json(page, exactly_one)

    def _parse_result(self, resource):
        location = resource['display_name']

        latitude = resource['lat'] or None
        longitude = resource['lon'] or None
        if latitude and longitude:
            latitude = float(latitude)
            longitude = float(longitude)

        return (location, (latitude, longitude))


    def parse_json(self, page, exactly_one=True):
        """Parse display name, latitude, and longitude from an JSON response."""
        if not isinstance(page, basestring):
            page = decode_page(page)
        resources = json.loads(page)

        if exactly_one and len(resources) != 1:
            raise ValueError("Didn't find exactly one result! " \
                             "(Found %d.)" % len(resources))

        if exactly_one and len(resources) == 1:
            return self._parse_result(resources[0])
        else:
            return [self._parse_result(resource) for resource in resources]
