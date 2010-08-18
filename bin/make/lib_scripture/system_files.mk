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
# 20100618 - djd - Added extra warning with zenity dialogs
#		to the clean up process.


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
  $(PATH_PROCESS)/$(FILE_TEX_STYLE) \
  $(PATH_PROCESS)/$(FILE_TEX_CUSTOM) \
  $(FILE_PROJECT_CONF)


##############################################################
#			   Rules for building and managing system files
##############################################################

# Rule to run assets check on project. This is run any time
# a typesetting process is run to be sure the files we need
# are in place. This is mainly for graphics files but could
# be easily expanded to other types as well.
check-assets :
	@echo INFO: Checking project assets - system_files
	@$(MOD_RUN_PROCESS) "$(MOD_CHECK_ASSETS)" "SYS" "" "" "basic"

# This is just like the check-assets rule but the 'refresh'
# mode is used to be sure that that existing files are over-
# written in case there has been updates.
refresh-assets :
	@echo INFO: Refreshing project assets
	@$(MOD_RUN_PROCESS) "$(MOD_CHECK_ASSETS)" "SYS" "" "" "refresh"

# Having these here enable rules to call other rules
.PHONY: check-assets refresh-assets

# Rule to create the custom style file which holds TeX code
# that is hard to automate. Project wide custom TeX macros
# should be put in this file.
$(PATH_PROCESS)/$(FILE_TEX_CUSTOM) :
	@echo INFO: Creating: $@
	@cp $(PATH_RESOURCES_PROCESS)/$(FILE_TEX_CUSTOM) $@

# In case the process folder isn't there (because of archive)
# This should be in the dependent file list.
$(PATH_PROCESS)/.stamp :
	$(call mdir,$(PATH_PROCESS))
	@touch $(PATH_PROCESS)/.stamp

# Update a .project.conf file so system improvements can be
# pulled into existing projects.
update :
	@$(MOD_RUN_PROCESS) "update_project_settings"

# Make a project.sty file (when needed)
make-styles :
	@$(MOD_RUN_PROCESS) "make_sty_file"

# Make a template from the current state of the project
make-template :
	@$(MOD_RUN_PROCESS) "make_template"

# Rule to make the project source folder. Of cource, if the user
# changes the name of the source folder after it might get
# confusing but that is more of a procedural problem.
$(PATH_SOURCE) :
	$(call mdir,$@)

# If, for some odd reason the Illustrations folder is not in
# the right place we'll put one where it is supposed to be found.
$(PATH_ILLUSTRATIONS) : | $(PATH_SOURCE)
	$(call mdir,"$(PATH_ILLUSTRATIONS)")

# The following rules will guide a process that will extract
# recorded information about this project and output it in
# a formated PDF document

# Create the .$(EXT_PDF) file
$(PATH_PROCESS)/PROJECT_INFO.$(EXT_PDF) : \
	$(PATH_TEXTS)/PROJECT_INFO.$(EXT_WORK) \
	$(PATH_PROCESS)/PROJECT_INFO.$(EXT_TEX)
	@echo INFO: Creating: $@
	@rm -f $@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(PATH_PROCESS)/PROJECT_INFO.$(EXT_TEX)

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
	echo INFO: Adding watermark; \
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
# to work ok. We will also use Zenity dialogs to help guide
# the process to avoid accidental deletion of critical data.

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
	@echo WARN: Project is locked, could not clean all files from: $(PATH_TEXTS)
endif

reset :
ifeq ($(LOCKED),0)
	$(call reset)
else
	@echo WARN: Project is locked, you are not permitted use the reset command.
endif

# Remove the book PDF file
define pdf-remove-book
	@echo WARN: Deleting: $(MATTER_BOOK_PDF)
	@rm -f $(MATTER_BOOK_PDF)
endef

