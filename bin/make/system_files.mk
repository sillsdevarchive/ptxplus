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
  $(PATH_PROCESS)/$(FILE_TEX_STYLE) \
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
	@$(PY_RUN_PROCESS) make_tex_control_file '' '' '$@' 'project'

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
$(PATH_ILLUSTRATIONS) :
	$(call mdir,$@)

# This is the main rule for copying all the shared illustration
# material like logos, watermarks, etc. First we will make the
# folder, then we will copy everthing into it.
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED) : | $(PATH_ILLUSTRATIONS)
	$(call mdir,$@)

# Watermark
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_WATERMARK) : | $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_WATERMARK),$@)

$(PATH_PROCESS)/$(FILE_WATERMARK) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_WATERMARK)
	$(call linkme,$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_WATERMARK),$@)

# BSM Logo
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_LOGO_BSM) : | $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_LOGO_BSM),$@)

$(PATH_PROCESS)/$(FILE_LOGO_BSM) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_LOGO_BSM)
	$(call linkme,$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_LOGO_BSM),$@)

# CFE Logo
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_LOGO_CFE) :| $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_LOGO_CFE),$@)

$(PATH_PROCESS)/$(FILE_LOGO_CFE) :$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_LOGO_CFE)
	$(call linkme,$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_LOGO_CFE),$@)

# Page border
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_PAGE_BORDER) : | $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)
	$(call copysmart,$(PATH_RESOURCES_ILLUSTRATIONS)/$(FILE_PAGE_BORDER),$@)

$(PATH_PROCESS)/$(FILE_PAGE_BORDER) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_PAGE_BORDER)
	$(call linkme,$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(FILE_PAGE_BORDER),$@)

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

# Make a directory
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

# Remove the book PDF file
pdf-remove-book :
	rm -f $(MATTER_BOOK_PDF)

# Clean out the log files
log-clean :
	rm -f $(PATH_LOG)/*.$(EXT_LOG)

# Clean the reports folder
reports-clean :
	rm -f $(PATH_REPORTS)/*.tmp
	rm -f $(PATH_REPORTS)/*.$(EXT_TEXT)
	rm -f $(PATH_REPORTS)/*.$(EXT_HTML)
	rm -f $(PATH_REPORTS)/*.$(EXT_CSV)

# Illustration folder clean up. Just take out the linked PNG files
illustrations-clean :
	rm -f $(PATH_ILLUSTRATIONS)/*.png

# Just in case we need to clean up to have a fresh start
process-clean :
	rm -f $(PATH_PROCESS)/*.$(EXT_LOG)
	rm -f $(PATH_PROCESS)/*.notepages
	rm -f $(PATH_PROCESS)/*.parlocs
	rm -f $(PATH_PROCESS)/*.delayed
	rm -f $(PATH_PROCESS)/*.$(EXT_PDF)
	rm -f $(PATH_PROCESS)/*.$(EXT_PDF)

# This will clean out all the generated in the texts folder.
# Be very careful with this one! You don't want to lose the
# work you put into your .$(EXT_PICLIST) and .$(EXT_ADJUSTMENT) files. Hopefully
# the lock mechanism will prevent this.
texts-clean :
ifeq ($(LOCKED),0)
	rm -f $(PATH_TEXTS)/*.$(EXT_TEXT)
	rm -f $(PATH_TEXTS)/*.$(EXT_WORK)
	rm -f $(PATH_TEXTS)/*.$(EXT_WORK)
endif
	rm -f $(PATH_TEXTS)/*.bak
	rm -f $(PATH_TEXTS)/*~

# This supports clean-all or can be called alone.
adjfile-clean-all :
ifeq ($(LOCKED),0)
	rm -f $(PATH_TEXTS)/*.$(EXT_ADJUSTMENT)
endif

# This supports clean-all or can be called alone.
picfile-clean-all :
ifeq ($(LOCKED),0)
	rm -f $(PATH_TEXTS)/*.$(EXT_PICLIST)
endif

# Just in case, here is a clean_all rule. However, be very
# when using it. It will wipe out all your previous work. This
# is mainly for using when you want to start over on a project.
reset : pdf-remove-book \
	texts-clean \
	adjfile-clean-all \
	picfile-clean-all \
	illustrations-clean \
	process-clean \
	reports-clean \
	log-clean


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


