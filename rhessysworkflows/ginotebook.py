"""@package rhessysworkflows.ginotebook

@brief Tools that enable interaction with GI Database:
https://github.com/ResearchSoftwareInstitute/ginotebook

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2016, University of North Carolina at Chapel Hill
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the University of North Carolina at Chapel Hill nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF NORTH CAROLINA AT CHAPEL HILL
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


@author Brian Miles <brian_miles@unc.edu>
"""
import json
from collections import OrderedDict

import requests

from .compat import http_responses


DEFAULT_HOSTNAME = 'gidesigner.renci.org'
DEFAULT_API_ROOT = 'ginotebook/api'

GI_TYPE_RAIN_GARDEN = 'Rain Garden'
GI_TYPE_TREE = 'Tree'
GI_TYPE_GREEN_ROOF = 'Green roof'
GI_TYPES = (GI_TYPE_RAIN_GARDEN, GI_TYPE_TREE, GI_TYPE_GREEN_ROOF)


class GINotebookException(Exception):
    def __init__(self, args):
        super(GINotebookException, self).__init__(args)


class GINotebookHTTPException(GINotebookException):
    """ Exception used to communicate HTTP errors from GI Notebook server
        Arguments in tuple passed to constructor must be: (url, status_code, params).
        url and status_code are of type string, while the optional params argument
        should be a dict.
    """
    def __init__(self, args):
        super(GINotebookHTTPException, self).__init__(args)
        self.url = args[0]
        self.method = args[1]
        self.status_code = args[2]
        if len(args) >= 4:
            self.params = args[3]
        else:
            self.params = None

    def __str__(self):
        msg = "Received status {status_code} {status_msg} when accessing {url} " + \
              "with method {method} and params {params}."
        return msg.format(status_code=self.status_code,
                          status_msg=http_responses[self.status_code],
                          url=self.url,
                          method=self.method,
                          params=self.params)

    def __unicode__(self):
        return unicode(str(self))


class GINotebookIntegrityError(GINotebookException):
    def __init__(self, args):
        super(GINotebookIntegrityError, self).__init__(args)
        self.obj_url1 = args[0]
        self.obj_url2 = args[1]
        self.field = args[2]

    def __str__(self):
        msg = "Expected {obj1} but got {obj2} for {field}."
        return msg.format(obj1=self.obj_url1, obj2=self.obj_url2, field=self.field)

    def __unicode__(self):
        return unicode(str(self))


class RHESSysDefaultType(object):
    """ Represents a RHESSys parameter default type (e.g. soil, stratum)
    """
    def __init__(self, id, url, name, rhessys_default_id):
        self.id = id
        self.url = url
        self.name = name
        self.rhessys_default_id = rhessys_default_id


class SoilType(RHESSysDefaultType):
    """ Represents a SoilType as presented by the GI Notebook rhessys_soil_types REST API end point
    """
    def __init__(self, id, url, name, rhessys_default_id):
        super(SoilType, self).__init__(id, url, name, rhessys_default_id)


class StratumType(RHESSysDefaultType):
    """ Represents a StratumType as presented by the GI Notebook rhessys_stratum_types REST API end point
    """
    def __init__(self, id, url, name, rhessys_default_id):
        super(StratumType, self).__init__(id, url, name, rhessys_default_id)


