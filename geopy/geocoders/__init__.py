from geopy.geocoders.bing import Bing
from geopy.geocoders.google import Google
from geopy.geocoders.googlev3 import GoogleV3
from geopy.geocoders.dot_us import GeocoderDotUS
from geopy.geocoders.geonames import GeoNames
from geopy.geocoders.wiki_gis import MediaWiki
from geopy.geocoders.wiki_semantic import SemanticMediaWiki
from geopy.geocoders.yahoo import Yahoo
from geopy.geocoders.openmapquest import OpenMapQuest

class Place(object):
    """This represents a place

    This is a generic container to hold a "place".  It's intended to be used with overriding
    the XXX method for a geocoder.  This will then give you access to more attributes of a
    geo-coded object in a consistent manner than simply (location (lat, long))."""

    def __init__(self, *args, **kwargs):
        self.street_line1 = kwargs.get('street_line1', None)
        self.street_line2 = kwargs.get('street_line2', None)
        self.suite =  kwargs.get('suite', None)
        self.street_number =  kwargs.get('street_number', None)
        self.route =  kwargs.get('route', None)
        self.city =  kwargs.get('city', None)
        self.state =  kwargs.get('state', None)
        self.zipcode =  kwargs.get('zipcode', None)
        self.county =  kwargs.get('county', None)
        self.neighborhood =  kwargs.get('neighborhood', None)
        self.latitude =  kwargs.get('latitude', None)
        self.longitude =  kwargs.get('longitude', None)
        self.is_confirmed =  kwargs.get('is_confirmed', False)
        self.formatted_address =  kwargs.get('formatted_address', None)
        self.subdivision_id = kwargs.get('subdivision_id', None)
        self.errors = []
        self.warnings = []

    def __unicode__(self):
        return self.formatted_address

    def __repr__(self):
        results = []
        if not self.formatted_address:
            return 'Unknown'
        for i in self.formatted_address:
            try: results.append(i.encode('ascii'))
            except UnicodeEncodeError: results.append("?")
        return "".join(results)

    def get_home_object(self):
        """This return the dictionary needed for a home"""
        subdivision, city, county = None, None, None
        if self.county:
            try:
                county = County.objects.get(name__iexact=self.county,
                                            state = self.state)
            except ObjectDoesNotExist:
                self.errors.append("%s county does not exist in %s" % (self.county,
                                                                       self.state))
        else:
            self.errors.append("County not given")
        if self.subdivision_id:
            from apps.subdivision.models import Subdivision
            try:
                subdivision = Subdivision.objects.get(id=self.subdivision_id)
            except ObjectDoesNotExist:
                error = "Unable to find subdivision id %s" % self.subdivision_id
                log.errors(error)
                self.errors.append(error)

        try:
            if hasattr(county, 'name') and self.city:
                city = City.objects.get(name__iexact=self.city, county=county)
        except ObjectDoesNotExist:
            if self.is_confirmed:
                warning = ("%s (%s) does not exist - adding it" % (self.city,
                                                                   self.county))

                city = get_or_create_unregistered_city(name=self.city,
                                                       county=county,
                                                       latitude=self.latitude,
                                                       longitude=self.longitude)
            else:
                error = "The city %s does not exist within %s county" % (self.city ,
                                                                         self.county)
                self.errors.append(error)
                log.error(error)

        errors = None
        if len(self.errors):
            errors = "<ul>"
            for item in self.errors: errors += "<li>%s</li>" % item
            errors += "</ul>"

        return dict(street_line1=self.street_line1, lot_number=self.lot_number,
                    street_line2=self.street_line2, city=city,
                    state=self.state, zipcode=self.zipcode,
                    confirmed_address=self.is_confirmed, latitude=self.latitude,
                    longitude = self.longitude, subdivision=subdivision,
                    errors = errors)
