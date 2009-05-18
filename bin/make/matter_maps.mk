# matter_peripheral.mk

# This file provides build rules for building all peripheral material,
# front and back, that might go into a Scripture publication. The
# rules will be laid out so that it will allow total flexibility as
# to if matter will be placed in the front or back. For example,
# it would be possible to put the copyright page in the back of the
# publication if necessary even though that is normally not done.
# Where components will be placed will be determined by the user
# as they layout the order in the Binding section of the project.ini
# file. That information is used to auto-build the process_instructions.mk
# file. That is the file that drives this one.
#
# It is possible to pick out one component and focus on that. Several
# generic rules will be provided for that.

# History:

# 20080925 - djd - Initial draft version.


##############################################################
#		Variables for peripheral matter
##############################################################

MATTER_MAPS_PDF		=
MATTER_MAPS_TEX		=

##############################################################
#		Map ID mapping information
##############################################################

# Maps are a special process. Each one listed here is a specific map.
# Definitions should be listed in the project.conf file
title_map		= TITLE_MAP
maps_map		= MAPS
m001_map		= M001
m002_map		= M002
m003_map		= M003
m004_map		= M004
m005_map		= M005
m006_map		= M006
m007_map		= M007
m008_map		= M008
m009_map		= M009
m010_map		= M010
m011_map		= M011


##############################################################
#		Rules for producing maps
##############################################################

# We'll do this similar to the peripheral process rules. First
# we will define a rule group for maps.

define map_rules

# We're going to start the map build process like the Scripture
# process, that's why there's a MAP for the ID. The make_map_file.py
# script will see to it that there is a Maps folder and a csv
# file for this map. It takes care of the copy process. It should
# be able to do this and if it can't it should tell us why.
$(PATH_MAPS)/$(1).svg : $(PATH_MAPS)
	cp $(PATH_MAPS_SOURCE)/$(1).svg $(PATH_MAPS)/$(1).svg

# Create a common project map translation file
$(PATH_MAPS_PROJECT)/$(1).csv ::
	@echo I just tried to blow a way your source file

#	cp $(PATH_MAPS_SOURCE)/$(1).csv $(PATH_MAPS_PROJECT)/$(1).csv

# Migrate the common project map translation file to the Maps folder
$(PATH_MAPS)/$(1).csv : $(PATH_MAPS) $(PATH_MAPS_PROJECT)/$(1).csv
	$(PY_PROCESS_SCRIPTURE_TEXT) migrate_map_file MAP $(PATH_MAPS_PROJECT)/$(1).csv $(PATH_MAPS)/$(1).csv

# Process the SVG file and edit it in Inkscape when it is done
# This prorocess has a double dependency in the following rules
# it will check each of them and run them in the order listed.
# Dependency #1
preprocess-$(1) :: $(PATH_MAPS)

# Dependency #2
preprocess-$(1) :: $(PATH_MAPS)/$(1).svg $(PATH_MAPS)/$(1).csv $(PATH_MAPS)/styles.csv
	@ FONTCONFIG_PATH=$(PATH_HOME)/$(PATH_FONTS) $(VIEWSVG) $$< &
	$(PY_PROCESS_SCRIPTURE_TEXT) make_map_file MAP $(PATH_MAPS)/$(1).svg

# Create the PDF version of the map
# This is dependent of other files in the process. A default version
# will be copied into the project Maps folder if one doesn't already
# exist there.
$(PATH_MAPS)/$(1).pdf : $(PATH_MAPS)/$(1).csv $(PATH_MAPS)/$(1).svg $(PATH_MAPS)/styles.csv
	@ FONTCONFIG_PATH=$(PATH_HOME)/$(PATH_FONTS) $(EXPORTSVG) -f $(PATH_MAPS)/$(1).svg -A $(PATH_MAPS)/$(1).pdf -T -F -d 2400


# Process the SVG file and view it in PDF when it is done
# This prorocess also has a double dependency in the following rules
# it will check each of them and run them in the order listed.
# Dependency #1
view-$(1) :: $(PATH_MAPS)

# Dependency #2
view-$(1) :: $(PATH_MAPS)/$(1).pdf
	@ $(VIEWPDF) $$< &

$(1) : $(PATH_MAPS)/$(1).svg


endef

##############################################################
#		Main processing rules
##############################################################

# First we need some rules to make sure the necessary files
# are in the right places

# Create a Maps folder if one isn't there already
$(PATH_MAPS) :
	mkdir -p $(PATH_MAPS)

# Move the styles.csv file over if it isn't there already
$(PATH_MAPS)/styles.csv : $(PATH_MAPS)
	cp $(PATH_MAPS_SOURCE)/styles.csv $(PATH_MAPS)/styles.csv


# This builds a rule (in memory) for all maps using the macro
# above. These will be called below when we process the
# individual items.

$(foreach v,$(MAP_IDS), $(eval $(call map_rules,$(v))))


###############################################################

ifneq ($(MAP_IDS),)
MATTER_MAPS_PDF		= $(PATH_MAPS)/MATTER_MAPS.pdf
MATTER_MAPS_TEX		= $(PATH_MAPS)/MATTER_MAPS.tex

# Create a TeX control file for building our book of maps
$(MATTER_MAPS_TEX) : $(foreach v,$(MAP_IDS), $(PATH_MAPS)/$(v).pdf)
	perl -e 'print "\\input $(TEX_PTX2PDF)\n\\input $(TEX_SETUP)\n"; for (@ARGV) {print "\\includepdf{$$_}\n"}; print "\n\\bye\n"' $(foreach v,$(MAP_IDS),$(v).pdf) > $@


$(MATTER_MAPS_PDF) : $(MATTER_MAPS_TEX)
	cd $(PATH_MAPS) && $(TEX_INPUTS) xetex $(MATTER_MAPS_TEX)

endif

# This will call TeX to create a "book" of maps. The results will
# be a PDF file that will be viewed in the PDF viewer.
view-maps : $(MATTER_MAPS_PDF)
	$(VIEWPDF) $< &
