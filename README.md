Generates files for EUV (Europa Universalis V) map modding from an input PNG file.

The Input PNG file should contain single pixel wide black borders for locations.

A single red (255,0,0) pixel within a location defines it as a wasteland
A single green (0,255,0)  pixel within a location defines it as a harbour
A single blue (0,0,255)  pixel within a location defines it as an ocean

Files that are generate from this information include:
00_default.txt
06_pops.txt
08_institutions.txt
default.map
definitions.txt
location_templates.txt
locations.png
