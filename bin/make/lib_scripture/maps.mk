# map.mk


# SVG Processing Rules
# This processes a single map file
define svg_process

# Copy in the original data file into the periph folder.
$(PATH_SOURCE_PERIPH)/$(1).$(EXT_CSV) : $(PATH_SOURCE_PERIPH)/$(1).$(EXT_PNG)
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-data.$(EXT_CSV),$$@)

# Link the data CSV file from the original in the Source
# Peripheral folder to the Maps folder.
$(PATH_MAPS)/$(1).$(EXT_CSV) : $(PATH_SOURCE_PERIPH)/$(1).$(EXT_CSV)
	@echo INFO: Linking map CSV: $(1).$(EXT_CSV)
	@ln -sf $$(shell readlink -f -- $(PATH_SOURCE_PERIPH)/$(1)).$(EXT_CSV) $$@

# Bring in the map background. This is a shared resource so
# it will be copied into the Illustrations folder and later
# linked to the Maps folder in Process.
$(PATH_ILLUSTRATIONS)/$(1)-bkgrnd.$(EXT_PNG) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-bkgrnd-cl.$(EXT_PNG),$$@)

# Link the map background file to the Maps folder.
$(PATH_MAPS)/$(1)-bkgrnd.$(EXT_PNG) : $(PATH_ILLUSTRATIONS)/$(1)-bkgrnd.$(EXT_PNG)
	@echo INFO: Linking map background file: $(1).$(EXT_PNG)
	@ln -sf $$(shell readlink -f -- $(PATH_ILLUSTRATIONS)/$(1)-bkgrnd.$(EXT_PNG)) $$@

# Copy in the map's svg style file right into the
# Process folder
$(PATH_MAPS)/$(1)-sty.$(EXT_CSV) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-styles.$(EXT_CSV),$$@)

# Bring in the original model file
$(PATH_SOURCE_PERIPH)/$(1).$(EXT_PNG) :
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-org.$(EXT_PNG),$$@)

# Copy the final SVG file into the Maps folder
$(PATH_MAPS)/$(1).$(EXT_SVG) : \
		$(PATH_MAPS)/$(1).$(EXT_CSV) \
		$(PATH_MAPS)/$(1)-bkgrnd.$(EXT_PNG) \
		$(PATH_MAPS)/$(1)-sty.$(EXT_CSV)
	$(call copysmart,$(PATH_RESOURCES_MAPS)/$($(1)_maps)-map.$(EXT_SVG),$$@)

# Crate the PDF file from the SVG file
$(PATH_MAPS)/$(1).$(EXT_PNG) : $(PATH_MAPS)/$(1).$(EXT_SVG)
	@echo INFO: Creating: $$@
	@rm -f $(PATH_MAPS)/$(1).$(EXT_PDF)
	@ FONTCONFIG_PATH=$(PATH_HOME)/$(PATH_FONTS) $(EXPORTSVG) --file=$(PATH_MAPS)/$(1).$(EXT_SVG) --export-png=$(PATH_PROCESS)/$(1).$(EXT_PNG) --export-text-to-path

# Crate the PDF file from the SVG file
$(PATH_PROCESS)/$(1).$(EXT_PDF) : $(PATH_MAPS)/$(1).$(EXT_PNG)
	@echo INFO: Creating: $$@
	@rm -f $(PATH_MAPS)/$(1).$(EXT_PDF)
	@ $($(PROCESS_MAP)-$(1))

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


edit-$(1) : $(PATH_MAPS)/$(1).$(EXT_SVG)
	$(VIEWSVG) $(PATH_MAPS)/$(1).$(EXT_SVG)


##### End SVG processing rules
endef




####################### Start Main Process ###################

# Assembling the maps will be different from other processes. There is no
# need for a USFM .sty sheet, or for USFM files. The PDF file handles will
# be inserted into a single .tex file which will be processed and produce
# the final group file. That will be added to other groups if needed.

# This builds a rule (in memory) for each of the maps
$(foreach v,$(GROUP_MAPS),$(eval $(call svg_process,$(v))))

# Create the final PDF file from the group component PDF files that have
# been included in a special .tex file that inserts them directly which
# avoids having to have an intermediat usfm file.
$(PATH_PROCESS)/$(FILE_GROUP_MAPS_PDF) : $(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX)
	@echo INFO: Creating: $(FILE_GROUP_MAPS_PDF)
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX)
	$(call watermark,$@)

$(PATH_PROCESS)/$(FILE_GROUP_MAPS_TEX) : \
		$(foreach v,$(GROUP_MAPS),$(PATH_TEXTS)/$(v).$(EXT_WORK)) \
		$(PATH_PROCESS)/$(FILE_TEX_SETTINGS) \
		$(PATH_PROCESS)/$(FILE_GROUP_MAPS_STY)
	@echo INFO: Creating: $(FILE_GROUP_MAPS_TEX)
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "" "" "$@" "maps"

#
$(PATH_PROCESS)/$(FILE_GROUP_MAPS_STY) :
	@echo INFO: Creating: $@
	@echo \\Marker pc > $@
	@echo \\FontSize 1 >> $@
	@echo \\LeftMargin 0 >> $@
	@echo \\FirstLineIndent 0 >> $@
	@echo \\RightMargin 0 >> $@
	@echo \\SpaceBefore 0 >> $@
	@echo \\SpaceAfter 0 >> $@

# View all the maps in the group in one PDF file
view-maps : $(PATH_PROCESS)/$(FILE_GROUP_MAPS_PDF)
	@echo INFO: Viewing $(FILE_GROUP_MAPS_PDF)
	@ $(VIEWPDF) $< &

# Remove the Maps PDF file
pdf-remove-maps :
	@echo INFO: Removing: $(FILE_GROUP_MAPS_PDF)
	@rm -f $(PATH_PROCESS)/$(FILE_GROUP_MAPS_PDF)


