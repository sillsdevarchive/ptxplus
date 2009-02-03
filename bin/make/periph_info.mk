# ptx_bible_info.mk

# This contains information for working with peripheral matter
# in a typesetting project. These are definitions that are more
# ptxplus specific.

# History
# 20080819 - djd - First working version


###################### Start Definitions #########################

ALL_PERIPH=blank concordance copyright cover forward glossary index intro preface publisher title title_nt title_ot toc


# These are peripheral matter that goes with the books, not in the
# front or back matter. However, the need to be handled like peripheral
# matter. They will be added to the book matter during binding.
title_nt_periph		= TITLE_NT
title_ot_periph		= TITLE_OT

# These are extra periferal texts that may need to be processed.
# However, these are not USFM (PTX) compatable.
blank_periph		= BLANK
concordance_periph	= CONCORDANCE
copyright_periph	= COPYRIGHT
cover_periph		= COVER
forward_periph		= FORWARD
glossary_periph		= GLOSSARY
index_periph		= INDEX
intro_periph		= INTRO
preface_periph		= PREFACE
publisher_periph	= PUBLISHER
title_periph		= TITLE
toc_periph		= TOC