# Clean out the log files
define log-clean
	@echo WARN: Cleaning out the Log folder
	@rm -f $(PATH_LOG)/*.$(EXT_LOG)
endef

# Clean the reports folder
define reports-clean
	@echo WARN: Cleaning out the Reports folder
	@rm -f $(PATH_REPORTS)/*.tmp
	@rm -f $(PATH_REPORTS)/*.$(EXT_TEXT)
	@rm -f $(PATH_REPORTS)/*.$(EXT_HTML)
	@rm -f $(PATH_REPORTS)/*.$(EXT_CSV)
endef

# Illustration folder clean up. Just take out the
# linked PNG files
define illustrations-clean
@if zenity --question --text="You have requested to clean out the Illustrations folder. If this project is part of a multi-publication group, by clicking OK, the deletion of the illustrations will effect other projects in this group that share these illustrations. Are you sure you want to do this?"; then \
	echo WARN: Deleting illustration files in: $(PATH_ILLUSTRATIONS); \
	rm -f $(PATH_ILLUSTRATIONS)/*.$(EXT_PNG); \
	rm -f $(PATH_ILLUSTRATIONS)/*.$(EXT_PDF); \
else \
	echo "INFO: Deletion of the illustration files has been canceled."; \
fi

endef

# This supports clean-all or can be called alone.
define picfile-clean-all
@if zenity --question --text="By continuing with this process you will delete your illustration placement files. These control where pictures are placed in your publication. Are you sure you want to do this?"; then \
	echo WARN: Deleting all .$(EXT_PICLIST) files from: $(PATH_TEXTS) ; \
	rm -f $(PATH_TEXTS)/*.$(EXT_PICLIST) ; \
else \
	echo "INFO: Deletion of the .$(EXT_PICLIST) files has been canceled." ; \
fi
endef

# This supports clean-all or can be called alone.
define adjfile-clean-all
@if zenity --question --text="By continuing with this process you will delete your adjustment files. These control paragraph adjustments. Are you sure you want to do this?"; then \
	echo WARN: Deleting all .$(EXT_ADJUSTMENT) files from: $(PATH_TEXTS) ; \
	rm -f $(PATH_TEXTS)/*.$(EXT_ADJUSTMENT) ; \
else \
	echo "INFO: Deletion of text adjustments has been canceled." ; \
fi
endef

# Just in case we need to clean up to have a fresh start
define process-clean
	@echo WARN: Cleaning out auto-generated files from: $(PATH_PROCESS)
	@rm -f $(PATH_PROCESS)/*.$(EXT_LOG)
	@rm -f $(PATH_PROCESS)/*.notepages
	@rm -f $(PATH_PROCESS)/*.parlocs
	@rm -f $(PATH_PROCESS)/*.delayed
	@rm -f $(PATH_PROCESS)/*.$(EXT_PDF)
	@rm -f $(PATH_PROCESS)/*.$(EXT_PDF)
endef

# This will clean out all the generated files in the texts folder.
define texts-clean
@if zenity --question --text="By continuing with this process you will delete your working source text. Are you sure you want to do this?"; then \
	echo WARN: Cleaning out working source files from: $(PATH_TEXTS) ; \
	rm -f $(PATH_TEXTS)/*.$(EXT_TEXT) ; \
	rm -f $(PATH_TEXTS)/*.$(EXT_WORK) ; \
	rm -f $(PATH_TEXTS)/*.bak ; \
	rm -f $(PATH_TEXTS)/*~ ; \
else \
	echo "INFO: Deletion working text has been canceled." ; \
fi
endef

# Just in case, here is a clean_all rule. However, be very
# when using it. It will wipe out all your previous work. This
# is mainly for using when you want to start over on a project.
define reset
	@zenity --warning --text="You have chosen to reset the project. At critical points in the process you will be given a chance to cancel specific actions. Carefully read the dialogs and answer thoughtfully. Be careful as you continue."
	@echo WARN: Resetting the project. I hope you meant to do that!
	$(call pdf-remove-book)
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
	@echo INFO: Creating: $@
	@mkdir -p $(PATH_ADMIN_WIKI)
	@cp $(PATH_WIKI_SOURCE)/* $(PATH_ADMIN_WIKI)

# Simple call to open the project wiki home page
wiki : | $(PATH_ADMIN_WIKI)
	@-$(CLOSEWIKI)
	@$(VIEWWIKI) $(PATH_ADMIN_WIKI) Home &

# Call on the project wiki notes
# (At some point we'll add a date prepend routine before the wiki page call.)
note : | $(PATH_ADMIN_WIKI)
	@-$(CLOSEWIKI)
	@$(TEXT_TO_WIKI) note $(PATH_ADMIN_WIKI)/Notes.$(EXT_TEXT)
	@$(VIEWWIKI) $(PATH_ADMIN_WIKI) Notes &

# Call on the project wiki issues page
# (At some point we'll add a date prepend routine before the wiki page call.)
issue : | $(PATH_ADMIN_WIKI)
	@-$(CLOSEWIKI)
	@$(TEXT_TO_WIKI) issue $(PATH_ADMIN_WIKI)/Issues.$(EXT_TEXT)
	@$(VIEWWIKI) $(PATH_ADMIN_WIKI) Issues &

# Call the system wiki help pages
help :
	@$(VIEWWIKI) $(PATH_SYSTEM_HELP) Home &

# Call the system wiki about page
about :
	@$(VIEWWIKI) $(PATH_SYSTEM_HELP) About &