class GIElement(object):
    """ Represents a GI Element as presented by the GI Notebook gi_element REST API end point
    """
    def __init__(self, id, url, name, model_3d_url, model_planview_url, soil_depth, ponding_depth,
                 major_axis, minor_axis,
                 stratum_type=None, soil_type=None):
        self.id = id
        self.url = url
        self.name = name
        self.model_3d_url = model_3d_url
        self.model_planview_url = model_planview_url
        self.soil_depth = soil_depth
        self.ponding_depth = ponding_depth
        self.major_axis = major_axis
        self.minor_axis = minor_axis
        self.stratum_type = stratum_type
        self.soil_type = soil_type

    def get_properties(self, dict_to_use=None, key_prefix=None, shorten=False):
        """ Generate a dict consisting of the properties of a GIElement.

        @param: dict_to_use: The dict to store properties in.  If None, a new dict will be created.
        @param: key_prefix: Prefix to be prepended onto each key name.  Prefix will be separate from the
        rest of the key by "_".
        @param: shorten: Use short names for properties if True.
        @return: Dict of properties.
        """
        if dict_to_use:
            p = dict_to_use
        else:
            p = {}

        temp = OrderedDict()
        temp['id'] = self.id
        temp['url'] = self.url
        temp['name'] = self.name

        if shorten:
            soil_depth = 'pedz'
            ponding_depth = 'pondz'
            major_axis = 'majax'
            minor_axis = 'minax'
            stratum_name = 'vegnm'
            stratum_default_id = 'vegid'
            soil_name = 'pednm'
            soil_default_id = 'pedid'
        else:
            soil_depth = 'soil_depth'
            ponding_depth = 'ponding_depth'
            major_axis = 'major_axis'
            minor_axis = 'minor_axis'
            stratum_name = 'stratum_name'
            stratum_default_id = 'stratum_default_id'
            soil_name = 'soil_name'
            soil_default_id = 'soil_default_id'

        temp[soil_depth] = self.soil_depth
        temp[ponding_depth] = self.ponding_depth
        temp[major_axis] = self.major_axis
        temp[minor_axis] = self.minor_axis
        if self.stratum_type:
            temp[stratum_name] = self.stratum_type.name
            temp[stratum_default_id] = int(self.stratum_type.rhessys_default_id)
        if self.soil_type:
            temp[soil_name] = self.soil_type.name
            temp[soil_default_id] = int(self.soil_type.rhessys_default_id)

        if key_prefix:
            # Re-write values with keys prefixed by key_prefix
            temp = {"{0}_{1}".format(key_prefix, k): v for (k, v) in temp.iteritems()}

        p.update(temp)

        return p


class GITemplate(object):
    """ Represents a GI Template as presented by the GI Notebook gi_template REST API end point
    """
    def __init__(self, id, url, name, gi_type, model_3d_url, model_planview_url):
        self.id = id
        self.url = url
        self.name = name
        self.gi_type = gi_type
        self.model_3d_url = model_3d_url
        self.model_planview_url = model_planview_url
        self.gi_elements = []

    def add_element(self, gi_element):
        """ Associate an instance with this template

        @param gi_element: A GIElement object
        @return:
        """
        self.gi_elements.append(gi_element)

    def get_properties(self, dict_to_use=None, flatten=True, shorten=False):
        """ Generate a dict consisting of the properties of a GIInstance.

        @param: dict_to_use: The dict to store properties in.  If None, a new dict will be created.
        @param: flatten: If False, properties of elements contained in template will be written
        to their own dict with key "element_<id>".  If True, element properties will be stored directly
        in the template properties dict, with "element_<id>_" prepended to each property name.
        @param: shorten: Use short names for properties if True.
        @return: Dict of properties.
        """
        if dict_to_use:
            p = dict_to_use
        else:
            p = {}

        if shorten:
            template_id = 'templt_id'
            template_url = 'templt_url'
            elements = 'elements'
        else:
            template_id = 'template_id'
            template_url = 'template_url'
            elements = 'elements'

        p[template_id] = self.id
        p[template_url] = self.url
        p['type'] = self.gi_type

        if not flatten:
            elems = []
            p[elements] = elems

        for i, element in enumerate(self.gi_elements, 1):
            if flatten:
                if shorten:
                    key = "e_{0}".format(i)
                else:
                    key = "element_{0}".format(i)
                element.get_properties(dict_to_use=p, key_prefix=key, shorten=shorten)
            else:
                elements.append(element.get_properties())

        return p


class GIInstance(object):
    """ Represents a GI Instance as presented by the GI Notebook gi_instance REST API end point
    """
    def __init__(self, id, url, placement_poly, poly_area_sq_meter, scenario=None, template=None):
        """

        @param id:
        @param url:
        @param placement_poly: WGS 84 polygon (a dict representation of the GeoJSON)
        @param poly_area_sq_meter: The area of placement_poly in square meters
        @param scenario: A GIScenario object
        @param template: A GITemplate object
        @return:
        """
        self.id = id
        self.url = url
        self.placement_poly = placement_poly
        self.poly_area_sq_meter = poly_area_sq_meter
        self.scenario = scenario
        self.template = template

    def get_as_geojson_feature(self, flatten=True, shorten=False, filter=None):
        """ Generate a dict representing a GIInstance as a GeoJSON Feature

        @param: flatten If True, compound properties will be flattened into a single namespace such that
        all properties values are simple strings.  This allows GIS clients to easily interpret feature properties.
        If False, properties values may be any JSON object.
        @param: shorten: Use short names for properties if True.
        @param: filter If flatten is True, filter should be a function that takes as input a dictionary
        and returns True if the items in the dictionary pass the filter, False if not.
        @return: Dict representing a GeoJSON Feature.
        """
        if shorten:
            poly_area_sq_meter = 'area_sq_m'
            instance_id = 'inst_id'
            instance_url = 'inst_url'
        else:
            poly_area_sq_meter = 'poly_area_sq_meter'
            instance_id = 'instance_id'
            instance_url = 'instance_url'

        p = OrderedDict([(poly_area_sq_meter, self.poly_area_sq_meter),
                         (instance_id, self.id), (instance_url, self.url)])
        if self.template:
            p = self.template.get_properties(p, flatten=flatten, shorten=shorten)

        feature = None
        filter_pass = True
        if flatten and filter:
            if not filter(p):
                filter_pass = False

        if filter_pass:
            feature = OrderedDict([('type', 'Feature'), ('id', self.id),
                                    ('geometry', self.placement_poly),
                                    ('properties', p)])
        return feature


