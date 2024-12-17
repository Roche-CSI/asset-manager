## Adding references to an asset

You can add existing assets as a reference before committing a created asset. A typical flow would be

```asset init <class_name```: creates asset
```asset add refs --type input --asset <name>```

It's important to note that references are allowed only between root nodes.