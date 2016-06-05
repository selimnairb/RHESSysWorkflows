"""@package rhessysworkflows.command.giconverter

@brief RHESSysWorkflows commands related to parameterizing green infrastructure.

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
import os
import sys
import subprocess
import shlex
import importlib
import tempfile

from rhessysworkflows.command.base import GrassCommand
from rhessysworkflows.command.exceptions import MetadataException
from rhessysworkflows.command.exceptions import RunException

from rhessysworkflows.rhessys import RHESSysPaths
from rhessysworkflows.metadata import RHESSysMetadata

from rhessysworkflows.ginotebook import DEFAULT_HOSTNAME, DEFAULT_API_ROOT
from rhessysworkflows.ginotebook import GINotebook


class GIConverter(GrassCommand):

    def __init__(self, projectDir, configFile=None, outfp=sys.stdout):
        """ Construct a GIConverter command.
        Arguments:
        projectDir -- string    The path to the project directory
        configFile -- string    The path to an EcohydroLib configuration file
        outfp -- file-like object    Where output should be written to

        """
        super(GIConverter, self).__init__(projectDir, configFile, outfp)
        self.param_const = self.param_db = None
        self.paths = None

    def checkMetadata(self, *args, **kwargs):
        """ Check to make sure the project directory has the necessary metadata to run this command.
        """
        super(GIConverter, self).checkMetadata(args, kwargs)

        # Check for necessary information in metadata
        if not 'dem_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a DEM raster" % (self.context.projectDir,))
        if not 'soil_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a soil raster in a GRASS mapset" % (self.context.projectDir,))
        if not 'landcover_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a landcover raster" % (self.context.projectDir,))
        if not 'landuse_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a land use raster" % (self.context.projectDir,))
        if not 'stratum_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a stratum raster" % (self.context.projectDir,))
        if not 'patch_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a patch raster in a GRASS mapset" % (self.context.projectDir,))
        if not 'roads_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a roads raster" % (self.context.projectDir,))
        if not 'slope_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a slope raster" % (self.context.projectDir,))
        if not 'streams_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a stream raster" % (self.context.projectDir,))
        if not 'zero_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a zero raster" % (self.context.projectDir,))

        if not 'dem_srs' in self.studyArea:
            raise MetadataException("Metadata in project directory %s does not contain a DEM spatial reference system" % (self.context.projectDir,))
        if not 'dem_res_x' in self.studyArea:
            raise MetadataException("Metadata in project directory %s does not contain a DEM x resolution" % (self.context.projectDir,))
        if not 'dem_res_y' in self.studyArea:
            raise MetadataException("Metadata in project directory %s does not contain a DEM y resolution" % (self.context.projectDir,))

        if not 'grass_dbase' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS Dbase" % (self.context.projectDir,))
        if not 'grass_location' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS location" % (self.context.projectDir,))
        if not 'grass_mapset' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS mapset" % (self.context.projectDir,))
        if not 'rhessys_dir' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a RHESSys directory" % (self.self.context.projectDir,))
        if not 'cf_bin' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a createflowpaths executable" % (self.context.projectDir,))
        if not 'lairead_bin' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a lairead executable" % (self.context.projectDir,))
        if not 'allometric_table' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain an allometric table" % (self.context.projectDir,))
        if not 'template_template' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a template_template" % (self.context.projectDir,))
        if not 'climate_stations' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a list of climate stations" % (self.context.projectDir,))
        if not 'paramdb_dir' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a ParamDB directory" % (self.context.projectDir,))
        if not 'paramdb' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a ParamDB" % (self.context.projectDir,))

    def run(self, *args, **kwargs):
        """ Create flow tables for multiple worldfiles

        Arguments:
        scenario_id -- int    ID of the GI Notebook scenario whose GI instances are to be parameterized.
        auth_token -- string    Authorization token to use for authenticating to the GI Notebook.
        host -- string    Hostname of GI Notebook server. Default: None.
        api_root -- string    The root of the API URL to use. Default: None.
        use_HTTPS -- boolean    Use HTTPS for communication with the GI Notebook.
        force -- boolean        Force overwrite of existing scenario output. Default: False.
        verbose -- boolean    Produce verbose output. Default: False.
        """
        scenario_id = kwargs.get('scenario_id')
        if scenario_id is None:
            raise RunException('Scenario ID was not specified.')
        auth_token = kwargs.get('auth_token')
        if auth_token is None:
            raise RunException('Authorization token was not specified.')
        host = kwargs.get('host', DEFAULT_HOSTNAME)
        api_root = kwargs.get('api_path', DEFAULT_API_ROOT)
        use_HTTPS = kwargs.get('use_HTTPS', False)
        force = kwargs.get('force', False)
        verbose = kwargs.get('verbose', False)

        self.checkMetadata()
        self.param_const, self.param_db = self._init_paramdb()
        self.paths = RHESSysPaths(self.context.projectDir, self.metadata['rhessys_dir'])

        gi_scenario_base = 'gi_scenario'
        gi_scenario_data = "{0}.geojson".format(gi_scenario_base)
        scenario_geojson_path = os.path.join(self.context.projectDir, gi_scenario_data)
        gi_scenario_soils_base = "{0}_wsoils".format(gi_scenario_base)
        gi_scenario_soils = "{0}.geojson".format(gi_scenario_soils_base)
        scenario_soils_geojson_path = os.path.join(self.context.projectDir, gi_scenario_soils)
        gi_scenario_landuse_base = "{0}_landuse".format(gi_scenario_base)
        gi_scenario_landuse = "{0}.geojson".format(gi_scenario_landuse_base)
        scenario_landuse_geojson_path = os.path.join(self.context.projectDir, gi_scenario_landuse)
        gi_scenario_data_key = 'gi_scenario_data'
        gi_scenario_soils_data_key = "{0}_soils".format(gi_scenario_data_key)
        gi_scenario_landuse_data_key = "{0}_landuse".format(gi_scenario_data_key)
        if gi_scenario_data_key in self.metadata:
            if verbose:
                self.outfp.write('Existing GI scenario found.\n')
            if force:
                if verbose:
                    self.outfp.write('Force option specified, overwriting existing GI scenario.\n')
                if os.path.exists(scenario_geojson_path):
                    os.unlink(scenario_geojson_path)
                if os.path.exists(scenario_soils_geojson_path):
                    os.unlink(scenario_soils_geojson_path)
                if os.path.exists(scenario_landuse_geojson_path):
                    os.unlink(scenario_landuse_geojson_path)
            else:
                raise RunException('Exiting.  Use force option to overwrite.')

        if verbose:
            output = None
        else:
            output = open('/dev/null')
        try:
            # Connect to GI Notebook and fetch GI instance information (in GeoJSON format)
            # for this scenario ID.
            if verbose:
                self.outfp.write("\nDownloading GI scenario {0} from GI database...\n".format(scenario_id))
            nb = GINotebook(hostname=host,
                            api_root=api_root,
                            use_https=use_HTTPS, auth_token=auth_token)
            scenario = nb.get_scenario(scenario_id)
            scenario_geojson = scenario.get_instances_as_geojson(indent=2, shorten=True)
            (gi_scenario_data_wgs84, scenario_geojson_wgs84_path), (gi_scenario_data, scenario_geojson_path) = \
                self._write_geojson_and_reproject(scenario_geojson, gi_scenario_base, verbose=verbose, output=output)

            # Filter out instances that do not contain soils data
            gi_scenario_soils_base = "{0}_wsoils".format(gi_scenario_base)
            scenario_geojson_wsoils = scenario.get_instances_as_geojson(indent=2, shorten=True,
                                                                        filter=lambda a: a.get('e_1_pedid') is not None)
            (gi_scenario_soils_wgs84, scenario_soils_geojson_wgs84_path), (gi_scenario_soils, scenario_soils_geojson_path) = \
                self._write_geojson_and_reproject(scenario_geojson_wsoils, gi_scenario_soils_base,
                                                  verbose=verbose, output=output)

            # Import scenario GeoJSON into GRASS
            self._import_vector_into_grass(scenario_geojson_path, gi_scenario_data_key,
                                           force=force, verbose=verbose, output=output)

            # Import scenario (instances with soils data) GeoJSON into GRASS
            self._import_vector_into_grass(scenario_soils_geojson_path, gi_scenario_soils_data_key,
                                           force=force, verbose=verbose, output=output)

            # Generate raster layers from vector-based GI Scenario
            # Raster for updating soil type
            self._rasterize(gi_scenario_soils_data_key, gi_scenario_soils_data_key,
                            column='e_1_pedid', labelcolumn='e_1_pednm',
                            rast_title='GI soil types',
                            verbose=verbose,
                            force=force,
                            redir_fp=output)
            # Raster for updating stratum type
            gi_scenario_strata = "gi_scenario_strata"
            self._rasterize(gi_scenario_data_key, gi_scenario_strata,
                            column='e_1_vegid', labelcolumn='e_1_vegnm',
                            rast_title='GI vegetation types',
                            verbose=verbose,
                            force=force,
                            redir_fp=output)

            # Raster for updating land use
            # Filter out instances that are not rain gardens (i.e. the only GI type for which we currently have a
            #   land use).
            scenario_geojson_landuse = scenario.get_instances_as_geojson(indent=2, shorten=True,
                                                                         filter=lambda a: a.get('type',
                                                                                                '') == 'Rain Garden')
            (gi_scenario_landuse_wgs84, scenario_landuse_geojson_wgs84_path), \
            (gi_scenario_landuse, scenario_landuse_geojson_path) = \
                self._write_geojson_and_reproject(scenario_geojson_landuse, gi_scenario_landuse_base,
                                                  verbose=verbose, output=output)
            # Import land use (i.e. instances that are rain gardens) GeoJSON into GRASS
            self._import_vector_into_grass(scenario_landuse_geojson_path, gi_scenario_landuse_data_key,
                                           force=force, verbose=verbose, output=output)

            # Search for raster value for rain gardens in RHESSys parameter DB
            rg_name = 'raingarden'
            rg_found = self.param_db.search(self.param_const.SEARCH_TYPE_HIERARCHICAL, 'landuse', rg_name,
                                            None, None, None, None, None, None, None, None)
            if not rg_found:
                raise RunException("Unable to find raingarden landuse class in parameter database")

            rg_id = [c[1][2] for c in self.param_db.classes.iteritems()][0]

            # Generate raster layer from vector-based GI Scenario
            # Raster for updating landuse type
            self._rasterize_single_value(gi_scenario_landuse_data_key, gi_scenario_landuse_data_key,
                                         value=rg_id, label=rg_name,
                                         rast_title='GI landuse types',
                                         verbose=verbose,
                                         force=force,
                                         redir_fp=output)

            # Write out updated landuse, stratum, and soil rasters and parameter definitions
            # Backup landuse raster
            self._backup_raster(self.grassMetadata['landuse_rast'])
            # Update landuse raster
            self._update_raster(self.grassMetadata['landuse_rast'], gi_scenario_landuse_data_key)
            # Generate parameter definition file for landuse raster
            self._generate_parameter_definitions_for_raster(self.grassMetadata['landuse_rast'], 'landuse',
                                                            verbose=verbose)
            # Backup stratum raster
            self._backup_raster(self.grassMetadata['stratum_rast'])
            # Update stratum raster
            self._update_raster(self.grassMetadata['stratum_rast'], gi_scenario_strata)
            # Generate parameter definition file for stratum raster
            self._generate_parameter_definitions_for_raster(self.grassMetadata['stratum_rast'], 'stratum',
                                                            verbose=verbose)
            # Backup soils raster
            self._backup_raster(self.grassMetadata['soil_rast'])
            # Update soils raster
            self._update_raster(self.grassMetadata['soil_rast'], gi_scenario_soils_data_key)
            # Generate parameter definition file for soil raster
            self._generate_parameter_definitions_for_raster(self.grassMetadata['soil_rast'], 'soil',
                                                            verbose=verbose)
            # Write metadata
            RHESSysMetadata.writeGRASSEntry(self.context, "{0}_rast".format(gi_scenario_landuse_data_key),
                                            gi_scenario_landuse_data_key)
            RHESSysMetadata.writeGRASSEntry(self.context, "{0}_rast".format(gi_scenario_soils_data_key),
                                            gi_scenario_soils_data_key)
            RHESSysMetadata.writeGRASSEntry(self.context, "{0}_rast".format(gi_scenario_strata), gi_scenario_strata)

            RHESSysMetadata.writeGRASSEntry(self.context, "{0}_vect".format(gi_scenario_data_key), gi_scenario_data_key)
            RHESSysMetadata.writeGRASSEntry(self.context, "{0}_vect".format(gi_scenario_soils_data_key),
                                            gi_scenario_soils_data_key)
            RHESSysMetadata.writeGRASSEntry(self.context, "{0}_vect".format(gi_scenario_landuse_data_key),
                                            gi_scenario_landuse_data_key)
            RHESSysMetadata.writeRHESSysEntry(self.context, gi_scenario_data_key, gi_scenario_data)

            if verbose:
                self.outfp.write('\n\nFinished parameterizing GI.\n')

            # Write processing history
            RHESSysMetadata.appendProcessingHistoryItem(self.context, RHESSysMetadata.getCommandLine())

        finally:
            if output:
                output.close()

    def _rasterize_single_value(self, input, output, value, label, rast_title,
                                verbose=False, force=False, redir_fp=None):
        if verbose:
            self.outfp.write("\nRasterizing {title}...\n".format(title=rast_title))

        p = self.grassLib.script.start_command('v.to.rast',
                                               input=input,
                                               output=output,
                                               use='val',
                                               value=value,
                                               overwrite=force,
                                               quiet=not verbose,
                                               stdout=redir_fp,
                                               stderr=redir_fp)
        rc = p.wait()
        if rc != 0:
            raise RunException("Unable to rasterize {title}; v.to.rast returned {rc}".format(title=rast_title,
                                                                                             rc=rc))

        rule_file = tempfile.NamedTemporaryFile(delete=False)
        rule_file_name = rule_file.name
        rule_file.write("{value}:{label}\n".format(value=value, label=label))
        rule_file.close()

        p = self.grassLib.script.start_command('r.category',
                                               map=output,
                                               rules=rule_file_name)
        rc = p.wait()
        if rc != 0:
            raise RunException("Unable to assign category to raster {rast}; r.category returned {rc}".format(rast=output,
                                                                                                             rc=rc))
        os.unlink(rule_file_name)

    def _rasterize(self, input, output, column, labelcolumn, rast_title,
                   verbose=False, force=False, redir_fp=None):
        if verbose:
            self.outfp.write("\nRasterizing {title}...\n".format(title=rast_title))

        # Select only those GI instances that have information for column
        input_extract = "{input}_extract".format(input=input)
        p = self.grassLib.script.start_command('v.extract',
                                               input=input,
                                               output=input_extract,
                                               overwrite=True, # Temporary value, always overwrite
                                               quiet=not verbose,
                                               stdout=redir_fp,
                                               stderr=redir_fp)
        rc = p.wait()
        if rc != 0:
            raise RunException("Unable to extract features; v.extract returned {rc}".format(rc=rc))

        p = self.grassLib.script.start_command('v.to.rast',
                                               input=input_extract,
                                               output=output,
                                               column=column,
                                               labelcolumn=labelcolumn,
                                               overwrite=force,
                                               quiet=not verbose,
                                               stdout=redir_fp,
                                               stderr=redir_fp)
        rc = p.wait()
        if rc != 0:
            raise RunException("Unable to rasterize {title}; v.to.rast returned {rc}".format(title=rast_title,
                                                                                             rc=rc))
        # Remove extract vector
        p = self.grassLib.script.start_command('g.remove',
                                               flags='f',
                                               vect=input_extract,
                                               quiet=not verbose,
                                               stdout=redir_fp,
                                               stderr=redir_fp)
        rc = p.wait()
        if rc != 0:
            raise RunException("Unable to clean up {vect}; g.remove returned {rc}".format(vect=input_extract,
                                                                                          rc=rc))

    def _write_geojson_and_reproject(self, geojson, filename_base, verbose=False, output=None):
        # Write GeoJSON to file in project directory
        geojson_wgs84 = "{0}_wgs84.geojson".format(filename_base)
        geojson_wgs84_path = os.path.join(self.context.projectDir, geojson_wgs84)
        f = open(geojson_wgs84_path, 'w')
        f.writelines(geojson)
        f.close()

        # Reproject scenario data from WGS84 into our coordinate system (using ogr2ogr)
        geojson_reproj = "{0}.geojson".format(filename_base)
        geojson_reproj_path = os.path.join(self.context.projectDir, geojson_reproj)
        t_srs = self.studyArea['dem_srs']
        if verbose:
            self.outfp.write("\nReprojecting {file} to {srs}...\n".format(file=geojson_wgs84, srs=t_srs))
        path_to_ogr_cmd = self.context.config.get('GDAL/OGR', 'PATH_OF_OGR2OGR')
        ogr_cmd = "{ogr} -overwrite -f GeoJSON -t_srs {t_srs} {dest} {src}".format(ogr=path_to_ogr_cmd,
                                                                                   t_srs=t_srs,
                                                                                   dest=geojson_reproj_path,
                                                                                   src=geojson_wgs84_path)
        args = shlex.split(ogr_cmd)
        # Send output to /dev/null so that we don't see the spurious error that OGR
        # can't write GeoJSON files, when it seems to create ours just fine
        p = subprocess.Popen(args, stdout=output, stderr=output)
        rc = p.wait()
        if rc != 0:
            raise RunException("GI Instance re-project command {0} returned {1}".format(ogr_cmd,
                                                                                        rc))
        return (geojson_wgs84, geojson_wgs84_path), (geojson_reproj, geojson_reproj_path)

    def _import_vector_into_grass(self, vector_input, vector_output, force=False, verbose=False, output=None):
        if verbose:
                self.outfp.write('\nImporting GI scenario data into GRASS...\n')
        p = self.grassLib.script.start_command('v.in.ogr',
                                               dsn=vector_input,
                                               output=vector_output,
                                               overwrite=force,
                                               quiet=not verbose,
                                               stdout=output,
                                               stderr=output)
        rc = p.wait()
        if rc != 0:
            raise RunException("Unable to import {vect} into GRASS; v.in.ogr returned {rc}".format(vect=vector_input,
                                                                                     rc=rc))

    def _init_paramdb(self):
        param_db_path = os.path.join(self.context.projectDir, self.metadata['paramdb'])
        if not os.access(param_db_path, os.R_OK):
            sys.exit("Unable to read RHESSys parameters database {0}".format(param_db_path))
        param_db_path = os.path.abspath(param_db_path)

        sys.path.append( os.path.join(self.context.projectDir, self.metadata['paramdb_dir']) )
        params = importlib.import_module('rhessys.params')
        param_const = importlib.import_module('rhessys.constants')
        param_db = params.paramDB(filename=param_db_path)

        return (param_const, param_db)

    def _backup_raster(self, raster_name,
                       verbose=False, force=False, output=None):
        backup_name = "{0}_backup".format(raster_name)
        arg = "{0},{1}".format(raster_name, backup_name)

        if verbose:
                self.outfp.write("\nBacking up raster {rast} to {backup}\n".format(rast=raster_name,
                                                                                   backup_name=backup_name))
        p = self.grassLib.script.start_command('g.copy',
                                               rast=arg,
                                               overwrite=True,
                                               quiet=not verbose,
                                               stdout=output,
                                               stderr=output)
        rc = p.wait()
        if rc != 0:
            raise RunException("Unable to backup {rast}; g.copy returned {rc}".format(rast=raster_name,
                                                                                      rc=rc))

    def _update_raster(self, dest_raster, src_raster,
                      verbose=False, force=False, output=None):
        # Read category values of dest_ and src_raster
        raster_vals_list = self._read_raster_categories((dest_raster, src_raster))
        raster_vals = {}
        for cat_vals in raster_vals_list:
            for key in cat_vals:
                raster_vals[key] = cat_vals[key]
        mapcalc_expr = '$dest=if(!isnull($src), $src, $dest)'
        # import pdb; pdb.set_trace()
        self.grassLib.script.raster.mapcalc(mapcalc_expr, dest=dest_raster, src=src_raster,
                                            verbose=verbose)
        self._update_raster_categories(dest_raster, raster_vals, verbose=verbose, output=output)

    def _read_raster_categories(self, rasters,
                                verbose=False, output=None):
        raster_vals_list = []
        for raster in rasters:
            raster_vals = {}
            raster_vals_list.append(raster_vals)
            pipe = self.grassLib.script.pipe_command('r.stats', flags='licn', input=raster)
            for line in pipe.stdout:
                (dn, cat, num) = line.strip().split()
                if cat != 'NULL':
                    raster_vals[cat] = int(dn)
            pipe.wait()
        return raster_vals_list

    def _update_raster_categories(self, raster_name, cat_dict,
                                  verbose=False, output=None):
        rules_str = '\n'.join(["{cat}:{label}".format(cat=cat_dict[k], label=k) for k in cat_dict])
        rules_str += '\n'
        rule_file = tempfile.NamedTemporaryFile(delete=False)
        rule_file_name = rule_file.name
        rule_file.write(rules_str)
        rule_file.close()
        p = self.grassLib.script.start_command('r.category', map=raster_name, rules=rule_file_name,
                                               verbose=verbose)
        rc = p.wait()
        os.unlink(rule_file_name)
        if rc != 0:
            raise RunException("Unable to update categories for raster {rast}; r.category returned {rc}".format(rast=raster_name,
                                                                                                                rc=rc))

    def _generate_parameter_definitions_for_raster(self, raster_name, raster_type_name,
                                                   verbose=False):
        pipe = self.grassLib.script.pipe_command('r.stats', flags='licn', input=raster_name)
        raster_vals = {}
        for line in pipe.stdout:
            (dn, cat, num) = line.strip().split()
            if cat != 'NULL':
                raster_vals[cat] = int(dn)
        pipe.wait()
        if verbose:
            self.outfp.write("Writing GI {0} definition files to {1}".format(raster_type_name,
                                                                             self.paths.RHESSYS_DEF))
        for key in raster_vals.keys():
            if verbose:
                self.outfp.write("\n{rast_type} '{cat}' has dn {dn}".format(rast_type=raster_type_name,
                                                                            cat=key, dn=raster_vals[key]))
            params_found = self.param_db.search(self.param_const.SEARCH_TYPE_HIERARCHICAL, None, key, None, None, None,
                                                None, None, None, None, None,
                                                defaultIdOverride=raster_vals[key])
            assert(params_found)
            self.param_db.writeParamFileForClass(self.paths.RHESSYS_DEF)