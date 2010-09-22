# peripheral.mk

# This file provides build rules for building all peripheral components,
# front and back, that might go into a Scripture publication. The
# rules will be laid out so that it will allow total flexibility as
# to if matter will be placed in the front or back. For example,
# it would be possible to put the copyright page in the back of the
# publication if necessary even though that is normally not done.
# Where components will be placed will be determined by the user
# as they layout the order in the Binding section of the project
# .conf file.

# History:

# 20100824 - djd - Initial draft version. Moved all the code from the
#		now deprecated matter_peripheral.mk


##############################################################
#		Variables for peripheral components
##############################################################

# Are there any?

##############################################################
#		General rules for all peripheral components
##############################################################

# Define the main macro rule group for what it takes to process
# peripheral components (front and back).

define periph_rules

# Peripheral material is unique to each project, as such, there only
# needs to be one copy to make maintainance simpler. With regular
# content text changes may be made to the working copy that are not
# made to the source. That is not the case with peripheral material.
# The source is the same as the working copy. The source is kept
# with in with the other source files so the translator has access
# to it. Checks and processes on peripheral material are currently
# done manually. This helps simplify the system and makes it more
# reliable.

# This rule simply links everything in the source peripheral folder
# to the project Texts folder
$(PATH_TEXTS)/$(1).$(EXT_WORK) : $(PATH_SOURCE_PERIPH)/$($(1)_peripheral).$(EXT_WORK)
	@echo INFO: Linking project to peripheral source texts: $$(shell readlink -f -- $$<)
	@ln -sf $$(shell readlink -f -- $$<) $$@

# Create the peripheral file by copying in the template. But if
# the template files doesn't exsit, then create a dummy one to
# serve as a placeholder. Note the line concatanation. This needs to
# be exicuted as one long line. Also be aware that we do not generate
# the TOC here as it is made by a seperate process.
# NOTE: the use of the "|" in the dependency list. The pipe enables makefile
# to check on the dependent target, in this case a directory, but
# the current target doesn't have to be rebuilt if it has not changed.
# This is very important here because a directory will always be
# changing.
$(PATH_SOURCE_PERIPH)/$($(1)_peripheral).$(EXT_WORK) : | $(PATH_SOURCE_PERIPH)
ifeq ($(PATH_SOURCE_PERIPH)/$($(1)_peripheral).$(EXT_WORK),$(PATH_SOURCE_PERIPH)/$(FILE_TOC_USFM))
	@echo Creating TOC from: $(PATH_TEXTS)/$(FILE_TOC_AUTO)
	@$(MOD_RUN_PROCESS) $(MOD_MAKE_TOC) 'TOC' '$(PATH_PROCESS)/$(FILE_TOC_AUTO)' '$$@' ''
else
	@echo INFO: Creating: $(PATH_SOURCE_PERIPH)/$($(1)_peripheral).$(EXT_WORK)
	$(call copysmart,$(PATH_RESOURCES_TEMPLATES)/$($(1)_peripheral).$(EXT_WORK),$$@)
endif

# This .tex file also generally has some dependencies on the
# COVER/FRONT/BACK_GROUP.tex files so we add them here. However,
# we will use the "|" (pipe) trick to prevent any updating in
# case the file already exists. As this is peripheral material
# we do not have an ID to pass along but we will set a special
# use flag which identifies the object as peripheral components.
# For this we use the "periph" flag.
$(PATH_PROCESS)/$(1).$(EXT_TEX) : | \
		$(PATH_PROCESS)/$(1).$(EXT_STYLE) \
		$(PATH_PROCESS)/$(FILE_TEX_COVER) \
		$(PATH_PROCESS)/$(FILE_TEX_FRONT) \
		$(PATH_PROCESS)/$(FILE_TEX_BACK)
	@echo INFO: Creating: $$@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "" "$(1)" "$$@" "periph"

# The rule to create the override style sheet.
$(PATH_PROCESS)/$(1).$(EXT_STYLE) :
	$(call copysmart,$(PATH_RESOURCES_TEMPLATES)/$($(1)_peripheral).$(EXT_STYLE),$$@)

# Process a single peripheral item and produce the final PDF.
$(PATH_PROCESS)/$(1).$(EXT_PDF) : \
		$(PATH_TEXTS)/$(1).$(EXT_WORK) \
		$(PATH_PROCESS)/$(1).$(EXT_TEX) \
		$(PATH_PROCESS)/$(1).$(EXT_STYLE) \
		$(DEPENDENT_FILE_LIST)
	@echo INFO: Creating: $$@
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(PATH_PROCESS)/$(1).$(EXT_TEX)
	$(call watermark,$$@)

