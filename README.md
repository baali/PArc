### Introduction

Create a WARC file for any URL. It will fetch static resources, images, CSS, javascript files and add all of them to single WARC file. It can be used with [wayback machine](https://hrbrmstr.github.io/wayback/index.html).

### Steps to create and add WARC to wayback archives:

    python create_warc.py URL WARC-Filename
    # This would create WARC-Filename.warc.gz that could be added to wayback archives
    wb-manager add Name-of-Archive-Records WARC-Filename.warc.gz
    # Now archived URL can be accessed on locally running wayback machine.
