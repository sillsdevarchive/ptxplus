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
	$(call mdir,$(PATH_HYPHENATION))

# Manually create the TeX hyphenation file
make-tex-hyphens : | $(PATH_HYPHENATION)/$(FILE_HYPHENATION_TXT)
	@echo INFO: Creating new file: $(FILE_HYPHENATION_TEX)
	@$(MOD_RUN_PROCESS) make_tex_hyphenation_file

# Overwrite the TeX hyphenation file
overwrite-tex-hyphens : | $(PATH_HYPHENATION)/$(FILE_HYPHENATION_TXT)
	@echo INFO: Overwriting: $(FILE_HYPHENATION_TEX)
	@$(MOD_RUN_PROCESS) make_tex_hyphenation_file "" "" "" "overwrite"
	@$(EDITSFM) $(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX) &

# Create a TeX hyphenation rules file based on what is in the
# project.conf file
$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TEX) : make-tex-hyphens

# Manually create the hyphenation word file if none exists but
# do not overwrite any existing ones. This is the file that
# is combined with the lccode.txt file to make the hyphenation.tex
# that the system ues.
$(PATH_HYPHENATION)/$(FILE_HYPHENATION_TXT) : make-master-wordlist
	@echo INFO: Creating a new hyphenation word list
	@$(MOD_RUN_PROCESS) make_hyphen_wordlist
	@$(EDITSFM) $@ &

# Rule name for the creating the hypheation file
make-hyphen-wordlist: $(PATH_HYPHENATION)/$(FILE_HYPHENATION_TXT)

# Manually create a master wordlist based on existing component
# wordlists in the Reports file. Best to run this after
# a preprocess-all command
make-master-wordlist : preprocess-content
	@echo INFO: Creating a new master word list
	@$(MOD_RUN_PROCESS) make_master_wordlist
	@$(EDITCSV) $(FILE_MASTERWORDS) &

.PHONY: preprocess make-hyphen-wordlist make-master-wordlist
