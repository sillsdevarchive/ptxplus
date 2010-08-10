# be_bible_info.mk

# This contians Bible information for a typesetting project based on.
# the default Bibledit behavior for file names.

# History
# 20080822 - djd - First version (non-working)
# 20081030 - djd - Added data, should work now.
# 20091211 - djd - Changed "book" to "component"


###################### Start Bible Definitions #########################


# Define default Bibledit file prefixes
# Note that spaces need to be escaped with "\"

# Old Testament
gen_component=1_Genesis
exo_component=2_Exodus
lev_component=3_Leviticus
num_component=4_Numbers
deu_component=5_Deuteronomy
jos_component=6_Joshua
jdg_component=7_Judges
rut_component=8_Ruth
1sa_component=9_1_Samuel
2sa_component=10_2_Samuel
1ki_component=11_1_Kings
2ki_component=12_2_Kings
1ch_component=13_1_Chronicles
2ch_component=14_2_Chronicles
ezr_component=15_Ezra
neh_component=16_Nehemiah
est_component=17_Esther
job_component=18_Job
psa_component=19_Psalms
pro_component=20_Proverbs
ecc_component=21_Ecclesiastes
sng_component=22_Song_of_Solomon
isa_component=23_Isaiah
jer_component=24_Jeremiah
lam_component=25_Lamentations
ezk_component=26_Ezekiel
dan_component=27_Daniel
hos_component=28_Hosea
jol_component=29_Joel
amo_component=30_Amos
oba_component=31_Obadiah
jon_component=32_Jonah
mic_component=33_Micah
nam_component=34_Nahum
hab_component=35_Habakkuk
zep_component=36_Zephaniah
hag_component=37_Haggai
zec_component=38_Zechariah
mal_component=39_Malachi

# New Testament
mat_component=40_Matthew
mrk_component=41_Mark
luk_component=42_Luke
jhn_component=43_John
act_component=44_Acts
rom_component=45_Romans
1co_component=46_1_Corinthians
2co_component=47_2_Corinthians
gal_component=48_Galatians
eph_component=49_Ephesians
php_component=50_Philippians
col_component=51_Colossians
1th_component=52_1_Thessalonians
2th_component=53_2_Thessalonians
1ti_component=54_1_Timothy
2ti_component=55_2_Timothy
tit_component=56_Titus
phm_component=57_Philemon
heb_component=58_Hebrews
jas_component=59_James
1pe_component=60_1_Peter
2pe_component=61_2_Peter
1jn_component=62_1_John
2jn_component=63_2_John
3jn_component=64_3_John
jud_component=65_Jude
rev_component=66_Revelation

# Deuterocanonical/Apocryphal components
tob_component=Tobit
jdt_component=Judith
esg_component=Esther
wis_component=Wisdom\ of\ Solomon
sir_component=Sirach
bar_component=Baruch
lje_component=Letter\ of\ Jeremiah
s3y_component=Song\ of\ the\ Three\ Children
sus_component=Susanna
bel_component=Bel\ and\ the\ Dragon
1ma_component=1\ Maccabees
2ma_component=2\ Maccabees
3ma_component=3\ Maccabees
4ma_component=4\ Maccabees
1es_component=1\ Esdras
2es_component=2\ Esdras
man_component=Prayer\ of\ Manasses
ps2_component=Psalms\ 151
oda_component=Odae
pss_component=Psalms\ of\ Solomon
jsa_component=Joshua\ A
jdb_component=Joshua\ B
tbs_component=Tobit\ S
sst_component=Susannah\ (Theodotion)
dnt_component=Daniel\ (Theodotion)
blt_component=Bel\ and\ the\ Dragon\ (Theodotion)
