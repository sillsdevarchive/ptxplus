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


##############################################################
#		Variables for some of the system matter
##############################################################

# This is the final output we want so we can name it here
MATTER_BOOK_PDF=$(PATH_PROCESS)/$(MATTER_BOOK).pdf

##############################################################
#			   Rules for building and managing system files
##############################################################

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

# Update a project.conf file so system improvements can be
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
	@ $(call mdir,$@)

# This is the main rule for copying all the shared illustration
# material like logos, watermarks, etc. First we will make the
# folder, then we will copy everthing into it.
$(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED) : | $(PATH_ILLUSTRATIONS)
	@ $(call mdir,$@)

$(PATH_PROCESS)/$(FILE_WATERMARK) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)
	@ $(call cplibtoshare,$(FILE_WATERMARK))
	@ $(call lnsharetoproc,$(FILE_WATERMARK))

$(PATH_PROCESS)/$(FILE_LOGO_BSM) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)
	@ $(call cplibtoshare,$(FILE_LOGO_BSM))
	@ $(call lnsharetoproc,$(FILE_LOGO_BSM))

$(PATH_PROCESS)/$(FILE_LOGO_CFE) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)
	@ $(call cplibtoshare,$(FILE_LOGO_CFE))
	@ $(call lnsharetoproc,$(FILE_LOGO_CFE))

$(PATH_PROCESS)/$(FILE_PAGE_BORDER) : $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)
	@ $(call cplibtoshare,$(FILE_PAGE_BORDER))
	@ $(call lnsharetoproc,$(FILE_PAGE_BORDER))

# The following rules will guide a process that will extract
# recorded information about this project and output it in
# a formated PDF document

# Create the .pdf file
$(PATH_PROCESS)/PROJECT_INFO.pdf : \
	$(PATH_TEXTS)/PROJECT_INFO.usfm \
	$(PATH_PROCESS)/PROJECT_INFO.tex
	@echo INFO: Creating: $@
	@rm -f $@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(PATH_PROCESS)/PROJECT_INFO.tex

# Create the .tex file that drives the typesetting process
$(PATH_PROCESS)/PROJECT_INFO.tex :
	@echo INFO: Creating: $@
	@echo \\input $(FILE_TEX_MACRO) > $@
	@echo \\input $(FILE_TEX_SETUP) >> $@
	@echo \\BodyColumns=1 >> $@
	@echo \\ptxfile{$(PATH_TEXTS)/PROJECT_INFO.usfm} >> $@
	@echo '\\bye' >> $@


###############################################################
#		Shared functions
###############################################################

define mdir
@echo INFO: Creating $(1)
@mkdir -p $(1)
endef

define watermark
@if [ $(WATERMARK) = "true" ] ; then \
	echo INFO: Adding watermark to ouput: $(1); \
	pdftk $(1) background $(PATH_PROCESS)/$(FILE_WATERMARK) output $(PATH_PROCESS)/tmp.pdf; \
	cp $(PATH_PROCESS)/tmp.pdf $(1); \
	rm -f $(PATH_PROCESS)/tmp.pdf; \
fi
endef

define cplibtoshare
@echo INFO: Copying: $(PATH_RESOURCES_ILLUSTRATIONS)/$(1) to $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(1)
@cp $(PATH_RESOURCES_ILLUSTRATIONS)/$(1) $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(1)
endef

define lnsharetoproc
@echo INFO: Linking: $(PATH_SOURCE)/$(PATH_ILLUSTRATIONS_SHARED)/$(1) to $(PATH_ILLUSTRATIONS)/$(1)
@ln -sf $(shell readlink -f -- $(PATH_SOURCE))/$(PATH_ILLUSTRATIONS_SHARED)/$(1) $(PATH_PROCESS)/$(1)
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
	@ $(call watermark,$<)
	@ $(VIEWPDF) $< &


###############################################################
#		Clean up files
###############################################################

# Remove the book PDF file
pdf-remove-book :
	rm -f $(MATTER_BOOK_PDF)

# Clean out the log files
log-clean :
	rm -f $(PATH_LOG)/*.log

# Clean the reports folder
reports-clean :
	rm -f $(PATH_REPORTS)/*.tmp
	rm -f $(PATH_REPORTS)/*.txt
	rm -f $(PATH_REPORTS)/*.html
	rm -f $(PATH_REPORTS)/*.csv

# Illustration folder clean up. Just take out the linked PNG files
illustrations-clean :
	rm -f $(PATH_ILLUSTRATIONS)/*.png

# Just in case we need to clean up to have a fresh start
process-clean :
	rm -f $(PATH_PROCESS)/*.log
	rm -f $(PATH_PROCESS)/*.notepages
	rm -f $(PATH_PROCESS)/*.parlocs
	rm -f $(PATH_PROCESS)/*.delayed
	rm -f $(PATH_PROCESS)/*.pdf
	rm -f $(PATH_PROCESS)/*.PDF

# This will clean out all the generated in the texts folder.
# Be very careful with this one! You don't want to lose the
# work you put into your .piclist and .adj files. Hopefully
# the lock mechanism will prevent this.
texts-clean :
ifeq ($(LOCKED),0)
	rm -f $(PATH_TEXTS)/*.txt
	rm -f $(PATH_TEXTS)/*.usfm
	rm -f $(PATH_TEXTS)/*.USFM
endif
	rm -f $(PATH_TEXTS)/*.bak
	rm -f $(PATH_TEXTS)/*~

# This supports clean-all or can be called alone.
adjfile-clean-all :
ifeq ($(LOCKED),0)
	rm -f $(PATH_TEXTS)/*.adj
endif

# This supports clean-all or can be called alone.
picfile-clean-all :
ifeq ($(LOCKED),0)
	rm -f $(PATH_TEXTS)/*.piclist
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
	$(TEXT_TO_WIKI) note $(PATH_ADMIN_WIKI)/Notes.txt
	$(VIEWWIKI) $(PATH_ADMIN_WIKI) Notes &

# Call on the project wiki issues page
# (At some point we'll add a date prepend routine before the wiki page call.)
issue : $(PATH_ADMIN_WIKI)
	@-$(CLOSEWIKI)
	$(TEXT_TO_WIKI) issue $(PATH_ADMIN_WIKI)/Issues.txt
	$(VIEWWIKI) $(PATH_ADMIN_WIKI) Issues &

# Call the system wiki help pages
help :
	$(VIEWWIKI) $(PATH_SYSTEM_HELP) Home &

# Call the system wiki about page
about :
	$(VIEWWIKI) $(PATH_SYSTEM_HELP) About &

# To edit the project.conf file
configure :
	$(EDITCONF) project.conf ptx2pdf-setup.txt ptx2pdf.sty &