class GIScenario(object):
    """ Represents a GI Scenario as presented by the GI Notebook gi_scenario REST API end point
    """
    def __init__(self, id, url, name, description, immutable, watershed_url):
        """

        @param id:
        @param url:
        @param name:
        @param description:
        @param immutable:
        @param watershed_url:
        @return:
        """
        self.id = id
        self.url = url
        self.name = name
        self.description = description
        self.immutable = immutable
        self.watershed_url = watershed_url
        self.gi_instances = []

    def add_instance(self, gi_instance):
        """ Associate a GIInstance with this scenario

        @param gi_instance: A GIInstance object
        @return:
        """
        gi_instance.scenario = self
        self.gi_instances.append(gi_instance)

    def get_instances_as_geojson(self, indent=None, flatten=True, shorten=False,
                                 filter=None):
        """ Generate a GeoJSON FeatureCollection representing all GI Instances associated with a scenario.

        @param: indent Integer by which JSON output will be indented for pretty printing
        @param: flatten If True, compound properties will be flattened into a single namespace such that
        all properties values are simple strings.  This allows GIS clients to easily interpret feature properties.
        If False, properties values may be any JSON object.
        @param: shorten Use short names for properties if True.
        @param: filter If flatten is True, filter should be a function that takes as input a dictionary
        and returns True if the items in the dictionary pass the filter, False if not.
        @return: String in GeoJSON format
        """
        features = []
        feature_collection = OrderedDict([('type', 'FeatureCollection'), ('features', features)])
        for instance in self.gi_instances:
            feature = instance.get_as_geojson_feature(flatten=flatten, shorten=shorten, filter=filter)
            if feature is not None:
                features.append(feature)

        return json.dumps(feature_collection, indent=indent)


