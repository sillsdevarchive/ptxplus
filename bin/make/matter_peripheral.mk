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
ifeq ($(LOCKED),0)
$(PATH_TEXTS)/$(1).usfm : $(PATH_PERIPH)/$($(1)_periph).$(NAME_SOURCE_EXTENSION)
	rm -f $(PATH_TEXTS)/$(1).usfm
	$(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(1) '$$<' '$$@'
	$(PY_PROCESS_SCRIPTURE_TEXT) CopyIntoSystem $(1) '$$<' '$$@'
	$(PY_PROCESS_SCRIPTURE_TEXT) TextProcesses $(1) '$$@' '$$@'
endif

# This enables us to do the preprocessing on a single peripheral item. Then it
# will open the log file produced from the processes run.
preprocess-$(1) : $(PATH_PERIPH)/$($(1)_periph).$(NAME_SOURCE_EXTENSION)
	rm -f $(PATH_TEXTS)/$(1).usfm
	$(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(1) '$$<'

# Output to the TeX control file (Do a little clean up first)
# The ($(1)_TEXSPECIAL) below is a workaround to overcome a current
# limitation with styles being applied to individual parts of a
# publication. This will insert a specially defined var done in
# the makefile.conf file.
$(PATH_PROCESS)/$(1).tex :
	echo '\\input $(TEX_PTX2PDF)' >> $$@
	echo '\\input $(TEX_SETUP)' >> $$@
	echo '$($(1)_TEXSPECIAL) \\ptxfile{$(PATH_TEXTS)/$(1).usfm}' >> $$@
	echo '\\bye' >> $$@

# Process a single peripheral item and produce the final PDF.
$(PATH_PROCESS)/$(1).pdf : \
	$(PATH_TEXTS)/$(1).usfm \
	$(PATH_PROCESS)/$(1).tex \
	$(DEPENDENT_FILE_LIST)
	cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(1).tex

# Each peripheral item needs a source but if it doesn't exist in the source folder
# then we need to copy one in from the templates we have in the system.
$(PATH_PERIPH)/$($(1)_periph).$(NAME_SOURCE_EXTENSION) :
	cp $(PATH_PERIPH_SOURCE)/$($(1)_periph).usfm '$$@'

# Open the PDF file with reader
view-$(1) : $(PATH_PROCESS)/$(1).pdf $(DEPENDENT_FILE_LIST)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $$< &

# Do not open the PDF file with reader
$(1) : $(PATH_PROCESS)/$(1).pdf $(DEPENDENT_FILE_LIST)

endef


##############################################################
#		Main processing rules
##############################################################

# This builds a rule (in memory) for all peripheral items using
# the macro above. These will be called below when we process
# the individual items.
$(foreach v,$(ALL_PERIPH), $(eval $(call periph_rules,$(v))))


###############################################################


# Cover matter binding rules
ifneq ($(MATTER_COVER),)
MATTER_COVER_PDF = $(PATH_PROCESS)/MATTER_COVER.pdf
$(MATTER_COVER_PDF) : $(foreach v,$(MATTER_COVER),$(PATH_PROCESS)/$(v).pdf) $(DEPENDENT_FILE_LIST)
	pdftk $(foreach v,$(MATTER_COVER),$(PATH_PROCESS)/$(v).pdf) cat output $@

endif

# Front matter binding rules
ifneq ($(MATTER_FRONT),)
MATTER_FRONT_PDF = $(PATH_PROCESS)/MATTER_FRONT.pdf
$(MATTER_FRONT_PDF) : $(foreach v,$(MATTER_FRONT),$(PATH_PROCESS)/$(v).pdf) $(DEPENDENT_FILE_LIST)
	pdftk $(foreach v,$(MATTER_FRONT),$(PATH_PROCESS)/$(v).pdf) cat output $@

endif

# Back matter binding rules
ifneq ($(MATTER_BACK),)
MATTER_BACK_PDF = $(PATH_PROCESS)/MATTER_BACK.pdf
$(MATTER_BACK_PDF) : $(foreach v,$(MATTER_BACK),$(PATH_PROCESS)/$(v).pdf) $(DEPENDENT_FILE_LIST)
	pdftk $(foreach v,$(MATTER_BACK),$(PATH_PROCESS)/$(v).pdf) cat output $@

endif

# Produce just the font matter (bound)
front : $(MATTER_FRONT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

# Produce just the back matter (bound)
back : $(MATTER_BACK_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &
