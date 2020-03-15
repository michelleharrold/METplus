"""

SeriesByInit: Basic Use Case
=========================================================================

This METplus SeriesByInit use case will run the MET Series Analysis tool
and is similar to the Feature Relative Use Case in the
model_application/medium_range weather area. 

"""

#############################################################################
# Scientific Objective
# --------------------
#
# By grouping the statistical information by the initialization time
# as a series (as opposed to grouping by geographical/grid locations), model
# differences specific to weather systems and model initialization can be discovered.

##############################################################################
# Datasets
# --------
#
#
# Input is the output of ExtractTiles, SERIES_ANALYSIS_INPUT_DIR.
#
# | **Forecast:** 
# |     extract_tiles/20141214_00
# | **Observation:** N/A
#
# | **Location:** All of the input data required for this use case can be found in the met_test sample data tarball. Click here to the METplus releases page and download sample data for the appropriate release: https://github.com/NCAR/METplus/releases
# | The tarball should be unpacked into the directory that you will set the value of INPUT_BASE. See 'Running METplus' section for more information.
#
# | **Data Source:** Unknown

##############################################################################
# METplus Components
# ------------------
#
# This use case utilizes the METplus SeriesByLead wrapper to search for
# files that are valid at a given run time and generate a command to run
# the MET tool series_analysis.
#
# Typically, running SeriesByInit will involve running the following METplus
# wrapper tasks in the following order, TcPairs, ExtractTiles, SeriesByInit.
# However, this use case example will run only SeriesByInit, therefore it
# uses sample data input from the output of already having run ExtractTiles. 

##############################################################################
# METplus Workflow
# ----------------
#
# Running SeriesByInit invokes the following MET tools: tc_stat, regrid_dataplane, 
# plot_data_plane and the following executables: convert.
#
# This example processes the following run times:
#
# | **Init:** 2014-12-14_00Z

##############################################################################
# METplus Configuration
# ---------------------
#
# METplus first loads all of the configuration files found in parm/metplus_config,
# then it loads any configuration files passed to METplus via the command line
# with the -c option, i.e. -c /path/to/SeriesByInit.conf
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/use_cases/met_tool_wrapper/SeriesByInit/SeriesByInit.conf

##############################################################################
# MET Configuration
# ---------------------
#
# METplus sets environment variables based on the values in the METplus configuration file.
# These variables are referenced in the MET configuration file. **YOU SHOULD NOT SET ANY OF THESE ENVIRONMENT VARIABLES YOURSELF! THEY WILL BE OVERWRITTEN BY METPLUS WHEN IT CALLS THE MET TOOLS!** If there is a setting in the MET configuration file that is not controlled by an environment variable, you can add additional environment variables to be set only within the METplus environment using the [user_env_vars] section of the METplus configuration files. See the 'User Defined Config' section on the 'System Configuration' page of the METplus User's Guide for more information.
#
# .. highlight:: bash
# .. literalinclude:: ../../../../parm/met_config/SeriesAnalysisConfig_seriesby_wrapped
#
# Note the following variables are referenced in the MET configuration file.
#
# * **${REGRID_TO_GRID}** - Corresponds to SERIES_ANALYSIS_REGRID_TO_GRID in the METplus configuration file.
# * **${NAME}** - forecast or obs field information. Generated from BOTH_VAR<n>_NAME in the METplus configuration file.
# * **${LEVEL}** - forecast or obs field information. Generated from BOTH_VAR<n>_LEVELS in the METplus configuration file.
# * **${STAT_LIST}** - Corresponds to SERIES_ANALYSIS_STAT_LIST in the METplus configuration file.


##############################################################################
# Running METplus
# ---------------
#
# It is recommended to run this use case by:
#
# Passing in SeriesByLead.conf then a user-specific system configuration file::
#
#   master_metplus.py -c /path/to/SeriesByInit.conf -c /path/to/user_system.conf
#
# The following METplus configuration variables must be set correctly to run this example.:
#
# * **INPUT_BASE** - Path to directory where sample data tarballs are unpacked (See Datasets section to obtain tarballs).
# * **OUTPUT_BASE** - Path where METplus output will be written. This must be in a location where you have write permissions
# * **MET_INSTALL_DIR** - Path to location where MET is installed locally
#
# Example User Configuration File::
#
#   [dir]
#   INPUT_BASE = /path/to/sample/input/data
#   OUTPUT_BASE = /path/to/output/dir
#   MET_INSTALL_DIR = /path/to/met-X.Y 
#
# **NOTE:** All of these items must be found under the [dir] section.
#

##############################################################################
# Expected Output
# ---------------
#
# A successful run will output the following both to the screen and to the logfile::
#
#   INFO: METplus has successfully finished running.
#
# Refer to the value set for **OUTPUT_BASE** to find where the output data was generated.
# Output for this use case will be found in **SERIES_ANALYSIS_OUTPUT_DIR** (relative to **OUTPUT_BASE**)
# and will contain the following files:
#
# * 20141214_00/
#
#   * ML1200942014/
#
#     * ANLY_ASCII_FILES_ML1200942014
#     * FCST_ASCII_FILES_ML1200942014
#     * series_TMP_Z2_FBAR.png
#     * series_TMP_Z2_FBAR.ps
#     * series_TMP_Z2_ME.png
#     * series_TMP_Z2_ME.ps
#     * series_TMP_Z2.nc
#     * series_TMP_Z2_OBAR.png
#     * series_TMP_Z2_OBAR.ps
#     * series_TMP_Z2_TOTAL.png
#     * series_TMP_Z2_TOTAL.ps
#  
# AND each directory contains the same set of files, as above, for each directory time.
#
#   * ML1200972014/
#   * ML1200992014/
#   * ML1201002014/
#   * ML1201032014/
#   * ML1201042014/
#   * ML1201052014/
#   * ML1201062014/
#   * ML1201072014/
#   * ML1201082014/
#   * ML1201092014/
#   * ML1201102014/


##############################################################################
# Keywords
# --------
#
# .. note:: `SeriesByInitUseCase <https://ncar.github.io/METplus/search.html?q=SeriesByInitUseCase&check_keywords=yes&area=default>`_, `SeriesAnalysisUseCase <https://ncar.github.io/METplus/search.html?q=SeriesAnalysisUseCase&check_keywords=yes&area=default>`_
