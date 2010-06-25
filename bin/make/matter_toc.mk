# matter_toc.mk

# This file provides build rules for auto-building the toc on
# the content section of the NT or OT.

# History:

# 20080725 - djd - Initial draft version.


##############################################################
#		General rules for toc matter
##############################################################

# Go get the .$(EXT_TEX) file from the template lib if needed
$(PATH_PROCESS)/TOC.$(EXT_TEX) :
	@echo Copying into project from: $(PATH_TEMPLATES)/TOC.$(EXT_TEX)
	@cp $(PATH_TEMPLATES)/TOC.$(EXT_TEX) $@

# Make the .$(EXT_STYLE) override file for the TOC
$(PATH_PROCESS)/TOC.$(EXT_STYLE) :
	@if test -r $(PATH_TEMPLATES)/TOC.$(EXT_STYLE); then \
		echo Copying into project from: $(PATH_TEMPLATES)/TOC.$(EXT_STYLE); \
		cp $(PATH_TEMPLATES)/TOC.$(EXT_STYLE) '$@'; \
	else \
		echo Could not find: $@; \
		echo Creating this file:; \
		echo Caution, you will need to edit it; \
		echo \# Override PTX style sheet for $(PATH_TEXTS)/TOC.$(EXT_WORK), edit as needed >> $@; \
	fi


################################################################
#		Define the rules for OT TOC generation
################################################################

ifneq ($(MATTER_NT),)

# Create a simulated auto-toc-nt.$(EXT_WORK) if XeTeX has not done it
# already. For now we just bring in a dummy file from templates
$(PATH_PROCESS)/auto-toc-nt.$(EXT_WORK) : | $(MATTER_NT_PDF)

# Create the TOC-NT USFM file. This file must be created
# from the auto-toc-nt.$(EXT_WORK) file that comes from XeTeX
$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/TOC-NT.$(EXT_WORK) : | \
	$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH) \
	$(PATH_PROCESS)/TOC-NT.$(EXT_TEX) \
	$(PATH_PROCESS)/TOC.$(EXT_TEX) \
	$(PATH_PROCESS)/TOC.$(EXT_STYLE) \
	$(PATH_PROCESS)/FRONT_MATTER.$(EXT_TEX) \
	$(PATH_PROCESS)/auto-toc-nt.$(EXT_WORK)
	@echo Creating TOC from: $(PATH_TEXTS)/auto-toc-nt.$(EXT_WORK)
	@$(MOD_RUN_PROCESS) $(MOD_MK_TOC) 'TOC' '$(PATH_PROCESS)/auto-toc-nt.$(EXT_WORK)' '$@' ''

#	@cp $(PATH_PROCESS)/auto-toc-nt.$(EXT_WORK) $@

# Note: this is deprecated because it is handled in the matter_perripheral.mk
# in the $(PATH_TEXTS)/$(1) rule. I will leave it here for a while as a reminder
# Link the TOC-NT.$(EXT_WORK) to the Texts folder
#$(PATH_TEXTS)/TOC-NT.$(EXT_WORK) : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/TOC-NT.$(EXT_WORK)
#	@echo Linking project to peripheral source texts: $(shell readlink -f -- $@)
#	ln -sf $(shell readlink -f -- $<) $(PATH_TEXTS)/

# Creating the TOC-NT.$(EXT_TEX) file that links to the main TOC.$(EXT_TEX) file
# TOC.$(EXT_TEX) is also shared with TOC-OT.$(EXT_TEX).
$(PATH_PROCESS)/TOC-NT.$(EXT_TEX) :
	@echo Creating file: $@
	@echo \\input TOC.$(EXT_TEX) >> $@
	@echo \\ptxfile{$(PATH_TEXTS)/TOC-NT.$(EXT_WORK)} >> $@
	@echo '\\bye' >> $@

# Create the final TOC-NT PDF
$(PATH_PROCESS)/TOC-NT.$(EXT_PDF) : \
	$(PATH_TEXTS)/TOC-NT.$(EXT_WORK) \
	$(PATH_PROCESS)/TOC.$(EXT_TEX) \
	$(PATH_PROCESS)/TOC.$(EXT_STYLE) \
	$(DEPENDENT_FILE_LIST)
	@echo Starting TeX processing
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(PATH_PROCESS)/TOC-NT.$(EXT_TEX)

# Open the TOC-NT PDF file with reader
view-toc-nt : $(PATH_PROCESS)/TOC-NT.$(EXT_PDF)
	@echo Creating and viewing: $(PATH_PROCESS)/TOC-NT.$(EXT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

endif

################################################################
#		Define the rules for OT TOC generation
################################################################

ifneq ($(MATTER_OT),)
$(PATH_PROCESS)/auto-toc-ot.$(EXT_WORK) : $(MATTER_OT_PDF)

# Create the TOC-OT USFM file. This file must be created
# from the auto-toc-ot.$(EXT_WORK) file that comes from XeTeX
$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/TOC-OT.$(EXT_WORK) : | \
	$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH) \
	$(PATH_PROCESS)/TOC-OT.$(EXT_TEX) \
	$(PATH_PROCESS)/TOC.$(EXT_TEX) \
	$(PATH_PROCESS)/TOC.$(EXT_STYLE) \
	$(PATH_PROCESS)/FRONT_MATTER.$(EXT_TEX) \
	$(PATH_PROCESS)/auto-toc-ot.$(EXT_WORK)
	@echo Copying into project from: $(PATH_TEXTS)/auto-toc-ot.$(EXT_WORK)
	@cp $(PATH_PROCESS)/auto-toc-ot.$(EXT_WORK) $@

# Link the TOC-OT.$(EXT_WORK) to the Texts folder
$(PATH_TEXTS)/TOC-OT.$(EXT_WORK) : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/TOC-OT.$(EXT_WORK)
	@echo Linking project to peripheral source texts: $(shell readlink -f -- $@)
	ln -sf $(shell readlink -f -- $<) $(PATH_TEXTS)/

# Creating the TOC-NT.$(EXT_TEX) file that links to the main TOC.$(EXT_TEX) file
# TOC.$(EXT_TEX) is also shared with TOC-OT.$(EXT_TEX).
$(PATH_PROCESS)/TOC-OT.$(EXT_TEX) :
	@echo Creating file: $@
	@echo \\input TOC.$(EXT_TEX) >> $@
	@echo \\ptxfile{$(PATH_TEXTS)/TOC-OT.$(EXT_WORK)} >> $@
	@echo '\\bye' >> $@

# Create the final TOC-OT PDF
$(PATH_PROCESS)/TOC-OT.$(EXT_PDF) : \
	$(PATH_TEXTS)/TOC-OT.$(EXT_WORK) \
	$(PATH_PROCESS)/TOC.$(EXT_TEX) \
	$(PATH_PROCESS)/TOC.$(EXT_STYLE) \
	$(DEPENDENT_FILE_LIST)
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) $(TEX_ENGINE) $(PATH_PROCESS)/TOC-OT.$(EXT_TEX)

# Open the TOC-NT PDF file with reader
view-toc-ot : $(PATH_PROCESS)/TOC-OT.$(EXT_PDF)
	@echo Creating and viewing: $(PATH_PROCESS)/TOC-OT.$(EXT_PDF)
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

endif

##############################################################
#		General exicution rules for toc matter
##############################################################



