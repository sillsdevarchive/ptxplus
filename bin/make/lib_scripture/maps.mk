# map.mk


# SVG Processing Rules
# This processes a single map file
define svg_process

# Copy in the original data file into the periph folder.
$(PATH_SOURCE_PERIPH)/$(1).$(EXT_CSV) : $(PATH_ILLUSTRATIONS)/$(1).$(EXT_PNG)
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-data.$(EXT_CSV),$$@)

# Link the data CSV file from the original in the Source Peripheral folder to
# the Maps folder.
$(PATH_MAPS)/$(1).$(EXT_CSV) : $(PATH_SOURCE_PERIPH)/$(1).$(EXT_CSV)
	@echo INFO: Linking map CSV: $(1).$(EXT_CSV)
	@ln -sf $$(shell readlink -f -- $(PATH_SOURCE_PERIPH)/$(1)).$(EXT_CSV) $$@

# Bring in the map background.  This is a shared resource so it will be copied
# into the Illustrations folder and later linked to the Maps folder in Process.
$(PATH_ILLUSTRATIONS)/$(1)-bkgrnd-$(MAP_COLOR_MODE).$(EXT_PNG) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-bkgrnd-$(MAP_COLOR_MODE).$(EXT_PNG),$$@)

# Link the map background file to the Maps folder.
$(PATH_MAPS)/$(1)-bkgrnd.$(EXT_PNG) : $(PATH_ILLUSTRATIONS)/$(1)-bkgrnd-$(MAP_COLOR_MODE).$(EXT_PNG)
	@echo INFO: Linking map background file: $(1).$(EXT_PNG)
	@ln -sf $$(shell readlink -f -- $(PATH_ILLUSTRATIONS)/$(1)-bkgrnd-$(MAP_COLOR_MODE).$(EXT_PNG)) $$@

# Copy in the map's svg style file right into the Process folder
$(PATH_MAPS)/$(1)-sty.$(EXT_CSV) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-styles.$(EXT_CSV),$$@)

# Bring in the original model file and park it in
# the Illustrations folder so other projects can
# use it if they need to.
$(PATH_ILLUSTRATIONS)/$(1).$(EXT_PNG) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-org.$(EXT_PNG),$$@)

# Copy into the project the temporary svg file that
# will be processed
$(PATH_MAPS)/$(1)-temp.$(EXT_SVG) :
	@echo INFO: Creating: $(1)-temp.$(EXT_SVG)
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-map.$(EXT_SVG),$$@)

# Copy the final SVG file into the Maps folder
$(PATH_MAPS)/$(1).$(EXT_SVG) : \
		$(PATH_MAPS)/$(1).$(EXT_CSV) \
		$(PATH_MAPS)/$(1)-bkgrnd.$(EXT_PNG) \
		$(PATH_MAPS)/$(1)-sty.$(EXT_CSV) \
		$(PATH_MAPS)/$(1)-temp.$(EXT_SVG)
	@echo INFO: Creating: $$@
	@$(MOD_RUN_PROCESS) $(MOD_MAKE_MAP) "" "$(PATH_MAPS)/$(1)-temp.$(EXT_SVG)" "$$@" ""

# Crate the intermediate PNG file from the SVG file.  Note that this uses a
# special command that was created by the make_make process which has all the
# necessary commands needed for Inkscape (at the command line)to convert the SVG
# file, which has been edited into its final form, to the PNG intermediate file
# that will be converted to the final component PDF form via Imagemagick.
$(PATH_MAPS)/$(1).$(EXT_PNG) : $(PATH_MAPS)/$(1).$(EXT_SVG)
	@echo INFO: Creating: $$@
	@rm -f $(PATH_MAPS)/$(1).$(EXT_PDF)
	@ $(PROCESS_MAP_PNG-$(1))

# Crate the PDF file from the intermediate PNG file.  Note that this uses a
# special command that was created by the make_make process which has all the
# necessary commands needed for Imagemagick to convert this intermediate file
# which was exported from Inkscape into the final PDF file.  The process
# includes rotate and colorspace commands.
$(PATH_PROCESS)/$(1).$(EXT_PDF) : $(PATH_MAPS)/$(1).$(EXT_PNG)
	@echo INFO: Creating: $$@
	@rm -f $$@
	@ $(PROCESS_MAP_PDF-$(1))

# Create the map page
$(PATH_TEXTS)/$(1).$(EXT_WORK) : $(PATH_PROCESS)/$(1).$(EXT_PDF)
	@echo INFO: Creating: $$@
	@echo \\id OTH > $$@
	@echo \\ide UTF-8 >> $$@
	@echo \\singlecolumn >> $$@
	@echo \\periph Map Page >> $$@
	@echo \\pc ​ >> $$@
	@echo '\\makedigitsother%' >> $$@
	@echo '\\catcode`{=1\\catcode`}=2\\catcode`#=6%' >> $$@
	@echo '\\domap{$(1).$(EXT_PDF)}' >> $$@
	@echo '\\catcode`{=11\\catcode`}=11\\makedigitsletters' >> $$@

# View the PDF file of this component
view-$(1) : $(PATH_PROCESS)/$(1).$(EXT_PDF)
	@echo INFO: Viewing $(1).$(EXT_PDF)
	@ $(VIEWPDF) $$< &

# Open up the map svg file in Inkscape (or whatever editor you are using)
preprocess-$(1) : $(PATH_MAPS)/$(1).$(EXT_SVG)
	@echo INFO: Opening for editing: $(1).$(EXT_SVG)
	@FONTCONFIG_PATH=$(PATH_HOME)/$(PATH_FONTS) $(VIEWSVG) $$<

