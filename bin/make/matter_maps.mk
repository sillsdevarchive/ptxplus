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
# 20100125 - djd - Added ability to process map graphic files
#		that have been created by an external process
# 20100202 - djd - Added auto CMYK conversion ability


##############################################################
#		Rules for producing maps
##############################################################

# We'll do this similar to the peripheral process rules. First
# we will define a rule group for maps.

define map_rules

# If the CREATE_MAP var is set to 0 this will enable the
# first set of rules to be acted on which enable the automated
# creation of SVG maps based on templates in the library.
# Otherwise, there is a set of rules that enable the use of
# existing maps that are kept in the Source/Maps-ID folder.


ifneq ($(CREATE_MAP),0)

# We're going to start the map build process like the Scripture
# process, that's why there's a MAP for the ID. The make_map_file.py
# script will see to it that there is a Maps folder and a csv
# file for this map. It takes care of the copy process. It should
# be able to do this and if it can't it should tell us why.
$(PATH_TEXTS)/$(1)-map.svg : \
	$(PATH_TEXTS)/$(1)-data.csv \
	$(PATH_TEXTS)/$(1)-styles.csv \
	$(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-org.png
	@echo INFO: Map $(1): Adding necessary files to project
	@cp $(PATH_MAP_TEMPLATES)/$(1)-map.svg $$@

$(PATH_TEXTS)/$(1)-map-post.svg : | $(PATH_TEXTS)/$(1)-map.svg
	@echo INFO: Merging map data and styles into $$(shell readlink -f -- $(PATH_TEXTS)/$(1)-map-post.svg)
	@$(PY_PROCESS_SCRIPTURE_TEXT) make_map_file MAP $(PATH_TEXTS)/$(1)-map.svg $$@

# Copy project map style file into project
$(PATH_TEXTS)/$(1)-styles.csv :
	@echo WARNING: Map style data: $$@ not found adding default to project.
	@cp $(PATH_MAP_TEMPLATES)/$(1)-styles.csv $$@

# Copy the map reference file to the peripheral-map source folder
# This is for refering to when the map data is being translated
$(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-org.png :
	@echo INFO: Map reference file: $$@ is being copied to project.
	@cp $(PATH_MAP_TEMPLATES)/$(1)-org.png $$@

# Create a common project map translation (data) file
$(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-data.csv :
	@echo WARNING: Map tranlation data: $$@ not found adding default to project.
	@cp $(PATH_MAP_TEMPLATES)/$(1)-data.csv $$@

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
	@echo INFO: Linking data for: $$(shell pwd)/$$@
	@ln -sf $$(shell readlink -f -- $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-data.csv) $(PATH_TEXTS)/

# When the View-Maps button is clicked this will create the
# USFM file that will be called from the .tex file. One is
# auto-created for each map that is to be processed. This is
# specifically for the RGB version of the map.
$(PATH_TEXTS)/$(1)-map-page-rgb.usfm :
	@echo INFO: Creating: $$@
	@echo \\id OTH > $$@
	@echo \\ide UTF-8 >> $$@
	@echo \\singlecolumn >> $$@
	@echo \\periph Map Page >> $$@
	@echo \\startmaps >> $$@
	@echo '\\makedigitsother%' >> $$@
	@echo '\\catcode`{=1\\catcode`}=2\\catcode`#=6%' >> $$@
	@echo '\\def\\domap#1{\\vbox to \\the\\textheight{\\vfil\\noindent\\hfil\\XeTeXpdffile #1 width \\the\\textwidth \\hfil\\par\\vfil}\\eject}%' >> $$@
	@echo '\\catcode `@=12' >> $$@
	@echo '\\domap{$(1)-map-rgb.pdf}' >> $$@
	@echo '\\bye' >> $$@

# When the cmyk-<mapID> command is given this will create the
# USFM file that will be called from the cmyk.tex file. One is
# auto-created for each map that is to be processed.
$(PATH_TEXTS)/$(1)-map-page-cmyk.usfm :
	@echo INFO: Creating: $$@
	@echo \\id OTH > $$@
	@echo \\ide UTF-8 >> $$@
	@echo \\singlecolumn >> $$@
	@echo \\periph Map Page >> $$@
	@echo \\startmaps >> $$@
	@echo '\\makedigitsother%' >> $$@
	@echo '\\catcode`{=1\\catcode`}=2\\catcode`#=6%' >> $$@
	@echo '\\def\\domap#1{\\vbox to \\the\\textheight{\\vfil\\noindent\\hfil\\XeTeXpdffile #1 width \\the\\textwidth \\hfil\\par\\vfil}\\eject}%' >> $$@
	@echo '\\catcode `@=12' >> $$@
	@echo '\\domap{$(1)-map-cmyk.pdf}' >> $$@
	@echo '\\bye' >> $$@

# This is the .tex file that is necessary to process the
# map .usfm file. This is created when the View-Maps button
# is clicked. This is dependent on the .usfm file
$(PATH_PROCESS)/$(1)-map-page-rgb.tex : | $(PATH_PROCESS)/BACK_MATTER.tex
	@echo INFO: Creating: $$@
	@echo \\input $(TEX_PTX2PDF) > $$@
	@echo \\input $(TEX_SETUP) >> $$@
	@echo \\input BACK_MATTER.tex >> $$@
	@echo \\def\\TopMarginFactor{0.4} >> $$@
	@echo \\ptxfile{$(PATH_TEXTS)/$(1)-map-page-rgb.usfm} >> $$@
	@echo '\\bye' >> $$@

# This is the .tex file that is necessary to process the
# map cmyk.usfm file. This is created when the cmyk-<mapID>
# command is given. This is dependent on the cmyk.usfm file
$(PATH_PROCESS)/$(1)-map-page-cmyk.tex : | $(PATH_PROCESS)/BACK_MATTER.tex
	@echo INFO: Creating: $$@
	@echo \\input $(TEX_PTX2PDF) > $$@
	@echo \\input $(TEX_SETUP) >> $$@
	@echo \\input BACK_MATTER.tex >> $$@
	@echo \\def\\TopMarginFactor{0.4} >> $$@
	@echo \\ptxfile{$(PATH_TEXTS)/$(1)-map-page-cmyk.usfm} >> $$@
	@echo '\\bye' >> $$@

# Create the typeset PDF version of the map
# This is the second step for creating the final map file.
# The rule here will call on TeX to process the map TeX file,
# creating a final version of the map ready for the final
# process, binding. This is dependent on the map.png process.
$(PATH_PROCESS)/$(1)-map-page-rgb.pdf : \
	$(PATH_PROCESS)/$(1)-map-rgb.pdf \
	$(PATH_PROCESS)/$(1)-map-page-rgb.tex \
	$(PATH_TEXTS)/$(1)-map-page-rgb.usfm
	@echo INFO: Creating: $$@
	@rm -f $(PATH_PROCESS)/$(1)-map.pdf
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(PATH_PROCESS)/$(1)-map-page-rgb.tex

# This process creates a PDF of the CMYK PNG file that was
# created in an earlier process. The PNG file is an intermediat
# step in the process.
$(PATH_PROCESS)/$(1)-map-page-cmyk.pdf : \
	$(PATH_PROCESS)/$(1)-map-cmyk.pdf \
	$(PATH_PROCESS)/$(1)-map-page-cmyk.tex \
	$(PATH_TEXTS)/$(1)-map-page-cmyk.usfm
	@echo INFO: Creating: $$@
	@rm -f $(PATH_PROCESS)/$(1)-map-page-cmyk.pdf
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(PATH_PROCESS)/$(1)-map-page-cmyk.tex

# Create the intermediate PDF version of the map
# This will transform the svg file to the initial PDF file.
# To typeset to to final form a second process must be run.
# This is just the first step in the total process.
# This process has a dependency on the map-post.svg file.
$(PATH_PROCESS)/$(1)-map-rgb.pdf : $(PATH_TEXTS)/$(1)-map-post.svg
	@echo INFO: Creating: $$@
	@rm -f $(PATH_PROCESS)/$(1)-map-rgb.pdf
	@ FONTCONFIG_PATH=$(PATH_HOME)/$(PATH_FONTS) $(EXPORTSVG) --file=$(PATH_TEXTS)/$(1)-map-post.svg --export-pdf=$$@

# Create the intermediate PNG file for the CMYK color space
# conversion by ImageMagick. This is done this way because the
# path out of Inkscape (which is what creates this file) is
# better than trying to do it all with ImageMagick. We convert
# SVG to PNG/RGB, then in the next step go PNG to PDF/CMYK.
$(PATH_PROCESS)/$(1)-map-rgb.png : $(PATH_TEXTS)/$(1)-map-post.svg
	@echo INFO: Creating: $$@
	@rm -f $(PATH_PROCESS)/$(1)-map-rgb.png
	@ FONTCONFIG_PATH=$(PATH_HOME)/$(PATH_FONTS) $(EXPORTSVG) --file=$(PATH_TEXTS)/$(1)-map-post.svg --export-png=$$@

# This is the process for creating a CMYK version of the
# current map and outputs to PDF. It uses ImageMagick for this.
# This is the second step of a two step process to get from
# SVG/RGB to PDF/CMYK. The PNG file is an intermediate step
# and has been created by Inkscape from the source SVG file.
$(PATH_PROCESS)/$(1)-map-cmyk.pdf : $(PATH_PROCESS)/$(1)-map-rgb.png
	@echo INFO: Creating: $$@
	@convert png:$(PATH_PROCESS)/$(1)-map-rgb.png -profile '$(RGB_PROFILE)' -profile $(CMYK_PROFILE) -compress zip -units PixelsPerInch -define pdf:use-cropbox=true pdf:$$@

# This will run all the preprocesses to the SVG file and
# open it up in Inkscape (or any other designated SVG editor)
# when the processes are done. When this is run it is
# assumed that there is no need for the files that generated
# after so they will be deleted. This is similar behavior
# as with book file processing. The default color space
# output is RGB. A special command is availible for CMYK.
preprocess-$(1) : $(PATH_TEXTS)/$(1)-map-post.svg
	@echo INFO: Creating or editing $(PATH_TEXTS)/$(1)-map-post.svg
	@rm -f $(PATH_PROCESS)/$(1)-map-page-rgb.pdf
	@FONTCONFIG_PATH=$(PATH_HOME)/$(PATH_FONTS) $(VIEWSVG) $(PATH_TEXTS)/$(1)-map-post.svg &

# Process the SVG file and view it in PDF when it is done. Note that this
# process will fail if the preprocess has not been run first. The map making
# process differs from typesetting so it has to be this way to protect data.
view-$(1) : $(PATH_PROCESS)/$(1)-map-page-rgb.pdf
	@echo INFO: Creating final typeset map: $(PATH_PROCESS)/$(1)-map-page-rgb.pdf
	@ $(VIEWPDF) $(PATH_PROCESS)/$(1)-map-page-rgb.pdf &

# Convert the intermediat PNG file to a CMYK color profile
cmyk-$(1) : $(PATH_PROCESS)/$(1)-map-page-cmyk.pdf
	@echo INFO: Creating CMYK color profile map: $(PATH_PROCESS)/$(1)-map-page-cmyk.pdf
	@ $(VIEWPDF) $(PATH_PROCESS)/$(1)-map-page-cmyk.pdf &

# Remove the current map PDF file
pdf-remove-$(1) :
	@echo WARNING: Removing: $$(shell readlink -f -- $(PATH_PROCESS)/$(1)-map-page-rgb.pdf) and $$(shell readlink -f -- $(PATH_PROCESS)/$(1)-map.pdf)
	@rm -f $(PATH_PROCESS)/$(1)-map-page-rgb.pdf
	@rm -f $(PATH_PROCESS)/$(1)-map-page-cmyk.pdf

# Edit the CSV data file
edit-data-$(1) : $(PATH_TEXTS)/$(1)-data.csv
	$(EDITCSV) $(PATH_TEXTS)/$(1)-data.csv

# Edit the CSV style file
edit-styles-$(1) : $(PATH_TEXTS)/$(1)-styles.csv
	$(EDITCSV) $(PATH_TEXTS)/$(1)-styles.csv

# View the original model map
view-model-$(1) : $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-org.png
	$(VIEWIMG) $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)-org.png

# View the original SVG template map
view-template-$(1) : $(PATH_TEXTS)/$(1)-map.svg
	$(VIEWSVG) $(PATH_TEXTS)/$(1)-map.svg

else


##########################################################################
# This section contains rules for processing the maps manually.
# In this senario it is assumed that the map graphic file is
# in PNG format and ready to be placed on the page. The rules
# here are written with that in mind.
##########################################################################

# Link the ready-made graphic file to the process folder. This is the
# common place to find files like this.
$(PATH_PROCESS)/$(1)-map-rgb.png : $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)
	@echo INFO: Linking file to: $(shell pwd)/$$@
	@ln -sf $$(shell readlink -f -- $(PATH_SOURCE)/$(PATH_SOURCE_MAPS)/$(1)) $$@

# Create a CMYK PDF version of the graphic file in the process folder for
# creating the final typeset page version. It is obviously dependent on
# the original version and all this assumes that the original is RGB. The
# PDF file is actually only a container for the graphic file (probably TIFF)
# We will treat it like the other PNG graphic file.
$(PATH_PROCESS)/$(1)-map-cmyk.pdf : $(PATH_PROCESS)/$(1)-map-rgb.png
	@echo INFO: Creating: $$@
	@echo png:$(PATH_PROCESS)/$(1)-map-rgb.png -profile $(RGB_PROFILE) -profile $(CMYK_PROFILE) -compress zip -units PixelsPerInch -define pdf:use-cropbox=true pdf:$$@
	@convert png:$(PATH_PROCESS)/$(1)-map-rgb.png -profile $(RGB_PROFILE) -profile $(CMYK_PROFILE) -compress zip -units PixelsPerInch -define pdf:use-cropbox=true pdf:$$@

# This is the rgb.tex file that is necessary to process the
# map .rgb.usfm file. This is created when the View-Maps button
# is clicked. This has a dependency on BACK_MATTER.tex
# which it calls from the matter_peripheral.mk rules file.
$(PATH_PROCESS)/$(1)-map-page-rgb.tex : | $(PATH_PROCESS)/BACK_MATTER.tex
	@echo INFO: Creating: $$@
	@echo \\input $(TEX_PTX2PDF) > $$@
	@echo \\input $(TEX_SETUP) >> $$@
	@echo \\input BACK_MATTER.tex >> $$@
	@echo '\\def\HeaderPosition{0}' >> $$@
	@echo '\\def\FooterPosition{0}' >> $$@
	@echo '% Change paper width for portrate or landscape adjust margins as needed' >> $$@
	@echo '%\\PaperWidth=210mm' >> $$@
	@echo '%\\PaperHeight=145mm' >> $$@
	@echo '\\def\TopMarginFactor{0}' >> $$@
	@echo '\\def\SideMarginFactor{0}' >> $$@
	@echo '\\def\BottomMarginFactor{0}' >> $$@
	@echo \\ptxfile{$(PATH_TEXTS)/$(1)-map-page-rgb.usfm} >> $$@
	@echo '\\bye' >> $$@

# This is the cmyk.tex file that is necessary to process the
# map .cmyk.usfm file. This is created when the View-Maps button
# is clicked. This has a dependency on BACK_MATTER.tex
# which it calls from the matter_peripheral.mk rules file.
$(PATH_PROCESS)/$(1)-map-page-cmyk.tex : | $(PATH_PROCESS)/BACK_MATTER.tex
	@echo INFO: Creating: $$@
	@echo \\input $(TEX_PTX2PDF) > $$@
	@echo \\input $(TEX_SETUP) >> $$@
	@echo \\input BACK_MATTER.tex >> $$@
	@echo '\\def\HeaderPosition{0}' >> $$@
	@echo '\\def\FooterPosition{0}' >> $$@
	@echo '% Change paper width for portrate or landscape adjust margins as needed' >> $$@
	@echo '%\\PaperWidth=210mm' >> $$@
	@echo '%\\PaperHeight=145mm' >> $$@
	@echo '\\def\TopMarginFactor{0}' >> $$@
	@echo '\\def\SideMarginFactor{0}' >> $$@
	@echo '\\def\BottomMarginFactor{0}' >> $$@
	@echo \\ptxfile{$(PATH_TEXTS)/$(1)-map-page-cmyk.usfm} >> $$@
	@echo '\\bye' >> $$@

# Create the rgb.USFM file for processing this map. The map file
# is linked into the process here.
$(PATH_TEXTS)/$(1)-map-page-rgb.usfm : | $(PATH_PROCESS)/$(1)-map-rgb.png
	@echo INFO: Creating: $$@
	@echo \\id OTH > $$@
	@echo \\ide UTF-8 >> $$@
	@echo \\singlecolumn >> $$@
	@echo \\periph Map Page >> $$@
	@echo \\p >> $$@
	@echo '\\makedigitsother' >> $$@
	@echo '\\hfil\XeTeXpicfile $(1)-map-rgb.png width 300pt \hfil\par' >> $$@
	@echo '\\makedigitsletters' >> $$@
	@echo '\\bye' >> $$@

# Create the cmyk.USFM file for processing this map. The map file
# is linked into the process here.
$(PATH_TEXTS)/$(1)-map-page-cmyk.usfm : | $(PATH_PROCESS)/$(1)-map-cmyk.pdf
	@echo INFO: Creating: $$@
	@echo \\id OTH > $$@
	@echo \\ide UTF-8 >> $$@
	@echo \\singlecolumn >> $$@
	@echo \\periph Map Page >> $$@
	@echo \\p >> $$@
	@echo '\\makedigitsother' >> $$@
	@echo '\\hfil\XeTeXpdffile $(1)-map-cmyk.pdf width 300pt \hfil\par' >> $$@
	@echo '\\makedigitsletters' >> $$@
	@echo '\\bye' >> $$@

# Render the resulting PDF file from the rgb.tex and rgb.usfm file.
$(PATH_PROCESS)/$(1)-map-page-rgb.pdf : \
	$(PATH_TEXTS)/$(1)-map-page-rgb.usfm \
	$(PATH_PROCESS)/$(1)-map-page-rgb.tex
	@echo INFO: Creating: $$@
	@rm -f $$@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(PATH_PROCESS)/$(1)-map-page-rgb.tex

# Render the resulting PDF file from the cmyk.tex and cmyk.usfm file.
$(PATH_PROCESS)/$(1)-map-page-cmyk.pdf : \
	$(PATH_TEXTS)/$(1)-map-page-cmyk.usfm \
	$(PATH_PROCESS)/$(1)-map-page-cmyk.tex
	@echo INFO: Creating: $$@
	@rm -f $$@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(PATH_PROCESS)/$(1)-map-page-cmyk.tex

# View the resulting created PDF file for this map.
view-$(1) : $(PATH_PROCESS)/$(1)-map-page-rgb.pdf
	@echo INFO: Viewing RGB color profile map: $$<
	@ $(VIEWPDF) $$< &

# In this process this is not too useful. Let's try just telling
# user to just use the view button
preprocess-$(1) :
	@echo INFO:  This feature is not necessary in this mode.

# Convert this map ID to CMYK
cmyk-$(1) : $(PATH_PROCESS)/$(1)-map-page-cmyk.pdf
	@echo INFO: Creating CMYK color profile map: $$<
	@ $(VIEWPDF) $$< &

# Remove the current map PDF file
pdf-remove-$(1) :
	@echo WARNING: Removing: $$(shell readlink -f -- $(PATH_PROCESS)/$(1)-map-page-cmyk.pdf)
	@rm -f $(PATH_PROCESS)/$(1)-map-page-cmyk.pdf

# Edit the CSV data file
edit-data-$(1) :
	@echo INFO: This feature is not necessary in this mode.

# Edit the CSV style file
edit-styles-$(1) :
	@echo INFO: This feature is not necessary in this mode.

# View the original model map
view-model-$(1) : $(PATH_PROCESS)/$(1)
	$(VIEWIMG) $(PATH_PROCESS)/$(1)

# View the original SVG template map
view-template-$(1) :
	@echo INFO: This feature is not necessary in this mode.

endif

# Delete (clean out) this set of map files but do not delete the data
# in the source folder. This is shared by both types of map processes.
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

# If nothing is listed in the MATTER_MAPS binding list, we do not
# bother doing anything.
ifneq ($(MATTER_MAPS),)

# If there was something in the binding list then we will need to set
# these two vars.
MATTER_MAPS_RGB_PDF		= $(PATH_PROCESS)/MATTER_MAPS_RGB.pdf
MATTER_MAPS_CMYK_PDF		= $(PATH_PROCESS)/MATTER_MAPS_CMYK.pdf

# This first rule is for auto SVG processing
#ifneq ($(CREATE_MAP),0)

# For binding we will use pdftk to put together the
# individual PDFs we created earlier in this process.
# We need to do this for both RGB and CMYK files.
$(MATTER_MAPS_RGB_PDF) : $(foreach v,$(MATTER_MAPS),$(PATH_PROCESS)/$(v)-map-page-rgb.pdf)
	@echo INFO: Creating the bound PDF file for RGB maps: $(MATTER_MAPS_RGB_PDF)
	pdftk $(foreach v,$(MATTER_MAPS),$(PATH_PROCESS)/$(v)-map-page-rgb.pdf) cat output $@

$(MATTER_MAPS_CMYK_PDF) : $(foreach v,$(MATTER_MAPS),$(PATH_PROCESS)/$(v)-map-page-cmyk.pdf)
	@echo INFO: Creating the bound PDF file: $(MATTER_MAPS_CMYK_PDF)
	pdftk $(foreach v,$(MATTER_MAPS),$(PATH_PROCESS)/$(v)-map-page-cmyk.pdf) cat output $@


endif

# This will call TeX to create a "book" of maps. The results will
# be a PDF file that will be viewed in the PDF viewer. This is done
# seperately for RGB and CMYK maps
view-rgb-maps : $(MATTER_MAPS_RGB_PDF)
	@echo INFO: Creating a single PDF file for all the RGB maps.
	@$(VIEWPDF) $< &

view-cmyk-maps : $(MATTER_MAPS_CMYK_PDF)
	@echo INFO: Creating a single PDF file for all the CMYK maps.
	@$(VIEWPDF) $< &

# Remove the matter map files (both RGB and CMYK)
remove-maps :
	@echo INFO: Removing file: $(MATTER_MAPS_RGB_PDF) and $(MATTER_MAPS_CMYK_PDF)
	@rm -f $(MATTER_MAPS_RGB_PDF)
	@rm -f $(MATTER_MAPS_CMYK_PDF)

# As there can be confusion using the buttons for this kind of
# processing we are going to steer the user to the Maps menu
# for any of the processes they may need to use. With the following
# two commands we will disable the buttons when working on maps.
view-maps :
	@echo WARNING: This command is not available in this mode. Please use the commands on the Maps menu for all map processes.

preprocess-maps :
	@echo WARNING: This command is not available in this mode. Please use the commands on the Maps menu for all map processes.

# Do a total reset of all the map files
clean-maps :
	@echo WARNING: All map have been deleted, Sorry if you did not mean to do this
	$(foreach v,$(MATTER_MAPS), $(shell rm -f $(PATH_TEXTS)/$(v)* && rm -f $(PATH_PROCESS)/$(v)*))
	@rm -f $(MATTER_MAPS_RGB_PDF)
	@rm -f $(MATTER_MAPS_CMYK_PDF)
