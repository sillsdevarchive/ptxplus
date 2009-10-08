# matter_books.mk

# This file provides build rules for building all mid-matter material, i.e.
# all the main Scripture content that might go into a publication.

# History:

# 20080404 - djd - Initial draft version. Moved all the code from the
#			now Deprecated main.mk which was written mainly
#			by Martin Hoskins.
# 20080407 - djd - Bug fixes on PDF view and also fixed include bug
#			on PROCESS_INSTRUCTIONS call that was failing on
#			setup. Also moved in the setup rules
# 20080410 - djd - Changed path names to more descriptive ones
# 20080418 - djd - Moved the vars into the file
# 20080421 - djd - Added middle_clean rule
# 20080421 - djd - Changed books command to books_bind for consitancy
# 20080421 - djd - Changed MIDDLE name indicator to BOOKS to
#		be more consistant in function
# 20080429 - djd - Added more vars to picture placement
# 20080501 - djd - Added $(PROJECT_CODE)/ to TeX setting files
#		in the whole book process to prevent the
#		settings files from being killed.
# 20080501 - djd - Removed image file extention vars, we assume
#		png as the file format we will use.
# 20080512 - djd - Added draft code to enable binding multiple
#		pulications from mulitple books
# 20080514 - djd - Added support for 3 level projects
# 20080531 - djd - Moved make_para_adjust_file.py to be a preprocess
# 20080624 - djd - Removed individual checks from this set of rules.
#		If that is implemented it will be in another rule
#		file to keep the code manageable.
# 20080703 - djd - Added some dependency rules back in for
#		.piclist and .adj processing.
# 20080710 - djd - Removed dependency files for .adj processing
#		I am trying to avoid the rule being called when
#		not needed.
# 20080725 - djd - Fixed bug in the bind-all rule. Also added a
#		rule for deleting system text when it hasn't been
#		checked or has been changed. Also, changed _base
#		to _book
# 20080820 - djd - Changed to simplified lower case names for
#		internal system file names
# 20080822 - djd - Changed to reflect moving the Source folder
#		to be inside the project
# 20081230 - djd - Removed piclist and adjustment file creation
#		from version control. Now controled manually via the GUI
#		or the command line.
# 20090110 - djd - Added booklet binding for single book files
# 20090218 - djd - Added warning messages and extra locks for
#		protecting text when the system is locked down
# 20090914 - djd - Changed the preprocess-book command to just
#		"preprocess" to avoid conflict with maps.


##############################################################
#		Variales for Middle Matter
##############################################################

# Do a blank setting on the following
MATTER_BOOKS_OT_PDF=
MATTER_BOOKS_OT_TEX=
MATTER_BOOKS_NT_PDF=
MATTER_BOOKS_NT_TEX=


##############################################################
#		Rules for publication Scripture content
##############################################################

# Before we can typeset we have to copy the source text
# into the Source folder. After that further preprocessing
# is needed. Any predictable process will be done here.
# The list of processes can be edited in the project ini
# ini under the [Preproces] section.

# Define the main macro for what it takes to process an
# individual book.

