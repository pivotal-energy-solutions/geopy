# Geopy - Generic Geocoder


geopy is a generic geocoder.

 * Adds in Google V3 Geocoder
 * Adds in Open Street Maps Geocoder
 * Returns real object with data back (rather than simply the lat/long)


####  Note:
_This fork provides for changes specifically for Pivotal Energy Solutions_


## CREDIT:

Initial code sits at http://code.google.com/p/geopy/
It was then forked to https://github.com/jbouvier/geopy
Finally it landed https://github.com/geopy/geopy

### Build Process:
1.  Update the `__version_info__` inside of the application. Commit and push.
2.  Tag the release with the version. `git tag <version> -m "Release"; git push --tags`
3.  Build the release `rm -rf dist build *egg-info; python setup.py sdist bdist_wheel`
4.  Upload the data `twine upload dist/*`

