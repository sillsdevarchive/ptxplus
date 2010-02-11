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
# 20090114 - djd - Changed the process model of peripheral material
#		so that now there is only one source and it is linked
#		into the project. Much easier to maintian this way.
# 20100203 - djd - Added the ability to create peripheral files
#		on the fly so there doesn't need to be a copy of
#		it in the ptxplus template lib

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

# Peripheral material is unique to each project, as such, there only
# needs to be one copy to make maintained simpler. With regular
# content text changes may be made to the working copy that are not
# made to the source. That is not the case with peripheral material.
# The source is the same as the working copy. The source is kept
# with in with the other source files so the translator has access
# to it. Checks and processes on peripheral material are currently
# done manually. This helps simplify the system and makes it more
# reliable.

$(PATH_TEXTS)/$(1) : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/$(1)
	@echo Linking project to peripheral source texts: $$(shell readlink -f -- $$<)
	ln -sf $$(shell readlink -f -- $$<) $(PATH_TEXTS)/

# Create the peripheral file by copying in the template. But if
# the template files doesn't exsit, then create a dummy one to
# serve as a placeholder. This is done by using the "test" conditional
# statement below. Note the line concatanation. This needs to be
# exicuted as one long line.
# NOTE: the use of the "|" in the dependency list. The pipe enables makefile
# to check on the dependent target, in this case a directory, but
# the current target doesn't have to be rebuilt if it has not changed.
# This is very important here because a directory will always be
# changing.
$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/$(1) : | $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)
	@if test -r $(PATH_TEMPLATES)/$(1); then \
		echo Copying into project from: $(PATH_TEMPLATES)/$(1); \
		cp $(PATH_TEMPLATES)/$(1) '$$@'; \
	else \
		echo Could not find: $$@; \
		echo Creating this file:; \
		echo Caution, you will need to edit it; \
		echo \\id OTH >> $$@; \
		echo \\ide UTF-8 >> $$@; \
		echo \\periph \<Fill in page type here\> >> $$@; \
		echo \\p This is a auto created page found at: $$@ >> $$@; \
		echo \\p Please edit as needed. >> $$@; \
	fi

# Output to the TeX control file. If one doesn't exist in the lib
# create a custom one that will need to be edited by the user.
#$(PATH_TEMPLATES)/$(1).tex :
#	@echo Could not find: $(PATH_TEMPLATES)/$(1).tex
#	@echo Creating one, you will need to edit it!
#	@echo \\input $(TEX_PTX2PDF) > $$@
#	@echo \\input $(TEX_SETUP) >> $$@
#	@echo \\input FRONT_MATTER.tex >> $$@
#	@echo \\ptxfile{$(PATH_TEXTS)/$(1)} >> $$@
#	@echo '\\bye' >> $$@

# This .tex file also generally has some dependencies on the
# FRONT/BACK_MATTER.tex files so we add them here. However, we
# will use the "|" (pipe) trick to prevent any updating in case
# the file already exists.
$(PATH_PROCESS)/$(1).tex : | $(PATH_PROCESS)/FRONT_MATTER.tex $(PATH_PROCESS)/BACK_MATTER.tex
	@if test -r $(PATH_TEMPLATES)/$(1).tex; then \
		echo Copying into project from: $(PATH_TEMPLATES)/$(1).tex; \
		cp $(PATH_TEMPLATES)/$(1).tex '$$@'; \
	else \
		echo Could not find: $$@; \
		echo Creating this file:; \
		echo Caution, you will need to edit it; \
		echo \\input $(TEX_PTX2PDF) >> $$@; \
		echo \\input $(TEX_SETUP) >> $$@; \
		echo \\input FRONT_MATTER.tex >> $$@; \
		echo %\\input FRONT_MATTER.tex >> $$@; \
		echo \\ptxfile{$(PATH_TEXTS)/$(1)} >> $$@; \
		echo '\\bye' >> $$@; \
	fi

# Process a single peripheral item and produce the final PDF.
$(PATH_PROCESS)/$(1).pdf : \
	$(PATH_TEXTS)/$(1) \
	$(PATH_PROCESS)/$(1).tex \
	$(DEPENDENT_FILE_LIST)
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(1).tex

# Open the PDF file with reader
view-$(1) : $(PATH_PROCESS)/$(1).pdf $(DEPENDENT_FILE_LIST)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $$< &

# This enables us to do the preprocessing on a single peripheral item.
preprocess-$(1) : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/$(1)
	@echo Preprocessing $(1)
	@$(PY_PROCESS_SCRIPTURE_TEXT) PreprocessChecks $(1) '$$<'

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

# Other rules will depend on this to create the project
# peripheral source folder if one doesn't exist.
$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH) :
	@echo Creating the project peripheral source folder
	@mkdir $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)


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
	@cp $(PATH_TEMPLATES)/FRONT_MATTER.tex '$@'

# Most back matter peripheral .tex files will have a dependency
# on BACK_MATTER.tex even if it doesn't there is a hard coded
# dependency here that will be met if called on.
$(PATH_PROCESS)/BACK_MATTER.tex :
	@cp $(PATH_TEMPLATES)/BACK_MATTER.tex '$@'

# This calls all the automated rules defined above and does them
# once on each file, even if the file is listed repeatedly in the
# Binding list. This is what the uniq call is for.
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

# Auto TOC creation rules

$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/ : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH) $(PATH_TEXTS)/auto-toc.usfm



# Make the content for a topical index from CSV data
# Not sure what the status on this call is. Does it
# even work yet?
make-topic-index :
	@$(PY_PROCESS_SCRIPTURE_TEXT) make_topic_index_file 'NA' $(PATH_SOURCE)$(PATH_SOURCE_PERIPH)/TOPICAL_INDEX.CSV $(PATH_TEXTS)/TOPICAL_INDEX.USFM
