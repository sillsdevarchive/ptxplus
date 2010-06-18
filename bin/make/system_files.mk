# system_files.mk

# This file provides build rules for setting up system files.

# History:

# 20080403 - djd - Added header information
# 20080404 - djd - Removed front, mid and back matter stuff
# 20080406 - did - Added PROCESS_INSTRUCTIONS rule
# 20080407 - djd - Moved setup functions to this module
# 20080410 - djd - Changed some vars to more descriptive ones
# 20080429 - djd - Removed PY_SETTINGS var refs
# 20080502 - djd - Changed path to process_instructions.mk
# 20080504 - djd - Added a bulk copy rule for all admin files
# 20080514 - djd - Added support for 3 level projects
# 20080517 - djd - Removed rule for making process_instructions
#		This is now handled by make_new_project.py
# 20080627 - djd - Channeled some processes through the system
#		processing command
# 20080726 - djd - Moved folder create rules to this file
# 20080807 - djd - Moved several rules out for new system
#		organization
# 20080809 - djd - Removed all system level rules as they are
#		now being handled by the Python scripts.
# 20080906 - djd - Took out the cleaning rules for source text
# 20080926 - djd - Added Wiki information management rules
# 20081004 - djd - Added project conf files editing rule
# 20090110 - djd - Added booklet binding
# 20091210 - djd - Reorganized and changed names of component
#		groups to be more consistant
# 20091211 - djd - Did more adjustments on the rules. Also, had
#		this file moved to the end of the include chain
#		because some rules in this file were dependent
#		on rules that had not been expanded yet.
# 20091223 - djd - Removed references to MAPS folder
# 20100507 - djd - Moved out rules for illustration creation
# 20100611 - djd - Added functions to share
# 20100615 - djd - Changed hard codded extions to vars


##############################################################
#		Variables for some of the system matter
##############################################################

# This is the final output we want so we can name it here
MATTER_BOOK_PDF=$(PATH_PROCESS)/$(MATTER_BOOK).$(EXT_PDF)


##############################################################
#		System-wide dependent files
##############################################################

# Build the dependent file listing here. This will include
# file paths and names we build here and the list we bring in
# from the project config file. This needs to be loaded early
# in the process. If this rules file ever needs to be moved
# down the chain this might have to move, or be put in a
# seperate file.
DEPENDENT_FILE_LIST = $(FILE_DEPENDENT_LIST) \
  $(PATH_PROCESS)/$(FILE_WATERMARK) \
  $(PATH_PROCESS)/$(FILE_LOGO_BSM) \
  $(PATH_PROCESS)/$(FILE_LOGO_CFE) \
  $(PATH_PROCESS)/$(FILE_PAGE_BORDER) \
  $(PATH_PROCESS)/$(FILE_TEX_SETUP) \
  $(PATH_PROCESS)/$(FILE_TEX_STYLE) \
  $(PATH_PROCESS)/$(FILE_BIBLE_STYLE) \
  $(PATH_PROCESS)/$(FILE_TEX_CUSTOM) \
  $(FILE_PROJECT_CONF)


##############################################################
#			   Rules for building and managing system files
##############################################################

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
	@$(PY_RUN_PROCESS) make_tex_control_file '' '' '$@' ''

# Rule to create the primary style file for the project. There
# will be lots of other secondary override stylesheets that
# are associated with specific objects but this is the "mother"
# style file.
$(PATH_PROCESS)/$(FILE_TEX_STYLE) :
	@echo INFO: Creating: $@
	@cp $(PATH_RESOURCES_PROCESS)/$(FILE_TEX_STYLE) $@

# Rule to create the custom style file which holds TeX code
# that is hard to automate. Project wide custom TeX macros
# should be put in this file.
$(PATH_PROCESS)/$(FILE_TEX_CUSTOM) :
	@echo INFO: Creating: $@
	@cp $(PATH_RESOURCES_PROCESS)/$(FILE_TEX_CUSTOM) $@

