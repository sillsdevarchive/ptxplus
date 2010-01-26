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


##############################################################
#		Variables for some of the system matter
##############################################################

# This is the final output we want so we can name it here
MATTER_BOOK_PDF=$(PATH_PROCESS)/$(MATTER_BOOK).pdf

##############################################################
#               Rules for building and managing system files
##############################################################

# Make a Hyphenation folder if necessary
$(PATH_HYPHENATION) :
	mkdir -p $(PATH_HYPHENATION)

# Manually create the TeX hyphenation file
make-tex-hyphens :
	$(PY_RUN_SYSTEM_PROCESS) make_tex_hyphenation_file

# Create a TeX hyphenation rules file based on what is in the
# project.conf file
$(TEX_HYPHENATION_FILE) : $(newHyphenationFile)
	$(PY_RUN_SYSTEM_PROCESS) make_tex_hyphenation_file

# In case the process folder isn't there (because of archive)
# This should be in the dependent file list.
$(PATH_PROCESS)/.stamp :
	mkdir -p $(PATH_PROCESS)
	touch $(PATH_PROCESS)/.stamp

# Update a project.conf file so system improvements can be
# pulled into existing projects.
update :
	$(PY_RUN_SYSTEM_PROCESS) update_project_settings

# If, for some odd reason the Illustrations folder is not in
# the right place we'll put one where it is supposed to be found.
$(PATH_ILLUSTRATIONS) :
	mkdir -p $(PATH_ILLUSTRATIONS)

# Make an illustrations.csv file if needed.
$(ADMIN_ILLUSTRATIONS_CSV) : $(PATH_ILLUSTRATIONS)
	cp $(ADMIN_ILLUSTRATIONS_CSV_SOURCE) $(ADMIN_ILLUSTRATIONS_CSV)

# Make a project.sty file (when needed)
make-styles :
	$(PY_RUN_SYSTEM_PROCESS) make_sty_file

# Make a template from the current state of the project
make-template :
	$(PY_RUN_SYSTEM_PROCESS) make_template

# Update a developer version of ptxplus
# This assumes you have Mercurial installed and setup
dev-update :
	cd $(PTXPLUS_BASE) && hg pull -u ptxplus

# Make links in Process folder for the draft watermark files
# This is just a quick-and-dirty implementation. May need to be
# made more elegant in the future.
$(PATH_PROCESS)/DraftWatermark-50.pdf :
	@echo Linking to watermark file image: $(shell readlink -f -- $(PATH_ILLUSTRATIONS)/DraftWatermark-50.pdf) to $(PATH_PROCESS)/
	@ln -sf $(shell readlink -f -- $(PATH_ILLUSTRATIONS)/DraftWatermark-50.pdf) $(PATH_PROCESS)/

$(PATH_PROCESS)/DraftWatermark-60.pdf :
	@echo Linking to watermark file image: $(shell readlink -f -- $(PATH_ILLUSTRATIONS)/DraftWatermark-60.pdf) to $(PATH_PROCESS)/
	@ln -sf $(shell readlink -f -- $(PATH_ILLUSTRATIONS)/DraftWatermark-60.pdf) $(PATH_PROCESS)/

$(PATH_PROCESS)/DraftWatermark-A5.pdf :
	@echo Linking to watermark file image: $(shell readlink -f -- $(PATH_ILLUSTRATIONS)/DraftWatermark-A5.pdf) to $(PATH_PROCESS)/
	@ln -sf $(shell readlink -f -- $(PATH_ILLUSTRATIONS)/DraftWatermark-A5.pdf) $(PATH_PROCESS)/

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
# This has a dependency on FRONT_MATTER.tex which it calls from
# the matter_peripheral.mk rules file.
$(PATH_PROCESS)/PROJECT_INFO.tex : $(PATH_PROCESS)/FRONT_MATTER.tex
	@echo INFO: Creating: $@
	@echo \\input $(TEX_PTX2PDF) > $@
	@echo \\input $(TEX_SETUP) >> $@
	@echo \\input FRONT_MATTER.tex >> $@
	@echo \\ptxfile{$(PATH_TEXTS)/PROJECT_INFO.usfm} >> $@
	@echo '\\bye' >> $@

# Create the .usfm file that contains the project information
$(PATH_TEXTS)/PROJECT_INFO.usfm :
	@echo INFO: Creating: $@
	@$(PY_PROCESS_SCRIPTURE_TEXT) INFO make_project_info $@

# Just in case we need this again
#	@echo \\id OTH > $@
#	@echo \\ide UTF-8 >> $@
#	@echo \\singlecolumn >> $@
#	@echo \\periph Project Info >> $@
#	@echo \\p Here is some info on this project >> $@

# @$(PY_PROCESS_SCRIPTURE_TEXT) make_project_info $(PATH_TEXTS)/PROJECT_INFO.usfm


# View the results
view-project-info : $(PATH_PROCESS)/PROJECT_INFO.pdf
	@echo INFO: Viewing: $@
	@ $(VIEWPDF) $@ &

###############################################################
#		Final component binding rules
###############################################################

# This is the main rule for the entire Bible
$(MATTER_BOOK_PDF) : $(MATTER_FRONT_PDF) $(MATTER_OT_PDF) $(MATTER_NT_PDF) $(MATTER_BACK_PDF) $(MATTER_MAPS_PDF)
	pdftk $(MATTER_FRONT_PDF) $(MATTER_OT_PDF) $(MATTER_NT_PDF) $(MATTER_BACK_PDF) $(MATTER_MAPS_PDF) cat output $@

# This is the caller for the main rule, let's look at the results
view-book : $(MATTER_BOOK_PDF)
	@- $(CLOSEPDF)
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

# Just in case we need to clean up to have a fresh start
process-clean :
	rm -f $(PATH_PROCESS)/*.log
	rm -f $(PATH_PROCESS)/*.notepages
	rm -f $(PATH_PROCESS)/*.parlocs
	rm -f $(PATH_PROCESS)/*.delayed
	rm -f $(PATH_PROCESS)/*.tex
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
reset : book-clean \
	texts-clean \
	adjfile-clean-all \
	picfile-clean-all \
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

# To see/edit our illustrations for this project
illustrations :
	$(EDITCSV) $(ADMIN_ILLUSTRATIONS_CSV)


