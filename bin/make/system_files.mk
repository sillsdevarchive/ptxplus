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


##############################################################
#               Rules for building and managing system files
##############################################################

# Make a Hyphenation folder if necessary
$(PATH_HYPHENATION) :
	mkdir -p $(PATH_HYPHENATION)

# Create the "raw" hyphenation word list file
$(TEX_HYPHENATION_WORDLIST) : $(PATH_HYPHENATION)
	$(PY_RUN_SYSTEM_PROCESS) make_hyphen_wordlist

#	touch $(TEX_HYPHENATION_WORDLIST)

# Manually create a master wordlist based on existing book
# wordlists in the Reports file. Best to run this after
# a preprocess-all command
make-master-wordlist :
	$(PY_RUN_SYSTEM_PROCESS) make_master_wordlist

# Manually create the hyphenation word list file
make-hyphen-wordlist :
	$(PY_RUN_SYSTEM_PROCESS) make_hyphen_wordlist

# Create a TeX hyphenation rules file based on what is in the
# project.conf file
$(TEX_HYPHENATION_FILE) : $(TEX_HYPHENATION_WORDLIST)
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


###############################################################
#		Final component binding rules
###############################################################

# This is the main rule for the entire Bible
$(BIBLE_FINAL) : $(MATTER_FRONT_PDF) $(MATTER_BOOKS_OT_PDF) $(MATTER_BOOKS_NT_PDF) $(MATTER_BACK_PDF) $(MATTER_MAPS_PDF)
	pdftk $(MATTER_FRONT_PDF) $(MATTER_BOOKS_OT_PDF) $(MATTER_BOOKS_NT_PDF) $(MATTER_BACK_PDF) $(MATTER_MAPS_PDF) cat output $@

# Remove the main bind PDF file
pdf-remove :
	rm -f $(BIBLE_FINAL)

# This is the caller for the main rule, let's look at the results
bind-all : $(BIBLE_FINAL)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

# This is the main binding rule plus an additional call to a booklet
# making tool.
bind-booklet : $(BIBLE_FINAL)
	@- $(CLOSEPDF)
	$(MAKE_BOOKLET) $<
	@ $(VIEWPDF) $< &


###############################################################
#		Clean up files
###############################################################

# Clean up the delivery folder if needed
bind-clean :
	rm -f $(BIBLE_FINAL)

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

# Some TeX processing goes on in the Maps folder so we'll
# clean that up too.
maps-clean :
	rm -f $(PATH_MAPS)/*.log
	rm -f $(PATH_MAPS)/*.notepages
	rm -f $(PATH_MAPS)/*.parlocs
	rm -f $(PATH_MAPS)/*.delayed
	rm -f $(PATH_MAPS)/*.tex
	rm -f $(PATH_MAPS)/*.pdf
	rm -f $(PATH_MAPS)/*.PDF

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
reset : bind-clean \
	texts-clean \
	adjfile-clean-all \
	picfile-clean-all \
	process-clean \
	maps-clean \
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

# This is for editing map data that is kept in the master csv file
maps :
	$(EDITCSV) $(PATH_MAPS)/maps_data.csv

# This will open the hyphenation word list
hyphenation :
	$(EDITCONF) $(TEX_HYPHENATION_WORDLIST)

###############################################################