# Rule to make the project source folder. Of cource, if the user
# changes the name of the source folder after it might get
# confusing but that is more of a procedural problem.
$(PATH_SOURCE) :
	@ $(call mdir,$@)

# In case the process folder isn't there (because of archive)
# This should be in the dependent file list.
$(PATH_PROCESS)/.stamp :
	@ $(call mdir,$(PATH_PROCESS))
	touch $(PATH_PROCESS)/.stamp

# Update a .project.conf file so system improvements can be
# pulled into existing projects.
update :
	$(PY_RUN_PROCESS) update_project_settings


# Make a project.sty file (when needed)
make-styles :
	$(PY_RUN_PROCESS) make_sty_file

# Make a template from the current state of the project
make-template :
	$(PY_RUN_PROCESS) make_template

# Update a developer version of ptxplus
# This assumes you have Mercurial installed and setup
dev-update :
	cd $(PTXPLUS_BASE) && hg pull -u ptxplus

# If, for some odd reason the Illustrations folder is not in
# the right place we'll put one where it is supposed to be found.
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS) :
	$(call mdir,$@)

# Watermark
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_WATERMARK) : | $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_WATERMARK),$@)

$(PATH_PROCESS)/$(FILE_WATERMARK) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_WATERMARK)
	$(call linkme,$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_WATERMARK),$@)

# BSM Logo
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_LOGO_BSM) : | $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_LOGO_BSM),$@)

$(PATH_PROCESS)/$(FILE_LOGO_BSM) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_LOGO_BSM)
	$(call linkme,$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_LOGO_BSM),$@)

# CFE Logo
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_LOGO_CFE) :| $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_LOGO_CFE),$@)

$(PATH_PROCESS)/$(FILE_LOGO_CFE) :$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_LOGO_CFE)
	$(call linkme,$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_LOGO_CFE),$@)

# Page border
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_PAGE_BORDER) : | $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_PAGE_BORDER),$@)

$(PATH_PROCESS)/$(FILE_PAGE_BORDER) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_PAGE_BORDER)
	$(call linkme,$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/$(FILE_PAGE_BORDER),$@)

# The following rules will guide a process that will extract
# recorded information about this project and output it in
# a formated PDF document

# Create the .$(EXT_PDF) file
$(PATH_PROCESS)/PROJECT_INFO.$(EXT_PDF) : \
	$(PATH_TEXTS)/PROJECT_INFO.$(EXT_WORK) \
	$(PATH_PROCESS)/PROJECT_INFO.$(EXT_TEX)
	@echo INFO: Creating: $@
	@rm -f $@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(PATH_PROCESS)/PROJECT_INFO.$(EXT_TEX)

# Create the .$(EXT_TEX) file that drives the typesetting process
$(PATH_PROCESS)/PROJECT_INFO.$(EXT_TEX) :
	@echo INFO: Creating: $@
	@echo \\input $(FILE_TEX_MACRO) > $@
	@echo \\input $(FILE_TEX_SETUP) >> $@
	@echo \\BodyColumns=1 >> $@
	@echo \\ptxfile{$(PATH_TEXTS)/PROJECT_INFO.$(EXT_WORK)} >> $@
	@echo '\\bye' >> $@


###############################################################
#		Shared functions
###############################################################

# Just make a directory, that's all
define mdir
@echo INFO: Creating $(1)
@mkdir -p $(1)
endef

# Add a watermark to the output if called for
define watermark
@if [ "$(USE_WATERMARK)" = "true" ] ; then \
	echo INFO: Adding watermark to ouput: $(1); \
	pdftk $(1) background $(PATH_PROCESS)/$(FILE_WATERMARK) output $(PATH_PROCESS)/tmp.$(EXT_PDF); \
	cp $(PATH_PROCESS)/tmp.$(EXT_PDF) $(1); \
	rm -f $(PATH_PROCESS)/tmp.$(EXT_PDF); \
fi
endef

# This will test for a file at the indicated
# source location. If one is found, it will
# copy it to the destination. If not, a dummy
# file will be created. This is useful for
# control files that can be empty.
define copysmart
@if test -r "$(1)"; then \
	echo INFO: Copying into project: $(2); \
	cp $(1) $(2); \
