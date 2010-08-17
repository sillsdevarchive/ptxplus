# matter_scripture.mk

# This file provides build rules for building all scripture material
# in a typical Scripture publication

# History:

# 20100602 - djd - Initial version created from code in
#		matter_books.mk file.
# 20100615 - djd - Changed hard codded extions to vars


##############################################################
#		Rules for publication Scripture content
##############################################################

# Before we can typeset we have to copy the source text
# into the Source folder. After that further preprocessing
# is needed. Any predictable process will be done here.
# The list of processes can be edited in the project ini
# ini under the [Preproces] section.

# Define the main macro for what it takes to process an
# individual component.

define component_rules

# Define our source file rule here. The idea is we do not want the
# user to get a file not found error when they process a file.
# Rather a dummy file will be created telling them the file is missing
# and hopefully some helpful instructions on what to do.
$(PATH_SOURCE)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE) : | $(PATH_SOURCE)
	$(call copysmart,$(PATH_RESOURCES_TEMPLATES)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE),$$@)

# This is the rule for creating the working text. We will use
# the postprocessing function to do this.
$(PATH_TEXTS)/$(1).$(EXT_WORK) : $(PATH_SOURCE)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)
ifeq ($(LOCKED),0)
	@echo Creating: $(PATH_TEXTS)/$(1).$(EXT_WORK)
	$$(call postprocessing,$(1),$($(1)_component))
else
	@echo INFO: Cannot create: $$@ because the project is locked.
endif

# This enables us to do the preprocessing on a single component and view the log file
# We will not do individual checks here as there can be a good number of them.
# If we implement that it will be in a different control file to simplify things.
# If we are checking text that means we are not sure about how good it is. That
# being the case, we don't want this text in the system yet so the very first
# thing we do is try to delete any existing copies from the source directory.
preprocess-$(1) : $(PATH_SOURCE)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE) $(DEPENDENT_FILE_LIST)
ifeq ($(LOCKED),0)
	$$(call preprocessing,$(1),$($(1)_component))
else
	@echo INFO: Cannot process: $$@ because the project is locked.
endif

# Call a postprocessing function which will run all the postprocesses.
postprocess-$(1) : $(PATH_SOURCE)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE) $(DEPENDENT_FILE_LIST)
ifeq ($(LOCKED),0)
	$$(call postprocessing,$(1),$($(1)_component))
else
	@echo INFO: Cannot post process: $(PATH_TEXTS)/$(1).$(EXT_WORK) because the project is locked.
endif

# Call the TeX control file creation script to create a simple
# control file that will link to the other settings
$(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_TEX) : $(PATH_PROCESS)/$(FILE_TEX_SETTINGS)
ifeq ($(LOCKED),0)
	@echo INFO: Creating: $$@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "$(1)" "$(1).$(EXT_WORK)" "$$@" ""
else
	@echo INFO: Cannot create: $$@ This is because the project is locked.
endif

# Process a single component and produce the final PDF. A Special dependency
# is set for the .$(EXT_ADJUSTMENT) file in case it has been altered.
# It would be nice to have a dependency on the piclist file but that
# process behaves different and not every component has one. So for
# now we need to leave it on its own.
$(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_PDF) : \
	$(PATH_TEXTS)/$(1).$(EXT_WORK) \
	$(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_ADJUSTMENT) \
	$(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_TEX) $(DEPENDENT_FILE_LIST)
	@echo INFO: Creating book PDF file: $(1).$(EXT_WORK).$(EXT_PDF)
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(1).$(EXT_WORK).$(EXT_TEX)
	$(call watermark,$$@)

#	cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) --no-pdf $(1).$(EXT_TEX)
#	cd $(PATH_PROCESS) && xdvipdfmx $(1).xdv

# Open the PDF file with reader
view-$(1) : $(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $$< &

# Open the SFM file with the text editor
edit-$(1) : $(PATH_TEXTS)/$(1).$(EXT_WORK)
	@ $(EDITSFM) $$< &

# Shortcut to open the PDF file
$(1) : $(PATH_PROCESS)/$(1).$(EXT_PDF)

# Rules for cleaning up content process files

# Remove the PDF for this component only
pdf-remove-$(1) :
	@echo INFO: Removing: $(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_PDF)
	@rm -f $(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_PDF)

# Make adjustment file which is a dependent of the PDF process
# Because every content file can have an adjustment file we
# automate this process by setting a dependency

adjlist-make-$(1) : $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_ADJUSTMENT)

