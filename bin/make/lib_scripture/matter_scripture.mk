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
# and hopefully some instructions on what to do.
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
$(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_TEX) : $(PATH_PROCESS)/$(FILE_TEX_BIBLE)
ifeq ($(LOCKED),0)
	@echo INFO: Creating: $$@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "$(1)" "$(1).$(EXT_WORK)" "$$@" ""
else
	@echo INFO: Cannot create: $$@ This is because the project is locked.
endif

# Process a single component and produce the final PDF. Special dependencies
# are set for the .$(EXT_ADJUSTMENT) and .$(EXT_PICLIST) files in case they have been altered.
# The .$(EXT_PICLIST) file is created in the content_illustrations.mk rules file.
$(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_PDF) : \
	$(PATH_TEXTS)/$(1).$(EXT_WORK) \
	$(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_ADJUSTMENT) \
	$(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_PICLIST) \
	$(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_TEX) \
	$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX) \
	check-assets | $(DEPENDENT_FILE_LIST)
	@echo INFO: Creating book PDF file: $$@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(1).$(EXT_WORK).$(EXT_TEX)
#	cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) --no-pdf $(1).$(EXT_TEX)
#	cd $(PATH_PROCESS) && xdvipdfmx $(1).xdv

# Open the PDF file with reader
view-$(1) : $(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_PDF)
	@- $(CLOSEPDF)
	$(call watermark,$$<)
	@ $(VIEWPDF) $$< &

# Open the SFM file with the text editor
edit-$(1) : $(PATH_TEXTS)/$(1).$(EXT_WORK)
	@ $(EDITSFM) $$< &

# Shortcut to open the PDF file
$(1) : $(PATH_PROCESS)/$(1).$(EXT_PDF)

# Make adjustment file
$(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_ADJUSTMENT) :
ifeq ($(USE_ADJUSTMENTS),true)
	@echo INFO: Creating: $$@
	@$(MOD_RUN_PROCESS) "$(MOD_PARA_ADJUST)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)"
else
	@echo INFO: USE_ADJUSTMENTS is set to \"$(USE_ADJUSTMENTS)\". $$@ not made.
endif


# Make illustrations file if illustrations are used in this pub
# If there is a path/file listed in the illustrationsLib field
# this rule will create a piclist file for the book being processed.
# Also, the make_piclist_file.py script it will do the illustration
# file copy and linking operations. It is easier to do that in that
# context than in the Makefile context.
$(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_PICLIST) : | $(PATH_ILLUSTRATIONS) $(PATH_SOURCE_PERIPH)/$(FILE_ILLUSTRATION_CAPTIONS)
ifeq ($(USE_ILLUSTRATIONS),true)
	@echo INFO: Creating: $$@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_PICLIST)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)"
else
	@echo INFO: USE_ILLUSTRATIONS is set to \"$(USE_ILLUSTRATIONS)\". $$@ not made.
endif


# Rules for cleaning up content process files

# Remove the PDF for this component only
pdf-remove-$(1) :
	@echo INFO: Removing: $(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_PDF)
	@rm -f $(PATH_PROCESS)/$(1).$(EXT_WORK).$(EXT_PDF)

# Remove the adjustment file for this component only
adjfile-remove-$(1) :
ifeq ($(LOCKED),0)
	@echo INFO: Removing: $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_ADJUSTMENT)
	@rm -f $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_ADJUSTMENT)
else
	@echo INFO: Cannot run: $$@ This is because the project is locked.
endif

# Remove the picture placement file for this component only
picfile-remove-$(1) :
ifeq ($(LOCKED),0)
	@echo INFO: Removing: $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_PICLIST)
	@rm -f $(PATH_TEXTS)/$(1).$(EXT_WORK).$(EXT_PICLIST)
else
	@echo INFO: Cannot run: $$@ This is because the project is locked.
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
$(PATH_PROCESS)/$(FILE_BIBLE_STYLE) : | $(PATH_SOURCE)
	$(call copysmart,$(PATH_RESOURCES_PROCESS)/$(FILE_BIBLE_STYLE),$@)

