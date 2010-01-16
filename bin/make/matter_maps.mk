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
# 20090909 - te - Some debugging work was done to fix a problem
#		with a python script not being called. More needs
#		to be done on this and other make file scripts to
#		make them more concise in the way the exicute.
# 20090914 - djd - Removed some double dependency rules to simplify
#		the process. Also removed the dependency for
#		pdf generation. The process will fail if preprocessing
#		has not been done. The reason is that there is
#		a proceedure conflict between maps and books.
# 20090923 - djd - Added the link-maps command to make created linked
#		files easier.
# 20091201 - djd - Changed references for MAP_IDS to MATTER_MAPS to
#		reflect changes in the rest of the system
# 20100113 - djd - Added code for processing maps with seperate
#		style files
# 20100116 - djd - Did a virtual rewrite on the process. It is now
#		more consistant with the rest of the processes.


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
$(PATH_TEXTS)/$(1)-map.svg : \
	$(PATH_TEXTS)/$(1)-data.csv \
	$(PATH_TEXTS)/$(1)-styles.csv \
	$(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-org.png
	@echo WARNING: Map: $(PATH_TEXTS)/$(1)-map.svg not found adding default to project.
	@cp $(PATH_MAP_TEMPLATES)/$(1)-map.svg $(PATH_TEXTS)/$(1)-map.svg

$(PATH_TEXTS)/$(1)-map-post.svg : $(PATH_TEXTS)/$(1)-map.svg
	@echo INFO: Merging map data and styles into $(shell readlink -f -- $(PATH_TEXTS)/$(1)-map-post.svg)
	@$(PY_PROCESS_SCRIPTURE_TEXT) make_map_file MAP $(PATH_TEXTS)/$(1)-map.svg

# Copy project map style file into project
# Question: How would you prevent makefile from copying over the
# the project style file if one already existed but the one in
# the library has been updated. We don't want to blow away any
# project data.
$(PATH_TEXTS)/$(1)-styles.csv :
	@echo WARNING: Map style data: $(PATH_TEXTS)/$(1)-styles.csv not found adding default to project.
	@cp $(PATH_MAP_TEMPLATES)/$(1)-styles.csv $(PATH_TEXTS)/$(1)-styles.csv

# Copy the map reference file to the peripheral-map source folder
# This is for refering to when the map data is being translated
$(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-org.png :
	@echo INFO: Map reference file: $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-org.png is being copied to project.
	@cp $(PATH_MAP_TEMPLATES)/$(1)-org.png $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-org.png

# Create a common project map translation (data) file
$(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-data.csv :
	@echo WARNING: Map tranlation data: $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-data.csv not found adding default to project.
	@cp $(PATH_MAP_TEMPLATES)/$(1)-data.csv $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-data.csv

# Link the project map data translation file to the Texts folder.
# We link it to prevent changes from being made that might cause
# confusion in the process. This way there is only one file to
# manage. Previously, there was a process in place that would
# convert the map label data in the CSV to a specified encoding.
# This was for multi-script projects. This added complications to
# the process that hindered efficient processing on non-multi-script
# projects. Just for the record the command for this was:
# migrate_map_file.py. This process has been deprecated for the most
# part. For the rare multi-script project, a less automated means
# will be needed to generate the original map label data.
# BTW, we use readlink here to resolve the path so the ln will make
# a successful link.
$(PATH_TEXTS)/$(1)-data.csv : $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-data.csv
	@echo INFO: Linking data for: $(shell pwd)/$(PATH_TEXTS)/$(1)-data.csv
	@ln -sf $(shell readlink -f -- $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-data.csv) $(PATH_TEXTS)/

# Create the initial PDF version of the map
# This will transform the svg file to the initial PDF file.
# To typeset to to final form a second process must be run.
# This is just the first step in the total process.
# This process has a dependency on the map.svg file.
# However, it is not explicitly stated in the rule because
# there is an editing process that must take place between
# the check and the view processes.
$(PATH_PROCESS)/$(1)-map-pre.pdf : $(PATH_TEXTS)/$(1)-map-post.svg
	@echo INFO: Creating: $(PATH_PROCESS)/$(1)-map-pre.pdf
	@ FONTCONFIG_PATH=$(PATH_HOME)/$(PATH_FONTS) $(EXPORTSVG) -f $(PATH_TEXTS)/$(1)-map-post.svg -A $(PATH_PROCESS)/$(1)-map-pre.pdf

# When the View-Maps button is clicked this will create the
# USFM file that will be called from the .tex file. One is
# auto-created for each map that is to be processed.
$(PATH_TEXTS)/$(1)-map.usfm : $(PATH_PROCESS)/$(1)-map-pre.pdf
	@echo INFO: Creating: $(PATH_TEXTS)/$(1)-map.usfm
	@echo \\id OTH > $$@
	@echo \\ide UTF-8 >> $$@
	@echo \\singlecolumn >> $$@
	@echo \\periph Map Page >> $$@
	@echo \\startmaps >> $$@
	@echo '\\makedigitsother%' >> $$@
	@echo '\\catcode`{=1\\catcode`}=2\\catcode`#=6%' >> $$@
	@echo '\\def\\domap#1{\\vbox to \\the\\textheight{\\vfil\\noindent\\hfil\\XeTeXpdffile #1 width \\the\\textwidth \\hfil\\par\\vfil}\\eject}%' >> $$@
	@echo '\\catcode `@=12' >> $$@
	@echo '\\domap{$(1)-map-pre.pdf}' >> $$@
	@echo '\\bye' >> $$@

# This is the .tex file that is necessary to process the
# map .usfm file. This is created when the View-Maps button
# is clicked. This is dependent on the .usfm file
$(PATH_PROCESS)/$(1)-map.tex : $(PATH_TEXTS)/$(1)-map.usfm
	@echo INFO: Creating: $(PATH_TEXTS)/$(1)-map.tex
	@echo \\input $(TEX_PTX2PDF) > $$@
	@echo \\input $(TEX_SETUP) >> $$@
	@echo \\input BACK_MATTER.tex >> $$@
	@echo \\def\\TopMarginFactor{0.4} >> $$@
	@echo \\ptxfile{$(PATH_TEXTS)/$(1)-map.usfm} >> $$@
	@echo '\\bye' >> $$@

# Create the typeset PDF version of the map
# This is the second step for creating the final map file.
# The rule here will call on TeX to process the map TeX file,
# creating a final version of the map ready for the final
# process, binding. This is dependent on the map.tex process.
$(PATH_PROCESS)/$(1)-map.pdf : $(PATH_PROCESS)/$(1)-map.tex
	@echo INFO: Creating: $(PATH_PROCESS)/$(1)-map.pdf
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(PATH_PROCESS)/$(1)-map.tex

# This will run all the preprocesses to the SVG file and
# open it up in Inkscape (or any other designated SVG editor)
# when the processes are done. When this is run it is
# assumed that there is no need for the files that generated
# after so they will be deleted. This is similar behavior
# as with book file processing.
# This should be done before the view process is done but
# a dependency does exist that will enable everything to
# be done with the view process, but it may not be pretty.
preprocess-$(1) : $(PATH_TEXTS)/$(1)-map-post.svg
	@rm -f $(PATH_PROCESS)/$(1)-map-pre.pdf
	@rm -f $(PATH_PROCESS)/$(1)-map.pdf
	@FONTCONFIG_PATH=$(PATH_HOME)/$(PATH_FONTS) $(VIEWSVG) $(PATH_TEXTS)/$(1)-map-post.svg &

# Process the SVG file and view it in PDF when it is done. Note that this
# process will fail if the preprocess has not been run first. The map making
# process differs from typesetting so it has to be this way for now.
view-$(1) :: $(PATH_PROCESS)/$(1)-map.pdf
	@echo INFO: Creating final typeset map: $(PATH_PROCESS)/$(1)-map.pdf
	@ $(VIEWPDF) $(PATH_PROCESS)/$(1)-map.pdf &

# Remove the current map PDF file
pdf-remove-$(1) :
	@echo WARNING: Removing: $(shell readlink -f -- $(PATH_PROCESS)/$(1)-map-pre.pdf) and $(shell readlink -f -- $(PATH_PROCESS)/$(1)-map.pdf)
	@rm -f $(PATH_PROCESS)/$(1)-map-pre.pdf
	@rm -f $(PATH_PROCESS)/$(1)-map.pdf

# Edit the CSV data file
edit-data-$(1) : $(PATH_TEXTS)/$(1)-data.csv
	$(EDITCSV) $(PATH_TEXTS)/$(1)-data.csv

# Edit the CSV style file
edit-style-$(1) : $(PATH_TEXTS)/$(1)-styles.csv
	$(EDITCSV) $(PATH_TEXTS)/$(1)-styles.csv

# Delete (clean out) this set of files
delete-$(1) :
	@echo WARNING: Removing all the files for the $(1) map set
	@rm -f $(PATH_PROCESS)/$(1)*
	@rm -f $(PATH_TEXTS)/$(1)*

endef

##############################################################
#		Main processing rules
##############################################################

# First we need some rules to make sure the necessary files
# are in the right places

# This builds a rule (in memory) for all maps using the macro
# above. These will be called below when we process the
# individual items.

$(foreach v,$(MATTER_MAPS), $(eval $(call map_rules,$(v))))

###############################################################

ifneq ($(MATTER_MAPS),)
MATTER_MAPS_PDF		= $(PATH_PROCESS)/MATTER_MAPS.pdf

# For binding we will use pdftk to put together the
# individual PDFs we created earlier in this process.
$(MATTER_MAPS_PDF) : $(foreach v,$(MATTER_MAPS),$(PATH_PROCESS)/$(v)-map.pdf)
	@echo INFO: Creating the TeX control file: $(MATTER_MAPS_PDF)
	pdftk $(foreach v,$(MATTER_MAPS),$(PATH_PROCESS)/$(v)-map.pdf) cat output $@

endif

# This will call TeX to create a "book" of maps. The results will
# be a PDF file that will be viewed in the PDF viewer.
view-maps : $(MATTER_MAPS_PDF)
	@echo INFO: Creating a single PDF file for all the maps.
	@$(VIEWPDF) $< &

# Remove the matter map file
pdf-remove-maps :
	@echo INFO: Removing file: $(MATTER_MAPS_PDF)
	@rm -f $(MATTER_MAPS_PDF)

# This kind of works. It will bring up a fresh version of all
# the maps, one at a time. You have to close Inkscape on each
# one before it will move on to the next.
preprocess-maps :
	@echo INFO: Running the preprocess on all maps.
	$(foreach v,$(MATTER_MAPS), $(shell make preprocess-$(v)))

# Do a total reset of all the map files
clean-maps :
	@echo WARNING: All map have been deleted, Sorry if you did not mean to do this
	$(foreach v,$(MATTER_MAPS), $(shell rm -f $(PATH_TEXTS)/$(v)* && rm -f $(PATH_PROCESS)/$(v)*))
	@rm -f $(MATTER_MAPS_PDF)
