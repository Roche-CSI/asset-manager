/** client side asset-db for offline and responsive performance */
export const DBConfig = { 
    name: 'AssetDB',
    version: 2, /* increment for any schema change */
    objectStoresMeta: [
        {
            store: 'signedURLs',
            storeConfig: {}, //key: asset_class + object_id
            storeSchema: [
                {name: 'contentType', keyPath: 'contentType', options: {unique: true}},
                {name: 'fileName', keyPath: 'fileName', options: {unique: true}},
                {name: 'objectData', keyPath: 'objectData', options: {unique: true}},
                {name: 'signedURL', keyPath: 'signedURL', options: {unique: true}}
            ]
        },
        {
            store: 'fileContents',
            storeConfig: {}, // key: content_id
            storeSchema: [
                {name: 'content', keyPath: 'content', options: {unique: true}},
                {name: 'timestamp', keyPath: 'timestamp', options: {unique: true}}
            ]
        },
        {
            store: 'favoriteClassName',
            storeConfig: {},
            storeSchema: [
            ]
        },
        {
            store: 'test',  //only for testing
            storeConfig: {},
            storeSchema: [
            ]
        },

    ]
} 