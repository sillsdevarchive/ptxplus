# matter_peripheral.mk

# This file provides build rules for building all peripheral material,
# front and back, that might go into a Scripture publication. The
# rules will be laid out so that it will allow total flexibility as
# to if matter will be placed in the front or back. For example,
# it would be possible to put the copyright page in the back of the
# publication if necessary even though that is normally not done.
# Where components will be placed will be determined by the user
# as they layout the order in the Binding section of the project.ini
# file. That information is used to auto-build the process_instructions.mk
# file. That is the file that drives this one.
#
# It is possible to pick out one component and focus on that. Several
# generic rules will be provided for that.

# History:

# 20080725 - djd - Initial draft version. Moved all the code from the
#		now deprecated matter_front.mk, matter_back.mk
#		and matter_maps.mk
# 20081010 - djd - Removed the -$(NAME_SOURCE_ORIGINAL) porton of
#		the names to avoid problems in projects where
#		multiple scripts are used.
# 20091201 - djd - Changed some process commands to be more in line
#		with others

##############################################################
#		Variables for peripheral matter
##############################################################

# Set the default to nothing here
MATTER_FRONT_PDF=
MATTER_BACK_PDF=


##############################################################
#		General rules for all peripheral matter
##############################################################

# Define the main macro rule group for what it takes to process
# peripheral matter (front and back).

define periph_rules

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
#
# A possible problem here is if the custom process was to be run on
# a peripheral file that was meant for Scripture text and changes
# were made that were not supposed to. We may need to add a little
# switch at the start of each of the text processes that would only
# perform them on specific kind of file taken from the \periph field.

ifeq ($(LOCKED),0)
$(PATH_TEXTS)/$(1) : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/$(1)
	@echo Regenerating $(PATH_TEXTS)/$(1)
	@rm -f $(PATH_TEXTS)/$(1)
	@$(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(1) '$$<' '$$@'
	@$(PY_PROCESS_SCRIPTURE_TEXT) CopyIntoSystem $(1) '$$<' '$$@'
	@$(PY_PROCESS_SCRIPTURE_TEXT) TextProcesses $(1) '$$@' '$$@'
endif

# This enables us to do the preprocessing on a single peripheral item. Then it
# will open the log file produced from the processes run.
preprocess-$(1) : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/$(1)
ifeq ($(LOCKED),0)
	@echo Preprocessing $(1)
	@rm -f $(PATH_TEXTS)/$(1)
	@$(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(1) '$$<'
else
	@echo Source locked: Will not preprocess file: $(1)
endif

# NOTE:
# If a peripheral template file does not exist for a given object
# in the template lib then one will need to be created manually
# for the project. Unfortunatly, there is not clean way to do this
# automatically. What is needed is a user template folder in
# ~/.ptxplus where one could be made automatically. For now we
# will just have to let the uggly error message be our guide.

# Output to the TeX control file (Do a little clean up first)
# The ($(1)_TEXSPECIAL) below is a workaround to overcome a current
# limitation with styles being applied to individual parts of a
# publication. This will insert a specially defined var done in
# the makefile.conf file.
$(PATH_PROCESS)/$(1).tex : $(PATH_PROCESS)/FRONT_MATTER.tex $(PATH_PROCESS)/BACK_MATTER.tex
	@cp $(PATH_TEMPLATES)/$(1).tex '$$@'

# Process a single peripheral item and produce the final PDF.
$(PATH_PROCESS)/$(1).pdf : \
	$(PATH_TEXTS)/$(1) \
	$(PATH_PROCESS)/$(1).tex \
	$(DEPENDENT_FILE_LIST)
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(1).tex

# Each peripheral item needs a source but if it doesn't exist in the source folder
# then we need to copy one in from the templates we have in the system.
$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/$(1) :
	@echo WARNING: Peripheral item: $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/$(1) missing adding template to project.
	@cp $(PATH_TEMPLATES)/$(1) '$$@'

# Open the PDF file with reader
view-$(1) : $(PATH_PROCESS)/$(1).pdf $(DEPENDENT_FILE_LIST)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $$< &

# Do not open the PDF file with reader
$(1) : $(PATH_PROCESS)/$(1).pdf $(DEPENDENT_FILE_LIST)

# Remove the PDF file for this source file
pdf-remove-$(1) :
	rm -f $(PATH_PROCESS)/$(1).pdf

endef

define uniq
$(if $(1),$(firstword $(1)) $(call uniq,$(filter-out $(firstword $(1)),$(1))),)
endef

define matter_binding

ifneq ($($(1)),)
$(1)_PDF = $(PATH_PROCESS)/$(1).pdf
$(PATH_PROCESS)/$(1).pdf : $(foreach v,$($(1)),$(PATH_PROCESS)/$(v).pdf) $(DEPENDENT_FILE_LIST)
	pdftk $(foreach v,$($(1)),$(PATH_PROCESS)/$(v).pdf) cat output $$@
endif
endef


##############################################################
#		Main processing rules
##############################################################

# This builds a rule (in memory) for these sets of files


# Cover matter binding rules
$(eval $(call matter_binding,MATTER_COVER))

# Front matter binding rules
$(eval $(call matter_binding,MATTER_FRONT))

# Back matter binding rules
$(eval $(call matter_binding,MATTER_BACK))

# Most front matter peripheral .tex files will have a dependency
# on FRONT_MATTER.tex even if it doesn't there is a hard coded
# dependency here that will be met if called on.
$(PATH_PROCESS)/FRONT_MATTER.tex :
	@cp $(PATH_TEMPLATES)/FRONT_MATTER.tex '$$@'

# Most back matter peripheral .tex files will have a dependency
# on BACK_MATTER.tex even if it doesn't there is a hard coded
# dependency here that will be met if called on.
$(PATH_PROCESS)/BACK_MATTER.tex :
	@cp $(PATH_TEMPLATES)/BACK_MATTER.tex '$$@'

$(foreach v,$(call uniq,$(MATTER_COVER) $(MATTER_FRONT) $(MATTER_BACK)),$(eval $(call periph_rules,$(v))))

# Produce all the outer cover material in one PDF file
view-cover : $(MATTER_COVER_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

# To produce individual elements of the outer cover just
# use: ptxplus view-<file_name>

# Produce just the font matter (bound)
view-front : $(MATTER_FRONT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

# Produce just the back matter (bound)
view-back : $(MATTER_BACK_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

# Clean up rules for peripheral matter

# Remove the cover matter PDF file
pdf-remove-cover :
	rm -f $(MATTER_COVER_PDF)

# Remove the front matter PDF file
pdf-remove-front :
	rm -f $(MATTER_FRONT_PDF)

# Remove the back matter PDF file
pdf-remove-back :
	rm -f $(MATTER_BACK_PDF)





# Make the content for a topical index from CSV data
make-topic-index :
	@$(PY_PROCESS_SCRIPTURE_TEXT) make_topic_index_file 'NA' $(PATH_SOURCE)$(PATH_SOURCE_PERIPH)/TOPICAL_INDEX.CSV $(PATH_TEXTS)/TOPICAL_INDEX.USFM
