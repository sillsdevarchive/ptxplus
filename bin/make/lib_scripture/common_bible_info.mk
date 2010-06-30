# be_bible_info.mk

# This contians common Bible information for a typesetting project.

# History
# 20080822 - djd - First working version
# 20091211 - djd - Samantic change from book to component


###################### Start Bible Definitions #########################

# Define OT books (39)
OT_COMPONENTS=gen exo lev num deu jos jdg rut 1sa 2sa 1ki 2ki 1ch 2ch ezr neh \
est job psa pro ecc sng isa jer lam ezk dan hos jol amo oba jon mic nam hab \
zep hag zec mal

# Define NT books (27)
NT_COMPONENTS=mat mrk luk jhn act rom 1co 2co gal eph php col 1th 2th 1ti 2ti \
tit phm heb jas 1pe 2pe 1jn 2jn 3jn jud rev

# Define Deuterocanonical/Apocryphal (26)
AP_COMPONENTS=tob jdt esg wis sir bar lje s3y sus bel 1ma 2ma 3ma 4ma 1es 2es man \
ps2 oda pss jsa jdb tbs sst dnt blt


# Define all Bible component groups (books). Note these are used mainly
# in the COMPONENTS_TO_PROCESS
# variable in the project.conf file
BIBLE_COMPONENTS_ALL=OT_COMPONENTS NT_COMPONENTS AP_COMPONENTS
BIBLE_COMPONENTS_CANON=OT_COMPONENTS NT_COMPONENTS



####################### Some Misc. Info ##########################
# This is not in use right now but could be some day

# Deuterocanonical/Apocryphal component codes
# TOB = Tobith
# JDT = Judith
# ESG = Esther (Greek)
# WIS = Wisdom of Solomon
# SIR = Ecclesiasticus
# BAR = Baruch
# LJE = Letter of Jeremiah
# S3Y = Song of the Three Young Men
# SUS = Susannah
# BEL = Bel and the Dragon
# 1MA = 1 Maccabees
# 2MA = 2 Maccabees
# 3MA = 3 Maccabees
# 4MA = 4 Maccabees
# 1ES = 1 Esdras
# 2ES = 2 Esdras
# MAN = Prayer of Manasseh
# PS2 = Psalm 151
# ODA = Odae
# PSS = Psalms of Solomon
# JSA = Joshua A.
# JDB = Judges B
# TBS = Tobit S.
# SST = Susannah (Theodotion)
# DNT = Daniel (Theodotion)
# BLT = Bel and the Dragon (Theodotion)
