# map.mk


# SVG Processing Rules
# This processes a single map file
define svg_process

# Copy in the original caption file into the source folder.
# If this is a multi-script project a transliteration
# process can be applied when it is copied into the project's
# map folder.
$(PATH_SOURCE)/$(1).$(EXT_CSV) :
	$(call copysmart,$(PATH_RESOURCES_TEMPLATES)/$($(1)_map).$(EXT_CSV),$$@)


# Copy in the map's svg style file
$(PATH_MAP)/$(1)-sty.$(EXT_CSV) :


# Bring in the original model file
$(PATH_MAP)/$(1)-sty.$(EXT_PNG) :


# Create the map's final CSV file from the original in
# the source folder. Special processes can be applied
# during the copy command.
$(PATH_MAP)/$(1).$(EXT_CSV) : $(PATH_SOURCE)/$(1).$(EXT_CSV)


# Create the final SVG file
$(PATH_MAP)/$(1).$(EXT_SVG) : $(PATH_MAP)/$(1).$(EXT_CSV)


# Crate the PDF file from the SVG file
$(PATH_MAP)/$(1).$(EXT_PDF) : $(PATH_MAP)/$(1).$(EXT_SVG)


# Link the newly created map PDF to the process folder
# so it can be linked properly to the map.usfm file.
$(PATH_PROCESS)/$(1).$(EXT_PDF) : $(PATH_MAP)/$(1).$(EXT_PDF)
	@echo INFO: Linking map PDF: $(1).$(EXT_PDF)
	@ln -sf $$(shell readlink -f -- $(PATH_MAP)/$(1)) $$@


##### End SVG processing rules
endef

####################### Start Main Process ###################

# This builds a rule (in memory) for each of the map components
$(foreach v,$(GROUP_MAP),$(eval $(call svg_process,$(v))))


# Create the main map file that will contain all the maps
# in the project.
$(PATH_TEXTS)/map.$(EXT_WORK) :


# Create the map control file
$(PATH_PROCESS)/map.$(EXT_TEX) :


# Create the map style file
$(PATH_PROCESS)/map.$(EXT_STYLE) :


view-map : $(PATH_PROCESS)/GROUP_MAP.$(EXT_PDF)
