# ptx_bible_info.mk

# This contians Bible information for a typesetting project based on.
# the default Paratext behavior for file names.

# History
# 20080305 - djd - First working version
# 20080404 - djd - Corrected numbering error
# 20080407 - djd - Expanded to include OT references
# 20080425 - djd - Reverted to previous numbering system which
#			is used by PTX. #40 does not exsist in PTX
#			Also added Deuterocanonical/Apocryphal info.
# 20080611 - djd - Add concordance and toc IDs
# 20080725 - djd - Added more periferal IDs, changed _base to _book
# 20080819 - djd - Added some book periferal material IDs and then
#		split out the peripheral material section into its
#		own file to help with multiple editor support
# 20080822 - djd - Removed common Bible info to seperate file

###################### Start Bible Definitions #########################

# Define default PTX file prefixes
# Old Testament
gen_book=01GEN
exo_book=02EXO
lev_book=03LEV
num_book=04NUM
deu_book=05DEU
jos_book=06JOS
jdg_book=07JDG
rut_book=08RUT
1sa_book=091SA
2sa_book=102SA
1ki_book=111KI
2ki_book=122KI
1ch_book=131CH
2ch_book=142CH
ezr_book=15EZR
neh_book=16NEH
est_book=17EST
job_book=18JOB
psa_book=19PSA
pro_book=20PRO
ecc_book=21ECC
sng_book=22SNG
isa_book=23ISA
jer_book=24JER
lam_book=25LAM
ezk_book=26EZK
dan_book=27DAN
hos_book=28HOS
jol_book=29JOL
amo_book=30AMO
oba_book=31OBA
jon_book=32JON
mic_book=33MIC
nam_book=34NAM
hab_book=35HAB
zep_book=36ZEP
hag_book=37HAG
zec_book=38ZEC
mal_book=39MAL
# New Testament (Note 40 has been skipped, this seems to be normal PTX behavior)
mat_book=41MAT
mrk_book=42MRK
luk_book=43LUK
jhn_book=44JHN
act_book=45ACT
rom_book=46ROM
1co_book=471CO
2co_book=482CO
gal_book=49GAL
eph_book=50EPH
php_book=51PHP
col_book=52COL
1th_book=531TH
2th_book=542TH
1ti_book=551TI
2ti_book=562TI
tit_book=57TIT
phm_book=58PHM
heb_book=59HEB
jas_book=60JAS
1pe_book=611PE
2pe_book=622PE
1jn_book=631JN
2jn_book=642JN
3jn_book=653JN
jud_book=66JUD
rev_book=67REV
# Deuterocanonical/Apocryphal books
tob_book=68TOB
jdt_book=69JDT
esg_book=70ESG
wis_book=71WIS
sir_book=72SIR
bar_book=73BAR
lje_book=74LJE
s3y_book=75S3Y
sus_book=76SUS
bel_book=77BEL
1ma_book=781MA
2ma_book=792MA
3ma_book=803MA
4ma_book=814MA
1es_book=821ES
2es_book=832ES
man_book=84MAN
ps2_book=85PS2
oda_book=86ODA
pss_book=87PSS
jsa_book=88JSA
jdb_book=89JDB
tbs_book=90TBS
sst_book=91SST
dnt_book=92DNT
blt_book=93BLT
# PTX will output more than these but documentation has not been found yet.
