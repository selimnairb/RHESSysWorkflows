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
import requests


DEFAULT_HOSTNAME = 'gidesigner.renci.org'
DEFAULT_API_ROOT = 'ginotebook/api/'

GI_TYPE_RAIN_GARDEN = 'Rain Garden'
GI_TYPE_TREE = 'Tree'
GI_TYPE_GREEN_ROOF = 'Green roof'
GI_TYPES = (GI_TYPE_RAIN_GARDEN, GI_TYPE_TREE, GI_TYPE_GREEN_ROOF)


class GINotebookException(Exception):
    def __init__(self, args):
        super(GINotebookException, self).__init__(args)


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
    def __init__(self, url, name, rhessys_default_id):
        super(SoilType, self).__init__(id, url, name, rhessys_default_id)



class StratumType(object):
    """ Represents a StratumType as presented by the GI Notebook rhessys_stratum_types REST API end point
    """
    def __init__(self, url, name, rhessys_default_id):
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


class GIInstance(object):
    """ Represents a GI Instance as presented by the GI Notebook gi_instance REST API end point
    """
    def __init__(self, id, url, placement_poly, scenario=None, template=None):
        """

        @param id:
        @param url:
        @param scenario: A GIScenario object
        @param template: A GITemplate object
        @param placement_poly: WGS 84 polygon (a dict representation of the GeoJSON)
        @return:
        """
        self.id = id
        self.url = url
        self.placement_poly = placement_poly
        self.scenario = scenario
        self.template = template


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
            self.auth_header['Authorization'] = "access_token {token}".format(token=auth_token)

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

    def request(self, method, url, params=None, data=None, files=None, headers=None, stream=False):
        if headers:
            h = dict(headers)
            h.update(self.auth_header)
        else:
            h = dict(self.auth_header)

        r = requests.request(method, url, params=params, data=data, files=files, headers=h, stream=stream,
                             verify=self.verify)
        return r