# Call the adjustlist creation macro
$(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_ADJUSTMENT) : $(PATH_TEXTS)/$(1).$(EXT_WORK)
ifeq ($(USE_ADJUSTMENTS),true)
	@$$(call makeadjlist,$(1))
else
	@echo INFO: USE_ADJUSTMENTS is set to \"$(USE_ADJUSTMENTS)\". $$@ not made.
endif

# Remove the adjustment file for this component only
adjlist-remove-$(1) :
ifeq ($(LOCKED),0)
	@echo Removing: $(1).$(EXT_WORK).$(EXT_ADJUSTMENT)
	@$$(call removeadjlist,$(1))
else
	@echo INFO: Cannot remove $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_ADJUSTMENT) because the project is locked.
endif

# Currently there is no dependency on this file but I wish there
# was one, but piclist is not needed for all components.
piclist-make-$(1) : $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_PICLIST)

# Make illustrations file if illustrations are used in this pub
# If there is a path/file listed in the illustrationsLib field
# this rule will create a piclist file for the book being processed.
# Also, the make_piclist_file.py script it will do the illustration
# file copy and linking operations. It is easier to do that in that
# context than in the Makefile context.
$(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_PICLIST) : | $(PATH_ILLUSTRATIONS) $(PATH_SOURCE_PERIPH)/$(FILE_ILLUSTRATION_CAPTIONS)
ifeq ($(USE_ILLUSTRATIONS),true)
	@$$(call makepiclist,$(1))
else
	@echo INFO: USE_ILLUSTRATIONS is set to \"$(USE_ILLUSTRATIONS)\". $$@ not made.
endif

# Remove the picture placement file for this component only
piclist-remove-$(1) :
ifeq ($(LOCKED),0)
	@echo Removing: $(1).$(EXT_WORK).$(EXT_PICLIST)
	@$$(call removepiclist,$(1))
else
	@echo INFO: Cannot remove: $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_PICLIST) because the project is locked.
endif

endef

######################## End Main Macro ######################

####################### Start Main Process ###################

# Build a TeX control file that will process the components
# in a publication

# In case makefile needs things in order, we will put some
# dependent rules here before we hit the main component_rules
# building rule

# This builds a rule (in memory) for each of the content components
$(foreach v,$(GROUP_CONTENT), $(eval $(call component_rules,$(v))))

# The rule to create the bible override style sheet. This is
# used to override styles for Scripture that come from the
# .project.sty file.
$(PATH_PROCESS)/$(FILE_TEX_STYLE) : | $(PATH_SOURCE)
	$(call copysmart,$(PATH_RESOURCES_PROCESS)/$(FILE_TEX_STYLE),$@)

# Rule for building the TeX settings file that is used for
# format settings of all the main content. This is not to
# be confused with the Bible control file which is a TeX
# control file for processing the entire Bible.
$(PATH_PROCESS)/$(FILE_TEX_SETTINGS) : $(FILE_PROJECT_CONF)
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "" "" "$@" ""

# Rule for building the GROUP_CONTENT control file. This is
# not the same as TeX settings file above.
$(PATH_PROCESS)/$(FILE_GROUP_CONTENT_TEX) :
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "content" "content" "$@" ""


# Rule for generating the entire Scripture content. It will
# also generate the TOC if that feature is turned on.
$(PATH_PROCESS)/$(FILE_GROUP_CONTENT_PDF) : \
	$(foreach v,$(filter $(BIBLE_COMPONENTS_ALL),$(GROUP_CONTENT)), \
	$(PATH_TEXTS)/$(v).$(EXT_WORK)) \
	$(foreach v,$(filter-out $(BIBLE_COMPONENTS_ALL),$(GROUP_CONTENT)), \
	$(PATH_TEXTS)/$(v).$(EXT_WORK)) \
	$(PATH_PROCESS)/$(FILE_GROUP_CONTENT_TEX) $(DEPENDENT_FILE_LIST)
	@echo INFO: Creating: $@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(FILE_GROUP_CONTENT_TEX)
	$(call watermark,$@)
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TOC)"

# The TOC data is made during the content creation. As such
# the TOC file creation cannot happen until the content is made.
$(PATH_SOURCE_PERIPH)/$(FILE_TOC) : $(PATH_PROCESS)/$(FILE_GROUP_CONTENT_PDF)

# This enables preprocess checks on all the components processing each one independently.
preprocess-content :
	@echo INFO: Preprocess checking all content components:
	@$(foreach v,$(GROUP_CONTENT), $(call preprocessing,$(v),$($(v)_component)) )

