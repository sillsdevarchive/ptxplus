

convert png:<png file> -profile '<path to source image profile>' -profile <path to dest profile> -compress zip -units PixelsPerInch -define pdf:use-cropbox=true pdf:<output pdf path>

To have it rescale to a higher resolution (regardless of the input resolution) add
 -resample DPIxDPI
you can also limit the amount of memory used with -limit area <size>gb

e.g.
convert -limit memory 1.5gb map 4gb test.png -profile '/usr/share/color/icc/sRGB.icm' -profile /usr/share/color/icc/ISOcoated.icc -resample 2400x2400 -compress lzw -units PixelsPerInch -define pdf:use-cropbox=true test.pdf

limit the memory use does keep you machine responsive but for big workloads (e.g. anything 2400 DPI) it'll take a long time to complete


convert png:test.png -profile '/usr/share/color/icc/sRGB.icm' -profile /usr/share/color/icc/ISOcoated.icc -resample 600x600 -compress zip -units PixelsPerInch -define pdf:use-cropbox=true pdf:test.pdf
