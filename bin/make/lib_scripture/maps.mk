# map.mk


# SVG Processing Rules
# This processes a single map file
define svg_process

# Copy in the original data file into the periph folder.
$(PATH_SOURCE_PERIPH)/$(1).$(EXT_CSV) : $(PATH_SOURCE_PERIPH)/$(1).$(EXT_PNG)
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_map)-data.$(EXT_CSV),$$@)

# Link the data CSV file from the original in the Source
# Peripheral folder to the Maps folder.
$(PATH_MAP)/$(1).$(EXT_CSV) : $(PATH_SOURCE_PERIPH)/$(1).$(EXT_CSV)
	@echo INFO: Linking map CSV: $(1).$(EXT_CSV)
	@ln -sf $$(shell readlink -f -- $(PATH_SOURCE_PERIPH)/$(1)).$(EXT_CSV) $$@

# Bring in the map background. This is a shared resource so
# it will be copied into the Illustrations folder and later
# linked to the Maps folder in Process.
$(PATH_ILLUSTRATIONS)/$(1)-bkgrnd.$(EXT_PNG) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_map)-bkgrnd-cl.$(EXT_PNG),$$@)

# Link the map background file to the Maps folder.
$(PATH_MAP)/$(1)-bkgrnd.$(EXT_PNG) : $(PATH_ILLUSTRATIONS)/$(1)-bkgrnd.$(EXT_PNG)
	@echo INFO: Linking map background file: $(1).$(EXT_PNG)
	@ln -sf $$(shell readlink -f -- $(PATH_ILLUSTRATIONS)/$(1)-bkgrnd.$(EXT_PNG)) $$@

# Copy in the map's svg style file right into the
# Process folder
$(PATH_MAP)/$(1)-sty.$(EXT_CSV) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_map)-styles.$(EXT_CSV),$$@)

# Bring in the original model file
$(PATH_SOURCE_PERIPH)/$(1).$(EXT_PNG) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_map)-org.$(EXT_PNG),$$@)

# Copy the final SVG file into the Maps folder
$(PATH_MAP)/$(1).$(EXT_SVG) : \
		$(PATH_MAP)/$(1).$(EXT_CSV) \
		$(PATH_MAP)/$(1)-bkgrnd.$(EXT_PNG) \
		$(PATH_MAP)/$(1)-sty.$(EXT_CSV)
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_map)-map.$(EXT_SVG),$$@)

# Crate the PDF file from the SVG file
$(PATH_MAP)/$(1).$(EXT_PDF) : $(PATH_MAP)/$(1).$(EXT_SVG)

edit-$(1) : $(PATH_MAP)/$(1).$(EXT_SVG)
	$(VIEWSVG) $(PATH_MAP)/$(1).$(EXT_SVG)

##### End SVG processing rules
endef

####################### Start Main Process ###################

# This builds a rule (in memory) for each of the map components
$(foreach v,$(GROUP_MAP),$(eval $(call svg_process,$(v))))


################# Work down here now #######################

# Create the main map file that will contain all the maps
# in the project.
$(PATH_TEXTS)/map.$(EXT_WORK) :


# Create the map control file
$(PATH_PROCESS)/map.$(EXT_TEX) :


# Create the map style file
$(PATH_PROCESS)/map.$(EXT_STYLE) :


view-map : $(PATH_PROCESS)/GROUP_MAP.$(EXT_PDF)
