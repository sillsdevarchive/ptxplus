# matter_scripture.mk

# This file provides build rules for building all scripture material
# in a typical Scripture publication

# History:

# 20100602 - djd - Initial version created from code in
#		matter_books.mk file.


##############################################################
#		Variales for Middle Matter
##############################################################

# Build the dependent file listing here. This will include
# file paths and names we build here and the list we bring in
# from the project config file. This needs to be loaded early
# in the process. If this rules file ever needs to be moved
# down the chain this might have to move, or be put in a
# seperate file.
DEPENDENT_FILE_LIST = $(FILE_DEPENDENT_LIST) \
  $(PATH_ILLUSTRATIONS)/$(FILE_WATERMARK) \
  $(FILE_PROJECT_CONF)


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
# user to come up cold when he selects a file for processing if
# that file is not there. Rather a dummy file will be created
# telling them the file is missing.
$(PATH_SOURCE)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION) : | $(PATH_SOURCE)
	@if test -r $(PATH_TEMPLATES)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION); then \
		echo Copying into project from: $(PATH_TEMPLATES)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION); \
		cp $(PATH_TEMPLATES)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION) '$$@'; \
	else \
		echo Could not find: $$@; \
		echo Creating this file:; \
		echo Caution, you will need to edit it; \
		echo \\id OTH >> $$@; \
		echo \\ide UTF-8 >> $$@; \
		echo \\periph \<Fill in page type here\> >> $$@; \
		echo \\p This is a auto created page found at: $$@ >> $$@; \
		echo \\p Please edit as needed. >> $$@; \
	fi

# This is the basic rule for auto-text-processing. To control processes
# edit the project.conf file. This will automatically run the four
# phases of text processing. However, first it will delete any copies
# in the system to avoid having bad data in the system. All problems with
# the source must be fixed in the source, no where else. The first process
# will be preprocess checks of the source text. Next it will run any custom
# proecesses that are configured in the project.conf file. These could be
# anything and may include copying text into the project, in which case
# requires setting the CopyIntoSystem setting to false. After the custom
# proecesses are run it will copy the text into the system and then it will
# run any necessary text processes on the system source text as defined in
# the project.conf file.
ifeq ($(LOCKED),0)
$(PATH_TEXTS)/$(1).usfm : $(PATH_SOURCE)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION)
	@echo INFO: Auto-preprocessing: $$< and creating $$@
	@rm -f $(PATH_TEXTS)/$(1).usfm
	@$(PY_RUN_PROCESS) preprocessChecks $(1) '$$<' '$$@'
	@$(PY_RUN_PROCESS) copyIntoSystem $(1) '$$<' '$$@'
	@$(PY_RUN_PROCESS) textProcesses $(1) '$$@' '$$@'
else
#	@echo File $(PATH_TEXTS)/$(1).usfm is locked
endif

# This enables us to do the preprocessing on a single component and view the log file
# We will not do individual checks here as there can be a good number of them.
# If we implement that it will be in a different control file to simplify things.
# If we are checking text that means we are not sure about how good it is. That
# being the case, we don't want this text in the system yet so the very first
# thing we do is try to delete any existing copies from the source directory.
preprocess-$(1) : $(PATH_SOURCE)/$($(1)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION) $(DEPENDENT_FILE_LIST)
ifeq ($(LOCKED),0)
	@echo INFO: Removing $(PATH_TEXTS)/$(1).usfm and error checking '$$<'
	@rm -f $(PATH_TEXTS)/$(1).usfm
	@$(PY_RUN_PROCESS) preprocessChecks $(1) '$$<'
endif

#################################
# Problem: It would be nice if we could include a warning to users in the above process
# whenever the system is locked so they know why it isn't processing their text. The
# problem is that an else statement with a warning doesn't seem to work. Don't know
# why so I had to remove it for now.
#################################

# Call the TeX control file creation script to create a simple
# control file that will link to the other settings
$(PATH_PROCESS)/$(1).usfm.tex : $(PATH_PROCESS)/$(FILE_TEX_BIBLE)
	@echo INFO: Creating book control file: $$@
	@$(PY_RUN_PROCESS) make_tex_control_file '$(1)' '$(PATH_PROCESS)/$(1).usfm' '$$@' '$(1)'

# The rule to create the override style sheet.
$(PATH_PROCESS)/$(1).usfm.sty :
	@echo INFO: Creating: $$@
	@echo \# Override PTX style sheet for $(1).usfm, edit as needed >> $$@

# Process a single component and produce the final PDF. Special dependencies
# are set for the .adj and .piclist files in case they have been altered.
# The .piclist file is created in the content_illustrations.mk rules file.
$(PATH_PROCESS)/$(1).pdf : \
	$(PATH_TEXTS)/$(1).usfm \
	$(PATH_TEXTS)/$(1).usfm.adj \
	$(PATH_TEXTS)/$(1).usfm.piclist \
	$(PATH_PROCESS)/$(1).usfm.tex \
	$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX) | $(PATH_PROCESS)/$(1).usfm.sty $(DEPENDENT_FILE_LIST)
	@echo INFO: Creating book PDF file: $$@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(1).usfm.tex