# View the original model map for reference
view-map-model-$(1) : $(PATH_ILLUSTRATIONS)/$(1).$(EXT_PNG)
	@echo INFO: Viewing: $$<
	@ $(VIEWIMG) $$<

# Remove pieces of a component
pdf-remove-$(1) :
	@echo WARNING: Removing: $(1).$(EXT_PDF)
	@rm -f $(PATH_PROCESS)/$(1).$(EXT_PDF)

svg-remove-$(1) :
	@echo WARNING: Removing: $(1).$(EXT_SVG)
	@rm -f $(PATH_MAPS)/$(1).$(EXT_SVG)

csv-data-remove-$(1) :
	@echo WARNING: Removing: $(1).$(EXT_CSV) - data
	@rm -f $(PATH_MAPS)/$(1).$(EXT_CSV)

csv-sty-remove-$(1) :
	@echo WARNING: Removing: $(1).$(EXT_CSV) - style
	@rm -f $(PATH_MAPS)/$(1)-sty.$(EXT_CSV)

png-remove-$(1) :
	@echo WARNING: Removing: $(1).$(EXT_PNG)
	@rm -f $(PATH_MAPS)/$(1).$(EXT_PNG)

usfm-remove-$(1) :
	@echo WARNING: Removing: $(1).$(EXT_WORK)
	@rm -f $(PATH_TEXTS)/$(1).$(EXT_WORK)

all-remove-$(1) :
	@echo WARNING: Removing all the files for the $(1) component
	@rm -f $(PATH_PROCESS)/$(1).$(EXT_PDF)
	@rm -f $(PATH_MAPS)/$(1).$(EXT_SVG)
	@rm -f $(PATH_MAPS)/$(1).$(EXT_CSV)
	@rm -f $(PATH_MAPS)/$(1)-sty.$(EXT_CSV)
	@rm -f $(PATH_MAPS)/$(1).$(EXT_PNG)
	@rm -f $(PATH_TEXTS)/$(1).$(EXT_WORK)
	@rm -f $(PATH_MAPS)/$(1)-temp.$(EXT_SVG)


##### End SVG processing rules
endef




############################### Start Main Process ############################

# Assembling the maps will be different from other processes.  There is no need
# for a USFM .sty sheet, or for USFM files.  The PDF file handles will be
# inserted into a single .tex file which will be processed and produce the final
# group file.  That will be added to other groups if needed.

# This builds a rule (in memory) for each of the maps
$(foreach v,$(GROUP_MAPS),$(eval $(call svg_process,$(v))))

# Create the final PDF file from the group component PDF files that have been
# included in a special .tex file that inserts them directly which avoids having
# to have an intermediat usfm file.
$(PATH_PROCESS)/$(FILE_GROUP_MAPS_PDF) : \
		$(foreach v,$(GROUP_MAPS),$(PATH_PROCESS)/$(v).$(EXT_PDF)) \
		$(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX)
	@echo INFO: Creating: $(FILE_GROUP_MAPS_PDF)
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX)
	$(call watermark,$@)

$(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX) : \
		$(foreach v,$(GROUP_MAPS),$(PATH_TEXTS)/$(v).$(EXT_WORK)) \
		$(PATH_PROCESS)/$(FILE_TEX_SETTINGS) \
		$(PATH_PROCESS)/$(FILE_GROUP_MAPS_STY)
	@echo INFO: Creating: $(FILE_GROUP_MAPS_TEX)
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "" "" "$@" "maps"

# Create the group style file for any custom styles.
$(PATH_PROCESS)/$(FILE_GROUP_MAPS_STY) :
	@echo INFO: Creating: $@
	@echo \\Marker pc > $@
	@echo \\FontSize 1 >> $@
	@echo \\LeftMargin 0 >> $@
	@echo \\FirstLineIndent 0 >> $@
	@echo \\RightMargin 0 >> $@
	@echo \\SpaceBefore 0 >> $@
	@echo \\SpaceAfter 0 >> $@

# View all the maps in the group in one PDF file We will remove the previous one
# in case there have been changes
view-maps : $(PATH_PROCESS)/$(FILE_GROUP_MAPS_PDF)
	@echo INFO: Viewing $(FILE_GROUP_MAPS_PDF)
	@ $(VIEWPDF) $< &

# Warn the user this can't be done
view-map-model-maps :
	@echo WARN: Sorry, no view option for combined map group

# Warn the user this can't be done
preprocess-maps :
	@echo WARN: Sorry, no edit/check option for combined map group

# Remove map group components
pdf-remove-maps :
	@echo INFO: Removing: $(FILE_GROUP_MAPS_PDF)
	@rm -f $(PATH_PROCESS)/$(FILE_GROUP_MAPS_PDF)

tex-remove-maps :
	@echo INFO: Removing: $(FILE_GROUP_MAPS_TEX)
	@rm -f $(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX)

sty-remove-maps :
	@echo INFO: Removing: $(FILE_GROUP_MAPS_STY)
	@rm -f $(PATH_PROCESS)/$(FILE_GROUP_MAPS_STY)

all-remove-maps :
	@echo INFO: Removing all map group components
	@rm -f $(PATH_PROCESS)/$(FILE_GROUP_MAPS_PDF)
	@rm -f $(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX)
	@rm -f $(PATH_PROCESS)/$(FILE_GROUP_MAPS_STY)

