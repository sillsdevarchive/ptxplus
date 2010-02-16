# matter_toc.mk

# This file provides build rules for auto-building the toc on
# the content section of the NT or OT.

# History:

# 20080725 - djd - Initial draft version.


##############################################################
#		General rules for toc matter
##############################################################

# Go get the .tex file from the template lib if needed
$(PATH_PROCESS)/TOC.tex :
	@echo Copying into project from: $(PATH_TEMPLATES)/TOC.tex
	@cp $(PATH_TEMPLATES)/TOC.TEX $@

# Make the .sty override file for the TOC
$(PATH_PROCESS)/TOC.sty :
	@if test -r $(PATH_TEMPLATES)/TOC.STY; then \
		echo Copying into project from: $(PATH_TEMPLATES)/TOC.STY; \
		cp $(PATH_TEMPLATES)/TOC.STY '$@'; \
	else \
		echo Could not find: $@; \
		echo Creating this file:; \
		echo Caution, you will need to edit it; \
		echo \# Override PTX style sheet for $(PATH_TEXTS)/TOC.USFM, edit as needed >> $@; \
	fi


################################################################
#		Define the rules for OT TOC generation
################################################################

ifneq ($(MATTER_NT),)

# Create a simulated auto-toc-nt.usfm if XeTeX has not done it
# already. For now we just bring in a dummy file from templates
$(PATH_PROCESS)/auto-toc-nt.usfm : $(MATTER_NT_PDF)

# Create the TOC-NT USFM file. This file must be created
# from the auto-toc-nt.usfm file that comes from XeTeX
$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/TOC-NT.usfm : | \
	$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH) \
	$(PATH_PROCESS)/TOC-NT.tex \
	$(PATH_PROCESS)/TOC.tex \
	$(PATH_PROCESS)/TOC.sty \
	$(PATH_PROCESS)/FRONT_MATTER.tex \
	$(PATH_PROCESS)/auto-toc-nt.usfm
	@echo Copying into project from: $(PATH_TEXTS)/auto-toc-nt.usfm
	@cp $(PATH_PROCESS)/auto-toc-nt.usfm $@

# Link the TOC-NT.usfm to the Texts folder
$(PATH_TEXTS)/TOC-NT.usfm : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/TOC-NT.usfm
	@echo Linking project to peripheral source texts: $(shell readlink -f -- $@)
	ln -sf $(shell readlink -f -- $<) $(PATH_TEXTS)/

# Creating the TOC-NT.tex file that links to the main TOC.tex file
# TOC.tex is also shared with TOC-OT.tex.
$(PATH_PROCESS)/TOC-NT.tex :
	@echo Creating file: $@
	@echo \\input TOC.tex >> $@
	@echo \\ptxfile{$(PATH_TEXTS)/TOC-NT.usfm} >> $@
	@echo '\\bye' >> $@

# Create the final TOC-NT PDF
$(PATH_PROCESS)/TOC-NT.pdf : \
	$(PATH_TEXTS)/TOC-NT.usfm \
	$(PATH_PROCESS)/TOC.tex \
	$(PATH_PROCESS)/TOC.sty \
	$(DEPENDENT_FILE_LIST)
	@echo Starting TeX processing
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(PATH_PROCESS)/TOC-NT.tex

# Open the TOC-NT PDF file with reader
view-toc-nt : $(PATH_PROCESS)/TOC-NT.pdf
	@echo Creating and viewing: $(PATH_PROCESS)/TOC-NT.pdf
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

endif

################################################################
#		Define the rules for OT TOC generation
################################################################

ifneq ($(MATTER_OT),)
$(PATH_PROCESS)/auto-toc-ot.usfm : $(MATTER_OT_PDF)

# Create the TOC-OT USFM file. This file must be created
# from the auto-toc-ot.usfm file that comes from XeTeX
$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/TOC-OT.usfm : | \
	$(PATH_SOURCE)/$(PATH_SOURCE_PERIPH) \
	$(PATH_PROCESS)/TOC-OT.tex \
	$(PATH_PROCESS)/TOC.tex \
	$(PATH_PROCESS)/TOC.sty \
	$(PATH_PROCESS)/FRONT_MATTER.tex \
	$(PATH_PROCESS)/auto-toc-ot.usfm
	@echo Copying into project from: $(PATH_TEXTS)/auto-toc-ot.usfm
	@cp $(PATH_PROCESS)/auto-toc-ot.usfm $@

# Link the TOC-OT.usfm to the Texts folder
$(PATH_TEXTS)/TOC-OT.usfm : $(PATH_SOURCE)/$(PATH_SOURCE_PERIPH)/TOC-OT.usfm
	@echo Linking project to peripheral source texts: $(shell readlink -f -- $@)
	ln -sf $(shell readlink -f -- $<) $(PATH_TEXTS)/

# Creating the TOC-NT.tex file that links to the main TOC.tex file
# TOC.tex is also shared with TOC-OT.tex.
$(PATH_PROCESS)/TOC-OT.tex :
	@echo Creating file: $@
	@echo \\input TOC.tex >> $@
	@echo \\ptxfile{$(PATH_TEXTS)/TOC-OT.usfm} >> $@
	@echo '\\bye' >> $@

# Create the final TOC-OT PDF
$(PATH_PROCESS)/TOC-OT.pdf : \
	$(PATH_TEXTS)/TOC-OT.usfm \
	$(PATH_PROCESS)/TOC.tex \
	$(PATH_PROCESS)/TOC.sty \
	$(DEPENDENT_FILE_LIST)
	@cd $(PATH_PROCESS) && $(TEX_INPUTS) xetex $(PATH_PROCESS)/TOC-OT.tex

# Open the TOC-NT PDF file with reader
view-toc-ot : $(PATH_PROCESS)/TOC-OT.pdf
	@echo Creating and viewing: $(PATH_PROCESS)/TOC-OT.pdf
	@- $(CLOSEPDF)
	@ $(VIEWPDF) $< &

endif

##############################################################
#		General exicution rules for toc matter
##############################################################



define test-def
# Just process the TOC this rule will be called from
# the process NT or OT
process-toc : $(PATH_PROCESS)/TOC.pdf
	@echo Creating the TOC file now (but it will not view)

endef
