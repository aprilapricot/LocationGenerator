## Generates files for EUV (Europa Universalis V) map modding from an input PNG file.
Input:
![input](https://github.com/aprilapricot/LocationGenerator/blob/main/files_examples/spiderweb10.png "Input")
Output:
![output](https://github.com/aprilapricot/LocationGenerator/blob/main/files_examples/locations.png "Locations")

- Small gaps will be closed automatically
- Any area under 100px will be merged into nearby locations, this is usually the result of artifacts or poor linework on the "spiderweb"
    - EUV will crash if a location under 100px is defined
- Locations have a max area size that will cause EUV to launch forever, please segment large background areas if they exist

### The Input PNG file should contain single pixel wide black borders for locations.
- A single red (255,0,0) pixel within a location defines it as a wasteland
- A single green (0,255,0)  pixel within a location defines it as a harbour
- A single blue (0,0,255)  pixel within a location defines it as an ocean


### Files that are generate from this information include:
- 00_default.txt
- 06_pops.txt
- 08_institutions.txt
- default.map
- definitions.txt
- location_templates.txt
- locations.png