#	cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex --no-pdf $(1).tex
#	cd $(PATH_PROCESS) && xdvipdfmx $(1).xdv

# Open the PDF file with reader
view-$(1) : $(PATH_PROCESS)/$(1).pdf
	@- $(CLOSEPDF)
	@if [ $(WATERMARK) = "true" ] ; then \
		echo INFO: Adding watermark to ouput: $(PATH_PROCESS)/$(1).pdf; \
		pdftk $(PATH_PROCESS)/$(1).pdf background $(PATH_ILLUSTRATIONS)/$(FILE_WATERMARK) output $(PATH_PROCESS)/tmp.pdf; \
		cp $(PATH_PROCESS)/tmp.pdf $(PATH_PROCESS)/$(1).pdf; \
		rm -f $(PATH_PROCESS)/tmp.pdf; \
	fi
	@ $(VIEWPDF) $$< &

# Open the SFM file with the text editor
edit-$(1) : $(PATH_TEXTS)/$(1).usfm
	@ $(EDITSFM) $$< &

# Shortcut to open the PDF file
$(1) : $(PATH_PROCESS)/$(1).pdf

# Make adjustment file
$(PATH_TEXTS)/$(1).usfm.adj :
	@echo INFO: Creating the adjustments file: $$@
	@$(PY_RUN_PROCESS) make_para_adjust_file $(1) $(PATH_TEXTS)/$(1).usfm

# Make illustrations file if illustrations are used in this pub
# If there is a path/file listed in the illustrationsLib field
# this rule will create a piclist file for the book being processed.
# Also, the make_piclist_file.py script it will do the illustration
# file copy and linking operations. It is easier to do that in that
# context than in the Makefile context.
$(PATH_TEXTS)/$(1).usfm.piclist : | $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_ILLUSTRATION_CAPTIONS)
ifneq ($(PATH_ILLUSTRATIONS_LIB),)
	@echo INFO: Creating illustrations list file: $$@
	@$(PY_RUN_PROCESS) make_piclist_file $(1) $(PATH_TEXTS)/$(1).usfm
endif

# Rules for cleaning up content process files

# Remove the PDF for this component only
pdf-remove-$(1) :
	@echo INFO: Removing file: $(PATH_PROCESS)/$(1).pdf
	@rm -f $(PATH_PROCESS)/$(1).pdf

# Remove the adjustment file for this component only
adjfile-remove-$(1) :
	@echo INFO: Removing file: $(PATH_TEXTS)/$(1).usfm.adj
	@rm -f $(PATH_TEXTS)/$(1).usfm.adj

# Remove the picture placement file for this component only
picfile-remove-$(1) :
	@echo INFO: Removing file: $(PATH_TEXTS)/$(1).usfm.piclist
	@rm -f $(PATH_TEXTS)/$(1).usfm.piclist

endef

######################## End Main Macro ######################

####################### Start Main Process ###################

# Build a TeX control file that will process the components
# in a publication

# In case makefile needs things in order, we will put some
# dependent rules here before we hit the main component_rules
# building rule

# Create the main settings file for this Scripture project.
# This will contain publication format settings. Context
# specific settings are kept in the bible_settings.txt file.
# In this context using PY_RUN_PROCESS we use the
# optional passed var as a way to pass the type of control
# file we are making. In this instance, we use "project"
# because the script will know by the flag name exactly what
# it is and what goes in it.
$(PATH_PROCESS)/$(FILE_TEX_SETUP) : $(FILE_PROJECT_CONF)
	@echo INFO: Creating: $@
	@$(PY_RUN_PROCESS) make_tex_control_file '' '' '$@' 'project'

# Rule for building the TeX settings file that is used in a
# specific context.
$(PATH_PROCESS)/$(FILE_TEX_BIBLE) : $(PATH_PROCESS)/$(FILE_TEX_SETUP) $(FILE_PROJECT_CONF)
	@echo INFO: Creating: $@
	@$(PY_RUN_PROCESS) make_tex_control_file '' '' '$@' 'bible'

# Start with the OT but we don't want to do anything if there
# are no components to process

ifneq ($(MATTER_OT),)
# These build a rule (in memory) for this set of components
$(foreach v,$(MATTER_OT), $(eval $(call component_rules,$(v))))

# A rule for creating the TeX control file for when the
# entire OT is being typeset.
$(PATH_PROCESS)/$(FILE_MATTER_OT_TEX) : \
	$(FILE_PROJECT_CONF) \
	$(PATH_PROCESS)/$(FILE_TEX_BIBLE)
	@echo INFO: Creating: $@
	@$(PY_RUN_PROCESS) make_tex_control_file '' '$@' 'otc'