# Rule for building the TeX settings file that is used for
# format settings of all the main content. This is not to
# be confused with the Bible control file which is a TeX
# control file for processing the entire Bible.
$(PATH_PROCESS)/$(FILE_TEX_BIBLE) : $(FILE_PROJECT_CONF)
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
	$(PATH_TEXTS)/$(v).$(EXT_WORK).$(EXT_PICLIST) \
	$(PATH_TEXTS)/$(v).$(EXT_WORK).$(EXT_ADJUSTMENT) \
	$(PATH_TEXTS)/$(v).$(EXT_WORK)) \
	$(PATH_PROCESS)/$(FILE_GROUP_CONTENT_TEX) \
	check-assets | $(DEPENDENT_FILE_LIST)
	@echo INFO: Creating: $@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(FILE_GROUP_CONTENT_TEX)
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TOC)"

# The TOC data is made during the content creation. As such
# the TOC file creation cannot happen until the content is made.
$(PATH_SOURCE_PERIPH)/$(FILE_TOC) : $(PATH_PROCESS)/$(FILE_GROUP_CONTENT_PDF)

# This enables preprocess checks on all the components at one time.
preprocess-content :
	@echo INFO: Preprocess checking all content components:
	@$(foreach v,$(GROUP_CONTENT), $(MOD_RUN_PROCESS) "preprocessChecks" "$(v)" "$(PATH_SOURCE)/$($(v)_component)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)"; )

# This enables preprocess checks on all the components at one time.
postprocess-content :
ifeq ($(LOCKED),0)
	@echo INFO: Postprocessing all content components
	@$(foreach v,$(GROUP_CONTENT), $(call postprocessing,$(v),$($(v)_component)) )
else
	@echo INFO: Cannot post process: $(PATH_TEXTS)/$(1).$(EXT_WORK) because the project is locked.
endif

# Do a component section and veiw the resulting output
view-contents : $(PATH_PROCESS)/$(FILE_GROUP_CONTENT_PDF)
	@- $(CLOSEPDF)
	$(call watermark,$<)
	@ $(VIEWPDF) $< &

pdf-remove-contents :
	@echo INFO: Removing file: $(FILE_CONTENTS_PDF)
	@rm -f $(FILE_CONTENTS_PDF)


###############################################################
#			Shared functions
###############################################################

# Run the postprocesses on working text, however, to be safe
# we run the preprocesses as well.
define postprocessing
$(call preprocessing ,$(1),$($(1)_component))
@echo INFO: Copy to: "$(PATH_TEXTS)/$(1).$(EXT_WORK)"
@$(MOD_RUN_PROCESS) "copyIntoSystem" "$(1)" "$(PATH_SOURCE)/$(2)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" ""
@echo INFO: Postprocessing: '$(PATH_TEXTS)/$(1).$(EXT_WORK)'
@$(MOD_RUN_PROCESS) "textProcesses" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" ""
endef

# Run preprocesses on the source text.
define preprocessing
@if test -r "$(PATH_TEXTS)/$(1).$(EXT_WORK)"; then \
	echo INFO: Removing: $(PATH_TEXTS)/$(1).$(EXT_WORK); \
	rm -f $(PATH_TEXTS)/$(1).$(EXT_WORK); \
fi
@echo INFO: Preprocessing: '$(PATH_SOURCE)/$(2)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)'
@$(MOD_RUN_PROCESS) "preprocessChecks" "$(1)" "$(PATH_SOURCE)/$(2)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" ""
endef

##############################################################
#			Rules for handling illustrations material
##############################################################

# Copy into place the captions.csv file that goes in the
# project peripheral folder located in the Source folder.
$(PATH_SOURCE_PERIPH)/$(FILE_ILLUSTRATION_CAPTIONS) : | $(PATH_SOURCE_PERIPH)
ifeq ($(USE_ILLUSTRATIONS),true)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_ILLUSTRATION_CAPTIONS),$@)
endif



# Old stuff for trash


## Start with the OT but we don't want to do anything if there
## are no components to process

#ifneq ($(MATTER_OT),)
## These build a rule (in memory) for all of the content components
#$(foreach v,$(GROUP_CONTENT), $(eval $(call component_rules,$(v))))

## A rule for creating the TeX control file for when the
## entire OT is being typeset.
#$(PATH_PROCESS)/$(FILE_MATTER_OT_TEX) : $(PATH_PROCESS)/$(FILE_TEX_BIBLE)
#	@echo INFO: Creating: $@
#	@$(MOD_RUN_PROCESS) $(MOD_MAKE_TEX) 'ot' 'ot' '$@' ''