# Open the PDF file with reader - Add a watermark if needed
view-$(1) : $(PATH_PROCESS)/$(1).$(EXT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $$< &

# This enables us to do the preprocessing on a single peripheral item.
preprocess-$(1) : $(PATH_SOURCE_PERIPH)/$($(1)_peripheral).$(EXT_WORK)
ifeq ($(LOCKED),0)
	@echo INFO: Preprocessing $($(1)_peripheral).$(EXT_WORK)
	@$(MOD_RUN_PROCESS) "preprocessChecks" "$($(1)_peripheral).$(EXT_WORK)" "$$<"
else
	echo INFO: Cannot run: $$@ This is because the project is locked.
endif

# Do not open the PDF file with reader
$(1) : $(PATH_PROCESS)/$(1).$(EXT_PDF) $(DEPENDENT_FILE_LIST)

# Remove the PDF file for this source file
pdf-remove-$(1) :
	@echo INFO: Removing $$@
	@rm -f $(PATH_PROCESS)/$(1).$(EXT_PDF)

# Benchmark test on the current component
benchmark-$(1) :
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "" ""

# Set the current file as benchmark. This will overwrite
# whatever might currently be in the benchmark folder.
benchmark-set-$(1) :
	@$(MOD_RUN_PROCESS) "$(MOD_BENCHMARK)" "$(1)" "$(PATH_TEXTS)/$(1).$(EXT_WORK)" "" "set"

# End to the periph_rules macro def
endef


###################################################################################################

# Filter out repeat instances of peripheral components, like
# blank pages which need to be listed multiple times
define uniq
$(if $(1),$(firstword $(1)) $(call uniq,$(filter-out $(firstword $(1)),$(1))),)
endef

# Bind all the components into a group PDF file
define group_binding

ifneq ($($(1)),)
$(1)_PDF = $(PATH_PROCESS)/$(1).$(EXT_PDF)
$(PATH_PROCESS)/$(1).$(EXT_PDF) : | $(foreach v,$($(1)),$(PATH_PROCESS)/$(v).$(EXT_PDF)) $(DEPENDENT_FILE_LIST)
	@echo INFO: Creating: $(1).$(EXT_PDF) [Components: $($(1))]
	@pdftk $(foreach v,$($(1)),$(v:%=$(PATH_PROCESS)/%.$(EXT_PDF))) cat output $$@
endif

endef


##############################################################
#		Main processing rules
##############################################################

# This builds a rule (in memory) for these sets of files

# This calls all the automated rules defined above and does them
# once on each component, even if the component is listed repeatedly
# in the Binding list. This is what the uniq call is for.
$(foreach v,$(call uniq,$(GROUP_COVER) $(GROUP_FRONT) $(GROUP_BACK)),$(eval $(call periph_rules,$(v))))

# Cover group binding rules
$(PATH_PROCESS)/$(GROUP_COVER).$(EXT_PDF) :
$(eval $(call group_binding,GROUP_COVER))

# Front group binding rules
$(PATH_PROCESS)/$(GROUP_FRONT).$(EXT_PDF) :
$(eval $(call group_binding,GROUP_FRONT))

# Back group binding rules
$(PATH_PROCESS)/$(GROUP_BACK).$(EXT_PDF) :
$(eval $(call group_binding,GROUP_BACK))

# This makes a simple TeX settings file for the cover. This may
# not really be needed but it seems to be the best way to handle
# this proceedure and remain consistant with the rest of the
# processes.
$(PATH_PROCESS)/$(FILE_TEX_COVER) : $(PATH_PROCESS)/$(FILE_TEX_SETTINGS)
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "" "" "$@" "cover"

# Most front group peripheral .tex files will have a dependency
# on $(FILE_TEX_FRONT) even if it doesn't, there is a hard coded
# dependency here that will be met if called on.
$(PATH_PROCESS)/$(FILE_TEX_FRONT) : $(PATH_PROCESS)/$(FILE_TEX_SETTINGS)
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "" "" "$@" "front"

# Most back group peripheral .tex files will have a dependency
# on BACK_GROUP.tex even if it doesn't there is a hard coded
# dependency here that will be met if called on.
$(PATH_PROCESS)/$(FILE_TEX_BACK) : $(PATH_PROCESS)/$(FILE_TEX_SETTINGS)
	@echo INFO: Creating: $@
	@$(MOD_RUN_PROCESS) "$(MOD_MAKE_TEX)" "" "" "$@" "back"

# Produce all the outer cover material in one PDF file
view-cover : $(PATH_PROCESS)/GROUP_COVER.$(EXT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

# To produce individual elements of the outer cover just
# use: ptxplus view-<file_name>

# Produce just the font group (bound)
view-front : $(PATH_PROCESS)/GROUP_FRONT.$(EXT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

# Produce just the back group (bound)
view-back : $(PATH_PROCESS)/GROUP_BACK.$(EXT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

# Clean up rules for peripheral groups

# Remove the cover group PDF file
pdf-remove-cover :
	@echo INFO: Removing: $(GROUP_COVER_PDF)
	@rm -f $(GROUP_COVER_PDF)

# Remove the front group PDF file
pdf-remove-front :
	@echo INFO: Removing: $(GROUP_FRONT_PDF)
	@rm -f $(GROUP_FRONT_PDF)

# Remove the back group PDF file
pdf-remove-back :
	@echo INFO: Removing: $(GROUP_BACK_PDF)
	@rm -f $(GROUP_BACK_PDF)



# Make the content for a topical index from CSV data
# Not sure what the status on this call is. Does it
# even work yet?
make-topic-index :
	@$(MOD_RUN_PROCESS) "make_topic_index_file" "NA" "$(PATH_SOURCE_PERIPH)/TOPICAL_INDEX.CSV" "$(PATH_TEXTS)/TOPICAL_INDEX.USFM"