# This enables postprocesses on all the components processing each one independently.
postprocess-content :
ifeq ($(LOCKED),0)
	@echo INFO: Postprocessing all content components
	@$(foreach v,$(GROUP_CONTENT), $(call postprocessing,$(v),$($(v)_component)) )
else
	@echo INFO: Cannot post process: $(PATH_TEXTS)/$(1).$(EXT_WORK) because the project is locked.
endif

# Do a component section and veiw the resulting output
view-content : $(PATH_PROCESS)/$(FILE_GROUP_CONTENT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

pdf-remove-content :
	@echo INFO: Removing file: $(FILE_CONTENTS_PDF)
	@rm -f $(FILE_CONTENTS_PDF)


###############################################################
#			Shared functions
###############################################################

# Run preprocesses on the source text.
define preprocessing
@if test -r "$(PATH_TEXTS)/$(1).$(EXT_WORK)"; then \
	echo INFO: Removing: $(PATH_TEXTS)/$(1).$(EXT_WORK); \
	rm -f $(PATH_TEXTS)/$(1).$(EXT_WORK); \
fi
@echo INFO: Preprocessing: '$(PATH_SOURCE)/$(2)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)'
@$(MOD_RUN_PROCESS) "preprocessChecks" "$(1)" "$(PATH_SOURCE)/$(2)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" ""
endef

# Run the postprocesses on working text, however, to be safe
# we run the preprocesses as well.
define postprocessing
$(call preprocessing ,$(1),$($(1)_component))
@echo INFO: Copy to: "$(PATH_TEXTS)/$(1).$(EXT_WORK)"
@$(MOD_RUN_PROCESS) "copyIntoSystem" "$(1)" "$(PATH_SOURCE)/$(2)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" ""
@echo INFO: Postprocessing: '$(PATH_TEXTS)/$(1).$(EXT_WORK)'
@$(MOD_RUN_PROCESS) "textProcesses" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" ""
endef

# Create a single adjustment file if adjustments are turned on
makeadjlist = $(MOD_RUN_PROCESS) "$(MOD_PARA_ADJUST)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)"

#define makeadjlist
#@echo INFO: Creating: $(1).$(EXT_WORK).$(EXT_ADJUSTMENT)
#@$(MOD_RUN_PROCESS) "$(MOD_PARA_ADJUST)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)"
#endef

# Create a single piclist file if illustrations are turned on
makepiclist = $(MOD_RUN_PROCESS) "$(MOD_MAKE_PICLIST)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)"


# Remove a single piclist file
removepiclist = rm -f $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_PICLIST)


# Remove a single adjustment file
removeadjlist = rm -f $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_ADJUSTMENT)


##############################################################
#			Rules for handling piclist file creation
##############################################################

# Copy into place the captions.csv file that goes in the
# project peripheral folder located in the Source folder.
$(PATH_SOURCE_PERIPH)/$(FILE_ILLUSTRATION_CAPTIONS) : | $(PATH_SOURCE_PERIPH)
ifeq ($(USE_ILLUSTRATIONS),true)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_ILLUSTRATION_CAPTIONS),$@)
endif

# Rule to make all the piclist files at one time
piclist-make-all :
ifeq ($(LOCKED),0)
	@for v in $(GROUP_CONTENT); do $(call makepiclist,$$v); done
else
	@echo INFO: Cannot create the piclist files because the project is locked
endif

# Rule to remove all piclist files at one time if the project is not locked
piclist-remove-all :
ifeq ($(LOCKED),0)
	@echo INFO: Now removing all piclist files
	@for v in $(GROUP_CONTENT); do $(call removepiclist,$$v); done
else
	@echo INFO: Cannot remove the piclist files because the project is locked
endif

#################################################################################

# Create all the adjustment files
# This will not work right if the working files have not been
# created before it is started
adjlist-make-all :
ifeq ($(LOCKED),0)
	@echo INFO: Creating all adjustment files:
	@for v in $(GROUP_CONTENT); do $(call makeadjlist,$$v); done
else
	@echo INFO: Cannot create the adjustment files because the project is locked
endif

##################################################################################

# Remove all the adjustment files
adjlist-remove-all :
ifeq ($(LOCKED),0)
	@echo INFO: Removing all adjustment files:
	@for v in $(GROUP_CONTENT); do $(call removeadjlist,$$v); done
else
	@echo INFO: Cannot remove the adjustment files because the project is locked
endif