## Render the entire OT
#$(PATH_PROCESS)/$(FILE_MATTER_OT_PDF) : \
#	$(foreach v,$(filter $(OT_COMPONENTS),$(MATTER_OT)), \
#	$(PATH_TEXTS)/$(v).$(EXT_WORK)) \
#	$(foreach v,$(filter-out $(OT_COMPONENTS),$(MATTER_OT)), \
#	$(PATH_TEXTS)/$(v).$(EXT_WORK).$(EXT_PICLIST) \
#	$(PATH_TEXTS)/$(v).$(EXT_WORK).$(EXT_ADJUSTMENT) \
#	$(PATH_TEXTS)/$(v).$(EXT_WORK)) \
#	$(PATH_PROCESS)/$(FILE_MATTER_OT_TEX) \
#	check-assets | $(DEPENDENT_FILE_LIST)
#	@echo INFO: Creating: $@
#	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(FILE_MATTER_OT_TEX)
#endif

#pdf-remove-ot :
#	@echo INFO: Removing file: $(FILE_MATTER_OT_PDF)
#	@rm -f $(FILE_MATTER_OT_PDF)


## Moving along we will do the NT if there are any components
## listed in the .project.conf file
#ifneq ($(MATTER_NT),)
## These build a rule (in memory) for this set of components
#$(foreach v,$(MATTER_NT), $(eval $(call component_rules,$(v))))

## A rule for creating the TeX control file for when the
## entire OT is being typeset.
#$(PATH_PROCESS)/$(FILE_MATTER_NT_TEX) : $(PATH_PROCESS)/$(FILE_TEX_BIBLE)
#	@echo INFO: Creating: $@
#	@$(MOD_RUN_PROCESS) $(MOD_MAKE_TEX) 'nt' 'nt' '$@' ''

## Render the entire NT
#$(PATH_PROCESS)/$(FILE_MATTER_NT_PDF) : \
#	$(foreach v,$(filter $(NT_COMPONENTS),$(MATTER_NT)), \
#	$(PATH_TEXTS)/$(v).$(EXT_WORK)) \
#	$(foreach v,$(filter-out $(NT_COMPONENTS),$(MATTER_NT)), \
#	$(PATH_TEXTS)/$(v).$(EXT_WORK).$(EXT_PICLIST) \
#	$(PATH_TEXTS)/$(v).$(EXT_WORK).$(EXT_ADJUSTMENT) \
#	$(PATH_TEXTS)/$(v).$(EXT_WORK)) \
#	$(PATH_PROCESS)/$(FILE_MATTER_NT_TEX) \
#	check-assets | $(DEPENDENT_FILE_LIST)
#	@echo INFO: Creating: $@
#	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(FILE_MATTER_NT_TEX)

#endif

#pdf-remove-nt :
#	@echo INFO: Removing file: $(FILE_MATTER_NT_PDF)
#	@rm -f $(FILE_MATTER_NT_PDF)

## Do a component section and veiw the resulting output
#view-ot : $(PATH_PROCESS)/$(FILE_MATTER_OT_PDF)
#	@- $(CLOSEPDF)
#	$(call watermark,$<)
#	@ $(VIEWPDF) $< &

#view-nt : $(PATH_PROCESS)/$(FILE_MATTER_NT_PDF)
#	@- $(CLOSEPDF)
#	$(call watermark,$<)
#	@ $(VIEWPDF) $< &


## Preproces all the components in a project then run whatever global processes
## needed like make-master-wordlist. (Add additional elements as added in the section below)
#preprocess-checks: preprocess-ot preprocess-nt


## These are to augment the individual book commands set above for instances
## when a specific group is being checked. (More may need to be added)
#preprocess-ot :
#	@echo INFO: Preprocess checking OT components:
#	@$(foreach v,$(MATTER_OT), $(MOD_RUN_PROCESS) preprocessChecks $(v) $(PATH_SOURCE)/$($(v)_component)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE); )

#preprocess-nt :
#	@echo INFO: Preprocess checking NT components:
#	@$(foreach v,$(MATTER_NT), $(MOD_RUN_PROCESS) preprocessChecks $(v) $(PATH_SOURCE)/$($(v)_component)$(NAME_SOURCE_ORIGINAL).$(EXT_SOURCE); )

## Having these here enable rules to call other rules
#.PHONY: view-ot view-nt preprocess-checks