# Render the entire OT
$(FILE_MATTER_OT_PDF) : \
	$(foreach v,$(filter $(OT_COMPONENTS),$(MATTER_OT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(foreach v,$(filter-out $(OT_COMPONENTS),$(MATTER_OT)), \
	$(PATH_TEXTS)/$(v).usfm.piclist \
	$(PATH_TEXTS)/$(v).usfm.adj \
	$(PATH_TEXTS)/$(v).usfm) \
	$(PATH_PROCESS)/$(FILE_MATTER_OT_TEX) \
	$(DEPENDENT_FILE_LIST)
	@echo INFO: Creating: $@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex OT.tex
endif

pdf-remove-ot :
	@echo INFO: Removing file: $(FILE_MATTER_OT_PDF)
	@rm -f $(FILE_MATTER_OT_PDF)


# Moving along we will do the NT if there are any components
# listed in the project.conf file
ifneq ($(MATTER_NT),)
# These build a rule (in memory) for this set of components
$(foreach v,$(MATTER_NT), $(eval $(call component_rules,$(v))))

# A rule for creating the TeX control file for when the
# entire OT is being typeset.
$(PATH_PROCESS)/$(FILE_MATTER_NT_TEX) : \
	$(FILE_PROJECT_CONF) \
	$(PATH_PROCESS)/$(FILE_TEX_BIBLE)
	@echo INFO: Creating: $@
	@$(PY_RUN_PROCESS) make_tex_control_file '' '$@' 'ntc'

# Render the entire NT
$(FILE_MATTER_NT_PDF) : \
	$(foreach v,$(filter $(NT_COMPONENTS),$(MATTER_NT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(foreach v,$(filter-out $(NT_COMPONENTS),$(MATTER_NT)), \
	$(PATH_TEXTS)/$(v).usfm.piclist \
	$(PATH_TEXTS)/$(v).usfm.adj \
	$(PATH_TEXTS)/$(v).usfm) \
	$(PATH_PROCESS)/$(FILE_MATTER_NT_TEX) \
	$(DEPENDENT_FILE_LIST)
	@echo INFO: Creating: $@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex NT.tex

endif

pdf-remove-nt :
	@echo INFO: Removing file: $(FILE_MATTER_NT_PDF)
	@rm -f $(FILE_MATTER_NT_PDF)

# Do a component section and veiw the resulting output
view-ot : $(FILE_MATTER_OT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

view-nt : $(FILE_MATTER_NT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &


# Preproces all the components in a project then run whatever global processes
# needed like make-master-wordlist. (Add additional elements as added in the section below)
preprocess-checks: preprocess-ot preprocess-nt


# These are to augment the individual book commands set above for instances
# when a specific group is being checked. (More may need to be added)
preprocess-ot :
	@echo INFO: Preprocess checking OT components:
	@$(foreach v,$(MATTER_OT), $(PY_RUN_PROCESS) preprocessChecks $(v) $(PATH_SOURCE)/$($(v)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION); )

preprocess-nt :
	@echo INFO: Preprocess checking NT components:
	@$(foreach v,$(MATTER_NT), $(PY_RUN_PROCESS) preprocessChecks $(v) $(PATH_SOURCE)/$($(v)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION); )

# Having these here enable rules to call other rules
.PHONY: view-ot view-nt preprocess-checks


##############################################################
#               Rules for handling illustrations material
##############################################################

# Copy into place the captions.csv file that goes in the
# shared folder if needed. Also, since the new captions file
# is probably different from the one in the project, we will
# delete that one right now, for better or worse.
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_ILLUSTRATION_CAPTIONS) : | $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)
ifneq ($(PATH_ILLUSTRATIONS_LIB),)
	@echo INFO: Removing file: $(PATH_ILLUSTRATIONS)/$(FILE_ILLUSTRATION_CAPTIONS)
	@rm -f $(PATH_ILLUSTRATIONS)/$(FILE_ILLUSTRATION_CAPTIONS)
	@echo INFO: Copying $@ to $(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_ILLUSTRATION_CAPTIONS)
	@cp $@ $(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_ILLUSTRATION_CAPTIONS)
endif

# Note: The following rule is here as a reminder. The project captions.csv
# file is created during make_piclist_file process which is done in the
# $(PATH_TEXTS)/$(1).usfm.piclist rule. The issue is that if this file
# is removed or deleted it cannot be remade on its own. This can cause an
# error in certain situations. This part of the make_piclist_file process
# might need to be done alone to avoid this if ever becomes a real problem.
#$(PATH_ILLUSTRATIONS)/$(FILE_ILLUSTRATION_CAPTIONS) : | $(PATH_ILLUSTRATIONS) $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_ILLUSTRATION_CAPTIONS)
#ifneq ($(PATH_ILLUSTRATIONS_LIB),)
#	@echo INFO: Copying $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_ILLUSTRATION_CAPTIONS) to $@
#	@cp $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_ILLUSTRATION_CAPTIONS) $@
#endif
