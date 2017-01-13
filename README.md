# Site Mapper

## SiteMap Data
[xml, csv and json output](https://openciti.ca/data)

## json viewers

### [Firefox](https://www.google.ca/url?sa=t&rct=j&q=&esrc=s&source=web&cd=1&cad=rja&uact=8&ved=0ahUKEwjk6oHC07PRAhVG4oMKHRDdBOoQFggcMAA&url=https%3A%2F%2Faddons.mozilla.org%2Fen-us%2Ffirefox%2Faddon%2Fjsonview%2F&usg=AFQjCNFnutZMnUPkykePxkREckXfDY1Xtg&sig2=xaRijwrrCdniT0tM5U9jBg)

### [Chrome](https://chrome.google.com/webstore/detail/json-viewer/gbmdgpbipfallnflgajpaliibnhdgobh)

## Usage


### Generate xml, csv and json from a url

`python3 sitemapper.py www.domain.gov`

since the above command may take too long to terminate, you can stop the script and proceed with the xml file that has been generated as illustrated below

### Generate csv and json from an xml source
`python3 pathtoxmlfile/file.xml -- csv`

### Generate json from a csv source
`python3 pathtocsvfile/file.csv -- json`

## Fork python-sitemap

The web crawler was forked from https://github.com/c4software/python-sitemap

Before the fork was made, a pull request to add GPL 3.0 was accepeted by c4software

----

# Licence

[GPL 3.0](http://www.gnu.org/licenses/gpl.txt)