define book_rules

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
$(PATH_TEXTS)/$(1).usfm : $(PATH_SOURCE)/$($(1)_book)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION)
	rm -f $(PATH_TEXTS)/$(1).usfm
	$(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(1) '$$<' '$$@'
	$(PY_PROCESS_SCRIPTURE_TEXT) CopyIntoSystem $(1) '$$<' '$$@'
	$(PY_PROCESS_SCRIPTURE_TEXT) TextProcesses $(1) '$$@' '$$@'
else
#	@echo File $(PATH_TEXTS)/$(1).usfm is locked
endif

# This enables us to do the preprocessing on a single book and view the log file
# We will not do individual checks here as there can be a good number of them.
# If we implement that it will be in a different control file to simplify things.
# If we are checking text that means we are not sure about how good it is. That
# being the case, we don't want this text in the system yet so the very first
# thing we do is try to delete any existing copies from the source directory.
preprocess-$(1) : $(PATH_SOURCE)/$($(1)_book)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION) $(DEPENDENT_FILE_LIST)
ifeq ($(LOCKED),0)
	rm -f $(PATH_TEXTS)/$(1).usfm
	$(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(1) '$$<'
endif

#################################
# Problem: It would be nice if we could include a warning to users in the above process
# whenever the system is locked so they know why it isn't processing their text. The
# problem is that an else statement with a warning doesn't seem to work. Don't know
# why so I had to remove it for now.
#################################

# TeX control - Call the TeX control file creation script which will
# create a TeX control file on the fly.
$(PATH_PROCESS)/$(1).tex :
	$(PY_PROCESS_SCRIPTURE_TEXT) make_tex_control_file $(1) 'Null' '$$@'

# Process a single book and produce the final PDF. Special dependencies
# are set for the .adj and .piclist files in case they have been altered.
$(PATH_PROCESS)/$(1).pdf : \
	$(PATH_TEXTS)/$(1).usfm \
	$(PATH_TEXTS)/$(1).usfm.adj \
	$(PATH_TEXTS)/$(1).usfm.piclist \
	$(PATH_PROCESS)/$(1).tex \
	$(TEX_HYPHENATION_FILE) \
	$(DEPENDENT_FILE_LIST)
	cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(1).tex
#	cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex --no-pdf $(1).tex
#	cd $(PATH_PROCESS) && xdvipdfmx $(1).xdv

# Open the PDF file with reader
view-$(1) : $(PATH_PROCESS)/$(1).pdf
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $$< &

# Open the SFM file with the text editor
edit-$(1) : $(PATH_TEXTS)/$(1).usfm
	@ $(EDITSFM) $$< &

# Shortcut to open the PDF file
$(1) : $(PATH_PROCESS)/$(1).pdf

# Make illustrations file manualy
make-picfile-$(1) :
	$(PY_PROCESS_SCRIPTURE_TEXT) make_piclist_file $(1) $(PATH_TEXTS)/$(1).usfm

# Make illustrations file automatically
$(PATH_TEXTS)/$(1).usfm.piclist : $(PATH_TEXTS)/$(1).usfm
	$(PY_PROCESS_SCRIPTURE_TEXT) make_piclist_file $(1) $(PATH_TEXTS)/$(1).usfm

# Make adjustment file
$(PATH_TEXTS)/$(1).usfm.adj :
	$(PY_PROCESS_SCRIPTURE_TEXT) make_para_adjust_file $(1) $(PATH_TEXTS)/$(1).usfm

# Remove the PDF for this book only
pdf-remove-$(1) :
	rm -f $(PATH_PROCESS)/$(1).pdf

# Remove the adjustment file for this book only
adjfile-remove-$(1) :
	rm -f $(PATH_TEXTS)/$(1).usfm.adj

# Remove the picture placement file for this book only
picfile-remove-$(1) :
	rm -f $(PATH_TEXTS)/$(1).usfm.piclist

# Bind this book into a booklet
bind-booklet-$(1) : $(PATH_PROCESS)/$(1).pdf
	@- $(CLOSEPDF)
	$(MAKE_BOOKLET) $$<
	@ $(VIEWPDF) $$< &

endef

######################## End Main Macro ######################

####################### Start Main Process ###################

# Build a TeX control file that will process the books in a publication

# Start with the OT but we don't want to do anything if there are no books to process
ifneq ($(MATTER_BOOKS_OT),)
# These build a rule (in memory) for this set of books
$(foreach v,$(MATTER_BOOKS_OT), $(eval $(call book_rules,$(v))))
MATTER_BOOKS_OT_PDF=$(PATH_PROCESS)/MATTER_BOOKS_OT.pdf
MATTER_BOOKS_OT_TEX=$(PATH_PROCESS)/MATTER_BOOKS_OT.tex

# Rule for building the TeX file for an entire publication
# like NT, OT or Bible. This is done with a little Perl code
# here. We may want to change this but as long as it works...
$(MATTER_BOOKS_OT_TEX) : project.conf
	$(PY_PROCESS_SCRIPTURE_TEXT) make_tex_control_file ot 'Null' '$@'


#	perl -e 'print "\\input $(TEX_PTX2PDF)\n\\input $(TEX_SETUP)\n"; for (@ARGV) {print "\\ptxfile{$$_}\n"}; print "\n\\bye\n"' $(foreach v,$(MATTER_BOOKS_OT),$(PATH_TEXTS)/$(v).usfm) > $@

# Render the entire OT
$(MATTER_BOOKS_OT_PDF) : \
	$(foreach v,$(filter $(OT_BOOKS),$(MATTER_BOOKS_OT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(foreach v,$(filter-out $(OT_BOOKS),$(MATTER_BOOKS_OT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(DEPENDENT_FILE_LIST) \
	$(MATTER_BOOKS_OT_TEX)
	cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex MATTER_BOOKS_OT.tex
endif

# Moving along we will do the NT if there are any books listed in the project.conf file
ifneq ($(MATTER_BOOKS_NT),)
# These build a rule (in memory) for this set of books
$(foreach v,$(MATTER_BOOKS_NT), $(eval $(call book_rules,$(v))))
MATTER_BOOKS_NT_PDF=$(PATH_PROCESS)/MATTER_BOOKS_NT.pdf
MATTER_BOOKS_NT_TEX=$(PATH_PROCESS)/MATTER_BOOKS_NT.tex

# Just like with the OT, this builds the .tex control file for all NT books
$(MATTER_BOOKS_NT_TEX) : project.conf
	$(PY_PROCESS_SCRIPTURE_TEXT) make_tex_control_file nt 'Null' '$@'

#	perl -e 'print "\\input $(TEX_PTX2PDF)\n\\input $(TEX_SETUP)\n"; for (@ARGV) {print "\\ptxfile{$$_}\n"}; print "\n\\bye\n"' $(foreach v,$(MATTER_BOOKS_NT),$(PATH_TEXTS)/$(v).usfm) > $@

# Render the entire NT
$(MATTER_BOOKS_NT_PDF) : \
	$(foreach v,$(filter $(NT_BOOKS),$(MATTER_BOOKS_NT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(foreach v,$(filter-out $(NT_BOOKS),$(MATTER_BOOKS_NT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(DEPENDENT_FILE_LIST) \
	$(MATTER_BOOKS_NT_TEX)
	cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex MATTER_BOOKS_NT.tex
endif

# Do a book section and veiw the resulting output
view-ot : $(MATTER_BOOKS_OT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

view-nt : $(MATTER_BOOKS_NT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &


# Preproces all the books in a project then run whatever global processes
# needed like make-master-wordlist.
preprocess-checks:
	@echo Preprocess checking OT books:
	@$(foreach v,$(MATTER_BOOKS_OT), $(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(v) $(PATH_SOURCE)/$($(v)_book)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION); )
	@echo Preprocess checking NT books:
	@$(foreach v,$(MATTER_BOOKS_NT), $(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(v) $(PATH_SOURCE)/$($(v)_book)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION); )

# Manually create a master wordlist based on existing book
# wordlists in the Reports file. Best to run this after
# a preprocess-all command
make-master-wordlist : preprocess-checks
	@echo Creating a new master word list
	@$(PY_RUN_SYSTEM_PROCESS) make_master_wordlist

# Manually create the hyphenation word list file
$(newHyphenationFile) : $(PATH_HYPHENATION) make-master-wordlist
	@echo Creating a new hyphenation word list
	@$(PY_RUN_SYSTEM_PROCESS) make_hyphen_wordlist

# Manually create the hyphenation word list file
force-make-hyphen-wordlist : $(PATH_HYPHENATION) make-master-wordlist
	@echo Creating a new hyphenation word list
	@$(PY_RUN_SYSTEM_PROCESS) make_hyphen_wordlist

# This enables all the preprocessing to be done in one command
preprocess: force-make-hyphen-wordlist
	@echo Completed preprocessing steps

.PHONY: view-ot view-nt preprocess make-hyphen-wordlist make-master-wordlist preprocess-checks
