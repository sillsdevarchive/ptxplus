# system_hyphenation.mk

# This file provides build rules for making the hypheation
# file and word lists.

# History:

# 20100301 - djd - Migrated rules from other files into this one
# 20100519 - djd - Fixed some file name problems


##############################################################
#		Rules for building hyphenation files
##############################################################

# Make a Hyphenation folder if necessary
$(PATH_HYPHENATION) :
	mkdir -p $(PATH_HYPHENATION)

# Manually create the TeX hyphenation file
make-tex-hyphens :
	$(PY_RUN_PROCESS) make_tex_hyphenation_file

# Create a TeX hyphenation rules file based on what is in the
# project.conf file
$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX) : | $(PATH_HYPHENATION)/$(FILE_HYPHENATION_TXT)
	$(PY_RUN_PROCESS) make_tex_hyphenation_file

# Manually create a master wordlist based on existing component
# wordlists in the Reports file. Best to run this after
# a preprocess-all command
make-master-wordlist : preprocess-checks
	@echo INFO: Creating a new master word list
	@$(PY_RUN_PROCESS) make_master_wordlist

#############################################################################
# Not sure what is happening here, lost track of what I was doing - djd

# There needs to be a review of he whole hyphenation list creation process
# (which really isn't right in the first place as we should be using
# hyphenation rules instead of an exclusion list). For now, we will just
# manually create a dummy file if none exists. A real file can be made
# with other commands in this section (I think)

# Manually create the hyphenation file if none exists but
# do not overwrite any existing ones. This is the file that
# is combined with the lccode.txt file to make the hyphenation.tex
# that the system ues.
$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TXT) :
	@echo INFO: Creating $@
	@touch $@

# Manually create the hyphenation word list file
force-make-hyphen-wordlist : $(PATH_HYPHENATION) make-master-wordlist
	@echo Creating a new hyphenation word list
	@$(PY_RUN_PROCESS) make_hyphen_wordlist

#############################################################################

# This enables all the preprocessing to be done in one command
preprocess: force-make-hyphen-wordlist
	@echo Completed preprocessing steps

.PHONY: preprocess make-hyphen-wordlist make-master-wordlist