class GINotebook(object):
    """ Class that allows interaction with GI Database:
        https://github.com/ResearchSoftwareInstitute/ginotebook

    """
    _URL_PROTO_WITHOUT_PORT = "{scheme}://{hostname}/{api_root}"
    _URL_PROTO_WITH_PORT = "{scheme}://{hostname}:{port}/{api_root}"

    def __init__(self, hostname=DEFAULT_HOSTNAME, api_root=DEFAULT_API_ROOT,
                 port=None, use_https=True, verify=True, auth_token=None):
        self.hostname = hostname
        self.verify = verify

        self.session = None
        self.auth_header = {}
        if auth_token:
            self.auth_header['Authorization'] = "Token {token}".format(token=auth_token)

        if use_https:
            self.scheme = 'https'
        else:
            self.scheme = 'http'
        self.use_https = use_https

        if port:
            self.port = int(port)
            if self.port < 0 or self.port > 65535:
                raise GINotebookException("Port number {0} is illegal.".format(self.port))
            self.url_base = self._URL_PROTO_WITH_PORT.format(scheme=self.scheme,
                                                             hostname=self.hostname,
                                                             port=self.port,
                                                             api_root=api_root)
        else:
            self.url_base = self._URL_PROTO_WITHOUT_PORT.format(scheme=self.scheme,
                                                                hostname=self.hostname,
                                                                api_root=api_root)

    def _request(self, method, url, params=None, data=None, files=None, headers=None, stream=False):
        if headers:
            h = dict(headers)
            h.update(self.auth_header)
        else:
            h = dict(self.auth_header)

        r = requests.request(method, url, params=params, data=data, files=files, headers=h, stream=stream,
                             verify=self.verify)
        return r

    def _get_resource(self, endpoint, id=None, url=None):
        if id:
            url = "{url_base}/{endpoint}/{id}/".format(url_base=self.url_base, endpoint=endpoint, id=id)
        elif not url:
            GINotebookException("Resource URL not specified")

        r = self._request('GET', url)
        if r.status_code != 200:
            raise GINotebookHTTPException((url, 'GET', r.status_code))
        return r.json()

    def get_scenario(self, id=None, url=None):
        """ Get GIScenario resource from the GI Notebook

        @param id: The ID of the GIScenario resource to download from the GI Notebook
        @param url: The URL of the GIScenario resource to download from the GI Notebook
        @return: GIScenario instance representing the resource
        """
        raw = self._get_resource('gi_scenarios', id=id, url=url)
        scenario = GIScenario(raw['id'], raw['url'], raw['name'], raw['description'], raw['immutable'],
                              raw['watershed'])
        for instance_url in raw['giinstances']:
            instance = self.get_instance(url=instance_url)
            scenario.add_instance(instance)

        return scenario

    def get_instance(self, id=None, url=None):
        """ Get GIInstance resource from the GI Notebook

        @param id: The ID of the GIInstance resource to download from the GI Notebook
        @param url: The URL of the GIInstance resource to download from the GI Notebook
        @return: GIInstance instance representing the resource
        """
        raw = self._get_resource('gi_instances', id=id, url=url)
        template = self.get_template(url=raw['template'])
        instance = GIInstance(raw['id'], raw['url'], raw['placement_poly'], raw['placement_poly_area_sq_m'],
                              template=template)

        return instance

    def get_template(self, id=None, url=None):
        """ Get GITemplate resource from the GI Notebook

        @param id: The ID of the GITemplate resource to download from the GI Notebook
        @param url: The URL of the GITemplate resource to download from the GI Notebook
        @return: GITemplate instance representing the resource
        """
        raw = self._get_resource('gi_templates', id=id, url=url)
        gi_type = self.get_type(url=raw['gi_type'])
        template = GITemplate(raw['id'], raw['url'], raw['name'], gi_type,
                              raw['model_3d'], raw['model_planview'])
        for element_url in raw['gi_elements']:
            element = self.get_element(url=element_url)
            template.add_element(element)

        return template

    def get_type(self, id=None, url=None):
        """ Get GI type resource from the GI Notebook

        @param id: The ID of the GI type resource to download from the GI Notebook
        @param url: The URL of the GI type resource to download from the GI Notebook
        @return: String representing the GI type
        """
        raw = self._get_resource('gi_types', id=id, url=url)

        return raw['name']

    def get_element(self, id=None, url=None):
        """ Get GIElement resource from the GI Notebook

        @param id: The ID of the GIElement resource to download from the GI Notebook
        @param url: The URL of the GIElement resource to download from the GI Notebook
        @return: GIElement instance representing the resource
        """
        raw = self._get_resource('gi_elements', id=id, url=url)
        stratum_type = None
        if raw['stratum_type']:
            stratum_type = self.get_stratum_type(url=raw['stratum_type'])
        soil_type = None
        if raw['soil_type']:
            soil_type = self.get_soil_type(url=raw['soil_type'])
        element = GIElement(raw['id'], raw['url'], raw['name'],
                            raw['model_3d'], raw['model_planview'],
                            raw['soil_depth'], raw['ponding_depth'],
                            raw['major_axis'], raw['minor_axis'],
                            stratum_type, soil_type)

        return element

    def get_stratum_type(self, id=None, url=None):
        """ Get StratumType resource from the GI Notebook

        @param id: The ID of the StratumType resource to download from the GI Notebook
        @param url: The URL of the StratumType resource to download from the GI Notebook
        @return: StratumType instance representing the resource
        """
        raw = self._get_resource('rhessys_stratum_types', id=id, url=url)
        stratum_type = StratumType(raw['id'], raw['url'], raw['name'],
                                   raw['rhessys_default_id'])

        return stratum_type

    def get_soil_type(self, id=None, url=None):
        """ Get SoilType resource from the GI Notebook

        @param id: The ID of the SoilType resource to download from the GI Notebook
        @param url: The URL of the SoilType resource to download from the GI Notebook
        @return: SoilType instance representing the resource
        """
        raw = self._get_resource('rhessys_stratum_types', id=id, url=url)
        soil_type = SoilType(raw['id'], raw['url'], raw['name'],
                             raw['rhessys_default_id'])

        return soil_type
