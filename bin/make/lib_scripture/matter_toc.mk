# matter_toc.mk

# This file provides build rules for auto-building the toc on
# the content section of the NT or OT.

# History:

# 20080725 - djd - Initial draft version.


##############################################################
#		General rules for toc matter
##############################################################

# Go get the .$(EXT_TEX) file from the template lib if needed
$(PATH_PROCESS)/$(FILE_TOC_TEX) :
	@echo Copying into project from: $(PATH_TEMPLATES)/$(FILE_TOC_TEX)
	@cp $(PATH_TEMPLATES)/$(FILE_TOC_TEX) $@

# Make the .$(EXT_STYLE) override file for the TOC
$(PATH_PROCESS)/$(FILE_TOC_STYLE) :
	@if test -r $(PATH_TEMPLATES)/$(FILE_TOC_STYLE); then \
		echo Copying into project from: $(PATH_TEMPLATES)/$(FILE_TOC_STYLE); \
		cp $(PATH_TEMPLATES)/$(FILE_TOC_STYLE) '$@'; \
	else \
		echo Could not find: $@; \
		echo Creating this file:; \
		echo Caution, you will need to edit it; \
		echo \# Override PTX style sheet for $(PATH_TEXTS)/$(FILE_TOC_USFM), edit as needed >> $@; \
	fi


################################################################
#		Define the rules for OT TOC generation
################################################################

ifneq ($(MATTER_NT),)

# Create a simulated auto-toc-nt.$(EXT_WORK) if XeTeX has not done it
# already. For now we just bring in a dummy file from templates
$(PATH_PROCESS)/$(FILE_TOC_AUTO) : | $(MATTER_NT_PDF)

$(PATH_TEXTS)/$(FILE_TOC_USFM) : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/$(FILE_TOC_USFM)
	@echo INFO: Linking project to peripheral source texts: $$(shell readlink -f -- $$<)
	@ln -sf $$(shell readlink -f -- $$<) $(PATH_TEXTS)/

# Create the TOC-NT USFM file. This file must be created
# from the auto-toc-nt.$(EXT_WORK) file that comes from XeTeX
#$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/$(FILE_TOC_USFM) : | \
#	$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH) \
#	$(PATH_PROCESS)/$(FILE_TOC_AUTO)
#	@echo Creating TOC from: $(PATH_TEXTS)/$(FILE_TOC_AUTO)
#	@$(MOD_RUN_PROCESS) $(MOD_MAKE_TOC) 'TOC' '$(PATH_PROCESS)/$(FILE_TOC_AUTO)' '$@' ''

# Create the final TOC PDF file
$(PATH_PROCESS)/$(FILE_TOC_PDF) : \
	$(PATH_TEXTS)/$(FILE_TOC_USFM) \
	$(PATH_PROCESS)/$(FILE_TOC_TEX) \
	$(PATH_PROCESS)/$(FILE_TOC_STYLE) \
	$(PATH_PROCESS)/$(FILE_TEX_FRONT) \
	$(DEPENDENT_FILE_LIST)
	@echo Starting TeX processing
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(PATH_PROCESS)/$(FILE_TOC_TEX)

# Open the TOC-NT PDF file with reader
view-toc : $(PATH_PROCESS)/$(FILE_TOC_PDF)
	@echo Creating and viewing: $(PATH_PROCESS)/$(FILE_TOC_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

endif


