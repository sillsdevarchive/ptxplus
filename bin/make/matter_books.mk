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
# 20091202 - djd - Changed the output names for NT and OT processing
# 20091210 - djd - Changed some more names to make things more
#		consistant for component processing
# 20100301 - djd - Moved out hyphenation file creation rules
# 20100414 - djd - Changed the way illustrations are handled and
#		added some more echo INFO statements


##############################################################
#		Variales for Middle Matter
##############################################################

# Do a blank setting on the following
MATTER_OT_PDF=
MATTER_OT_TEX=
MATTER_NT_PDF=
MATTER_NT_TEX=


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
	@$(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(1) '$$<' '$$@'
	@$(PY_PROCESS_SCRIPTURE_TEXT) CopyIntoSystem $(1) '$$<' '$$@'
	@$(PY_PROCESS_SCRIPTURE_TEXT) TextProcesses $(1) '$$@' '$$@'
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
	@$(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(1) '$$<'
endif

#################################
# Problem: It would be nice if we could include a warning to users in the above process
# whenever the system is locked so they know why it isn't processing their text. The
# problem is that an else statement with a warning doesn't seem to work. Don't know
# why so I had to remove it for now.
#################################

# TeX control - Call the TeX control file creation script which will
# create a TeX control file on the fly.
# Just in case we will throw in the watermark pages here too.
$(PATH_PROCESS)/$(1).tex : \
	$(PATH_PROCESS)/DraftWatermark-60.pdf \
	$(PATH_PROCESS)/DraftWatermark-50.pdf \
	$(PATH_PROCESS)/DraftWatermark-A5.pdf
	@echo INFO: Creating book control file: $$@
	@$(PY_PROCESS_SCRIPTURE_TEXT) make_tex_control_file $(1) 'Null' '$$@'

# Process a single component and produce the final PDF. Special dependencies
# are set for the .adj and .piclist files in case they have been altered.
$(PATH_PROCESS)/$(1).pdf : \
	$(PATH_TEXTS)/$(1).usfm \
	$(PATH_TEXTS)/$(1).usfm.adj \
	$(PATH_TEXTS)/$(1).usfm.piclist \
	$(PATH_PROCESS)/$(1).tex | $(DEPENDENT_FILE_LIST)
	@echo INFO: Creating book PDF file: $$@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(1).tex
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

# Make illustrations file if illustrations are used in this pub
# If there is a path/file listed in the illustrationsLib field
# this rule will create a piclist file for the book being processed
$(PATH_TEXTS)/$(1).usfm.piclist : | $(PATH_SOURCE)/captions.csv
ifneq ($(PATH_ILLUSTRATIONS_LIB),)
	@echo INFO: Creating illustrations list file: $$@
	@$(PY_PROCESS_SCRIPTURE_TEXT) make_piclist_file $(1) $(PATH_TEXTS)/$(1).usfm
endif

# Make adjustment file
$(PATH_TEXTS)/$(1).usfm.adj :
	@echo INFO: Creating the adjustments file: $$@
	@$(PY_PROCESS_SCRIPTURE_TEXT) make_para_adjust_file $(1) $(PATH_TEXTS)/$(1).usfm

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

# Create the captions file if illustrations are used in this
# project
$(PATH_SOURCE)/captions.csv :
ifneq ($(PATH_ILLUSTRATIONS_LIB),)
	@echo INFO: Copying captions.csv to $(PATH_SOURCE)
	@cp $(PATH_RESOURCES_ILLUSTRATIONS)/captions.csv $@
endif


# Start with the OT but we don't want to do anything if there
# are no components to process
ifneq ($(MATTER_OT),)
# These build a rule (in memory) for this set of components
$(foreach v,$(MATTER_OT), $(eval $(call component_rules,$(v))))
MATTER_OT_PDF=$(PATH_PROCESS)/OT.pdf
MATTER_OT_TEX=$(PATH_PROCESS)/OT.tex

# Rule for building the TeX file for an entire publication
# like NT, OT or Bible. This is done with a little Perl code
# here. We may want to change this but as long as it works...
# Also, I will throw in the watermark pages (this needs to be changed!)
$(MATTER_OT_TEX) : \
	$(PATH_PROCESS)/DraftWatermark-60.pdf \
	$(PATH_PROCESS)/DraftWatermark-50.pdf \
	$(PATH_PROCESS)/DraftWatermark-A5.pdf \
	project.conf
	$(PY_PROCESS_SCRIPTURE_TEXT) make_tex_control_file OT 'Null' '$@'


#	perl -e 'print "\\input $(TEX_PTX2PDF)\n\\input $(TEX_SETUP)\n"; for (@ARGV) {print "\\ptxfile{$$_}\n"}; print "\n\\bye\n"' $(foreach v,$(MATTER_OT),$(PATH_TEXTS)/$(v).usfm) > $@

# Render the entire OT
$(MATTER_OT_PDF) : \
	$(foreach v,$(filter $(OT_COMPONENTS),$(MATTER_OT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(foreach v,$(filter-out $(OT_COMPONENTS),$(MATTER_OT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(DEPENDENT_FILE_LIST) \
	$(MATTER_OT_TEX)
	cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex OT.tex
endif

pdf-remove-ot :
	@echo INFO: Removing file: $(MATTER_OT_PDF)
	rm -f $(MATTER_OT_PDF)

# Moving along we will do the NT if there are any components
# listed in the project.conf file
ifneq ($(MATTER_NT),)
# These build a rule (in memory) for this set of components
$(foreach v,$(MATTER_NT), $(eval $(call component_rules,$(v))))
MATTER_NT_PDF=$(PATH_PROCESS)/NT.pdf
MATTER_NT_TEX=$(PATH_PROCESS)/NT.tex

# Just like with the OT, this builds the .tex control file
# for all NT components.
# Also, I will throw in the watermark pages (this needs to be changed!)
$(MATTER_NT_TEX) : \
	$(PATH_PROCESS)/DraftWatermark-60.pdf \
	$(PATH_PROCESS)/DraftWatermark-50.pdf \
	$(PATH_PROCESS)/DraftWatermark-A5.pdf \
	project.conf
	$(PY_PROCESS_SCRIPTURE_TEXT) make_tex_control_file NT 'Null' '$@'

#	perl -e 'print "\\input $(TEX_PTX2PDF)\n\\input $(TEX_SETUP)\n"; for (@ARGV) {print "\\ptxfile{$$_}\n"}; print "\n\\bye\n"' $(foreach v,$(MATTER_NT),$(PATH_TEXTS)/$(v).usfm) > $@

# Render the entire NT
$(MATTER_NT_PDF) : \
	$(foreach v,$(filter $(NT_COMPONENTS),$(MATTER_NT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(foreach v,$(filter-out $(NT_COMPONENTS),$(MATTER_NT)), \
	$(PATH_TEXTS)/$(v).usfm) \
	$(DEPENDENT_FILE_LIST) \
	$(MATTER_NT_TEX)
	cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex NT.tex

endif

pdf-remove-nt :
	@echo INFO: Removing file: $(MATTER_NT_PDF)
	rm -f $(MATTER_NT_PDF)

# Do a component section and veiw the resulting output
view-ot : $(MATTER_OT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

view-nt : $(MATTER_NT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &


# Preproces all the components in a project then run whatever global processes
# needed like make-master-wordlist. (Add additional elements as added in the section below)
preprocess-checks: preprocess-ot preprocess-nt


# These are to augment the individual book commands set above for instances
# when a specific group is being checked. (More may need to be added)
preprocess-ot :
	@echo INFO: Preprocess checking OT components:
	@$(foreach v,$(MATTER_OT), $(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(v) $(PATH_SOURCE)/$($(v)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION); )

preprocess-nt :
	@echo INFO: Preprocess checking NT components:
	@$(foreach v,$(MATTER_NT), $(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(v) $(PATH_SOURCE)/$($(v)_component)$(NAME_SOURCE_ORIGINAL).$(NAME_SOURCE_EXTENSION); )


.PHONY: view-ot view-nt preprocess-checks