else \
	echo INFO: File not found. Creating: $(2); \
	echo \# The file you have requested, $(2), is missing. This file was created to take its place. Please replace or edit this file as needed >> $(2); \
fi
endef

# Create a link into the project
define linkme
@echo INFO: Linking: $(1) to $(2)
@ln -sf $(shell readlink -f -- $(1)) $(2)
endef


###############################################################
#		Final component binding rules
###############################################################

# This is the main rule for the entire Bible
$(MATTER_BOOK_PDF) : $(MATTER_FRONT_PDF) $(MATTER_OT_PDF) $(MATTER_NT_PDF) $(MATTER_BACK_PDF) $(MATTER_MAPS_PDF)
	pdftk $(MATTER_FRONT_PDF) $(MATTER_OT_PDF) $(MATTER_NT_PDF) $(MATTER_BACK_PDF) $(MATTER_MAPS_PDF) cat output $@

# This is the caller for the main rule, let's look at the results
view-book : $(MATTER_BOOK_PDF)
	@- $(CLOSEPDF)
	$(call watermark,$<)
	@ $(VIEWPDF) $< &


###############################################################
#		Clean up files
###############################################################

# To protect the user from accidental deleations we need to
# have some contols in place. We will first set up a bunch of
# cleaning rules that call functions to do the work. I will
# use identical names between rules and functions. This seems
# to work ok.
#
# We want to implement some simple command line input from
# the user with the bash read comment. For example I would like
# to use something like:

SHELL := /bin/bash
#SHELL=/bin/bash

test :
	$(call test)

define test
@echo "A yes or no question"
@read $myinput
@if [ "$$myinput" == "yes" ]; then \
	echo Now I go do something; \
else \
	echo No I cannot do that because you answered $$myinput; \
fi
endef

# But this does not work, why?



pdf-remove-book :
	$(call pdf-remove-book)

log-clean :
	$(call log-clean)

reports-clean :
	$(call reports-clean)

illustrations-clean :
ifeq ($(LOCKED),0)
	$(call illustrations-clean)
else
	@echo WARN: Cannot delete .$(EXT_PNG) files because the project is locked!
endif

picfile-clean-all :
ifeq ($(LOCKED),0)
	$(call picfile-clean-all)
else
	@echo WARN: Cannot delete .$(EXT_PICLIST) files because the project is locked!
endif

adjfile-clean-all :
ifeq ($(LOCKED),0)
	$(call adjfile-clean-all)
else
	@echo WARN: Cannot delete .$(EXT_ADJUSTMENT) files because the project is locked!
endif

process-clean :
	$(call process-clean)

texts-clean :
ifeq ($(LOCKED),0)
	$(call texts-clean)
else
	@echo INFO: Project is locked, could not clean all files from: $(PATH_TEXTS)
endif

reset :
ifeq ($(LOCKED),0)
	$(call reset)
else
	@echo INFO: Project is locked, you are not permitted use the reset command.
endif

# Remove the book PDF file
define pdf-remove-book
	@echo INFO: Deleting: $(MATTER_BOOK_PDF)
	@rm -f $(MATTER_BOOK_PDF)
endef

