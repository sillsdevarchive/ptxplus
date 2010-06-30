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
# 20080725 - djd - Added more periferal IDs, changed _base to _component
# 20080819 - djd - Added some component periferal material IDs and then
#		split out the peripheral material section into its
#		own file to help with multiple editor support
# 20080822 - djd - Removed common Bible info to seperate file
# 20091211 - djd - Changed "component" to "component"


###################### Start Bible Definitions #########################

# Define default PTX file prefixes
# Old Testament
gen_component=01GEN
exo_component=02EXO
lev_component=03LEV
num_component=04NUM
deu_component=05DEU
jos_component=06JOS
jdg_component=07JDG
rut_component=08RUT
1sa_component=091SA
2sa_component=102SA
1ki_component=111KI
2ki_component=122KI
1ch_component=131CH
2ch_component=142CH
ezr_component=15EZR
neh_component=16NEH
est_component=17EST
job_component=18JOB
psa_component=19PSA
pro_component=20PRO
ecc_component=21ECC
sng_component=22SNG
isa_component=23ISA
jer_component=24JER
lam_component=25LAM
ezk_component=26EZK
dan_component=27DAN
hos_component=28HOS
jol_component=29JOL
amo_component=30AMO
oba_component=31OBA
jon_component=32JON
mic_component=33MIC
nam_component=34NAM
hab_component=35HAB
zep_component=36ZEP
hag_component=37HAG
zec_component=38ZEC
mal_component=39MAL
# New Testament (Note 40 has been skipped, this seems to be normal PTX behavior)
mat_component=41MAT
mrk_component=42MRK
luk_component=43LUK
jhn_component=44JHN
act_component=45ACT
rom_component=46ROM
1co_component=471CO
2co_component=482CO
gal_component=49GAL
eph_component=50EPH
php_component=51PHP
col_component=52COL
1th_component=531TH
2th_component=542TH
1ti_component=551TI
2ti_component=562TI
tit_component=57TIT
phm_component=58PHM
heb_component=59HEB
jas_component=60JAS
1pe_component=611PE
2pe_component=622PE
1jn_component=631JN
2jn_component=642JN
3jn_component=653JN
jud_component=66JUD
rev_component=67REV
# Deuterocanonical/Apocryphal components
tob_component=68TOB
jdt_component=69JDT
esg_component=70ESG
wis_component=71WIS
sir_component=72SIR
bar_component=73BAR
lje_component=74LJE
s3y_component=75S3Y
sus_component=76SUS
bel_component=77BEL
1ma_component=781MA
2ma_component=792MA
3ma_component=803MA
4ma_component=814MA
1es_component=821ES
2es_component=832ES
man_component=84MAN
ps2_component=85PS2
oda_component=86ODA
pss_component=87PSS
jsa_component=88JSA
jdb_component=89JDB
tbs_component=90TBS
sst_component=91SST
dnt_component=92DNT
blt_component=93BLT
# PTX will output more than these but documentation has not been found yet.
