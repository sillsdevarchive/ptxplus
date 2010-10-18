# map.mk


# SVG Processing Rules
# This processes a single map file
define svg_process

# Copy in the original data file into the periph folder.
$(PATH_SOURCE_PERIPH)/$(1).$(EXT_CSV) : $(PATH_SOURCE_PERIPH)/$(1).$(EXT_PNG)
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-data.$(EXT_CSV),$$@)

# Link the data CSV file from the original in the Source
# Peripheral folder to the Maps folder.
$(PATH_MAP)/$(1).$(EXT_CSV) : $(PATH_SOURCE_PERIPH)/$(1).$(EXT_CSV)
	@echo INFO: Linking map CSV: $(1).$(EXT_CSV)
	@ln -sf $$(shell readlink -f -- $(PATH_SOURCE_PERIPH)/$(1)).$(EXT_CSV) $$@

# Bring in the map background. This is a shared resource so
# it will be copied into the Illustrations folder and later
# linked to the Maps folder in Process.
$(PATH_ILLUSTRATIONS)/$(1)-bkgrnd.$(EXT_PNG) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-bkgrnd-cl.$(EXT_PNG),$$@)

# Link the map background file to the Maps folder.
$(PATH_MAP)/$(1)-bkgrnd.$(EXT_PNG) : $(PATH_ILLUSTRATIONS)/$(1)-bkgrnd.$(EXT_PNG)
	@echo INFO: Linking map background file: $(1).$(EXT_PNG)
	@ln -sf $$(shell readlink -f -- $(PATH_ILLUSTRATIONS)/$(1)-bkgrnd.$(EXT_PNG)) $$@

# Copy in the map's svg style file right into the
# Process folder
$(PATH_MAP)/$(1)-sty.$(EXT_CSV) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-styles.$(EXT_CSV),$$@)

# Bring in the original model file
$(PATH_SOURCE_PERIPH)/$(1).$(EXT_PNG) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-org.$(EXT_PNG),$$@)

# Copy the final SVG file into the Maps folder
$(PATH_MAP)/$(1).$(EXT_SVG) : \
		$(PATH_MAP)/$(1).$(EXT_CSV) \
		$(PATH_MAP)/$(1)-bkgrnd.$(EXT_PNG) \
		$(PATH_MAP)/$(1)-sty.$(EXT_CSV)
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-map.$(EXT_SVG),$$@)

# Crate the PDF file from the SVG file
$(PATH_MAP)/$(1).$(EXT_PDF) : $(PATH_MAP)/$(1).$(EXT_SVG)

edit-$(1) : $(PATH_MAP)/$(1).$(EXT_SVG)
	$(VIEWSVG) $(PATH_MAP)/$(1).$(EXT_SVG)

##### End SVG processing rules
endef

####################### Start Main Process ###################

# Assembling the maps will be different from other processes. There is no
# need for a USFM .sty sheet, or for USFM files. The PDF file handles will
# be inserted into a single .tex file which will be processed and produce
# the final group file. That will be added to other groups if needed.

# This builds a rule (in memory) for each of the map components
$(foreach v,$(GROUP_MAP),$(eval $(call svg_process,$(v))))

# Create the final PDF file from the group component PDF files that have
# been included in a special .tex file that inserts them directly which
# avoids having to have an intermediat usfm file.
$(PATH_PROCESS)/$(FILE_GROUP_MAPS_PDF) : $(PATH_PROCESS)/GROUP_MAPS.$(EXT_TEX)
	@echo INFO: Creating: $(FILE_GROUP_MAPS_PDF)
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX)
	$(call watermark,$$@)

# Create the .tex file which includes all the map components in PDF form.
# This .tex file will be slightly different from most .tex files that are
# produced by the makd tex module. Note, this is dependant on each of the
# individual map components being produced first.
$(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX) : $(foreach v,$(GROUP_MAPS),$(PATH_PROCESS)/$(v).$(EXT_PDF))
	@echo INFO: Creating: $(FILE_GROUP_MAPS_TEX)
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "" "" "$@" "maps"


view-maps : $(PATH_PROCESS)/$(FILE_GROUP_MAPS_PDF)