# Clean out the log files
define log-clean
	@echo INFO: Cleaning out the Log folder
	@rm -f $(PATH_LOG)/*.$(EXT_LOG)
endef

# Clean the reports folder
define reports-clean
	@echo INFO: Cleaning out the Reports folder
	@rm -f $(PATH_REPORTS)/*.tmp
	@rm -f $(PATH_REPORTS)/*.$(EXT_TEXT)
	@rm -f $(PATH_REPORTS)/*.$(EXT_HTML)
	@rm -f $(PATH_REPORTS)/*.$(EXT_CSV)
endef

# Illustration folder clean up. Just take out the
# linked PNG files
define illustrations-clean
	@echo INFO: Deleting illustration files in: $(PATH_ILLUSTRATIONS)
	@rm -f $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/*.$(EXT_PNG)
	@rm -f $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS)/*.$(EXT_PDF)
endef

# This supports clean-all or can be called alone.
define picfile-clean-all
	@echo INFO: Deleting all .$(EXT_PICLIST) files from: $(PATH_TEXTS)
	@rm -f $(PATH_TEXTS)/*.$(EXT_PICLIST)
endef

# This supports clean-all or can be called alone.
define adjfile-clean-all
	@echo INFO: Deleting all .$(EXT_ADJUSTMENT) files from: $(PATH_TEXTS)
	@rm -f $(PATH_TEXTS)/*.$(EXT_ADJUSTMENT)
endef

# Just in case we need to clean up to have a fresh start
define process-clean
	@echo INFO: Cleaning out process files from: $(PATH_PROCESS)
	@rm -f $(PATH_PROCESS)/*.$(EXT_LOG)
	@rm -f $(PATH_PROCESS)/*.notepages
	@rm -f $(PATH_PROCESS)/*.parlocs
	@rm -f $(PATH_PROCESS)/*.delayed
	@rm -f $(PATH_PROCESS)/*.$(EXT_PDF)
	@rm -f $(PATH_PROCESS)/*.$(EXT_PDF)
endef

# This will clean out all the generated in the texts folder.
# Be very careful with this one! You don't want to lose the
# work you put into your .$(EXT_PICLIST) and .$(EXT_ADJUSTMENT) files. Hopefully
# the lock mechanism will prevent this.
define texts-clean
	@echo INFO: Cleaning out file from: $(PATH_TEXTS)
	@rm -f $(PATH_TEXTS)/*.$(EXT_TEXT)
	@rm -f $(PATH_TEXTS)/*.$(EXT_WORK)
	@rm -f $(PATH_TEXTS)/*.bak
	@rm -f $(PATH_TEXTS)/*~
endef

# Just in case, here is a clean_all rule. However, be very
# when using it. It will wipe out all your previous work. This
# is mainly for using when you want to start over on a project.
define reset
	@echo INFO: Resetting the project. I hope you meant to do that!
	$(call pdf-remove-book)
	$(call texts-clean)
	$(call adjfile-clean-all)
	$(call picfile-clean-all)
	$(call illustrations-clean)
	$(call process-clean)
	$(call reports-clean)
	$(call log-clean)
endef


###############################################################
#		Manage Project Information
###############################################################

# If for some reason the Wiki doesn't exist for this project
# we'll make a fresh one now.
$(PATH_ADMIN_WIKI) :
	mkdir -p $(PATH_ADMIN_WIKI)
	cp $(PATH_WIKI_SOURCE)/* $(PATH_ADMIN_WIKI)

# Simple call to open the project wiki home page
wiki : $(PATH_ADMIN_WIKI)
	@-$(CLOSEWIKI)
	$(VIEWWIKI) $(PATH_ADMIN_WIKI) Home &

# Call on the project wiki notes
# (At some point we'll add a date prepend routine before the wiki page call.)
note : $(PATH_ADMIN_WIKI)
	@-$(CLOSEWIKI)
	$(TEXT_TO_WIKI) note $(PATH_ADMIN_WIKI)/Notes.$(EXT_TEXT)
	$(VIEWWIKI) $(PATH_ADMIN_WIKI) Notes &

# Call on the project wiki issues page
# (At some point we'll add a date prepend routine before the wiki page call.)
issue : $(PATH_ADMIN_WIKI)
	@-$(CLOSEWIKI)
	$(TEXT_TO_WIKI) issue $(PATH_ADMIN_WIKI)/Issues.$(EXT_TEXT)
	$(VIEWWIKI) $(PATH_ADMIN_WIKI) Issues &

# Call the system wiki help pages
help :
	$(VIEWWIKI) $(PATH_SYSTEM_HELP) Home &

# Call the system wiki about page
about :
	$(VIEWWIKI) $(PATH_SYSTEM_HELP) About &

# To edit the .project.conf file
configure :
	$(EDITCONF) .project.conf ptx2pdf-setup.$(EXT_TEXT) ptx2pdf.sty &


