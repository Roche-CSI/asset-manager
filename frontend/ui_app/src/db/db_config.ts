/** client side asset-db for offline and responsive performance */
export const DBConfig = {
    name: 'AssetDB',
    version: 1, /* increment for any schema change */
    objectStoresMeta: [
        {
            store: 'asset_class',
            storeConfig: {keyPath: 'name', autoIncrement: false},
            storeSchema: [
                {name: 'id', keyPath: 'id', options: {unique: true}},
                {name: 'name', keyPath: 'name', options: {unique: true}},
                {name: 'owner', keyPath: 'owner', options: {unique: false}},
                {name: 'created_by', keyPath: 'created_by', options: {unique: false}},
                {name: 'created_at', keyPath: 'created_at', options: {unique: false}},
                {name: 'modified_by', keyPath: 'modified_by', options: {unique: false}},
                {name: 'modified_at', keyPath: 'modified_at', options: {unique: false}},
                {tags: 'tags', keyPath: 'tags', options: {unique: false}},
            ]
        },
        {
            store: 'asset',
            storeConfig: {keyPath: 'name', autoIncrement: false},
            storeSchema: [
                {name: 'id', keyPath: 'id', options: {unique: true}},
                {name: 'name', keyPath: 'name', options: {unique: true}},
                {name: 'asset_class', keyPath: 'asset_class', options: {unique: false}},
                {name: 'seq_id', keyPath: 'seq_id', options: {unique: false}},
                {name: 'owner', keyPath: 'owner', options: {unique: false}},
                {name: 'top_hash', keyPath: 'top_hash', options: {unique: false}},
                {name: 'refs', keyPath: 'refs', options: {unique: false}},
                {name: 'alias', keyPath: 'alias', options: {unique: false}},
                {name: 'created_by', keyPath: 'created_by', options: {unique: false}},
                {name: 'created_at', keyPath: 'created_at', options: {unique: false}},
                {name: 'modified_by', keyPath: 'modified_by', options: {unique: false}},
                {name: 'modified_at', keyPath: 'modified_at', options: {unique: false}},
                {name: 'tags', keyPath: 'tags', options: {unique: false}},
            ]
        },
        {
            store: 'version',
            storeConfig: {keyPath: 'id', autoIncrement: false},
            storeSchema: [
                {name: 'id', keyPath: 'id', options: {unique: true}},
                {name: 'asset', keyPath: 'asset', options: {unique: false}},
                {name: 'number', keyPath: 'number', options: {unique: false}},
                {name: 'patch', keyPath: 'patch', options: {unique: false}},
                {name: 'parent', keyPath: 'parent', options: {unique: false}},
                {name: 'commit_hash', keyPath: 'commit_hash', options: {unique: false}},
                {name: 'commit_message', keyPath: 'commit_message', options: {unique: false}},
                {name: 'created_by', keyPath: 'created_by', options: {unique: false}},
                {name: 'created_at', keyPath: 'created_at', options: {unique: false}},
            ]
        },
        {
            store: 'version_counter',
            storeConfig: {keyPath: 'id', autoIncrement: false},
            storeSchema: [
                {name: 'id', keyPath: 'id', options: {unique: true}},
                {name: 'asset', keyPath: 'asset', options: {unique: false}},
                {name: 'counter', keyPath: 'counter', options: {unique: false}},
                {name: 'leaf_version', keyPath: 'leaf_version', options: {unique: false}},
                {name: 'leaf_objects', keyPath: 'leaf_objects', options: {unique: false}},
                {name: 'created_by', keyPath: 'created_by', options: {unique: false}},
                {name: 'created_at', keyPath: 'created_at', options: {unique: false}},
                {name: 'modified_by', keyPath: 'modified_by', options: {unique: false}},
                {name: 'modified_at', keyPath: 'modified_at', options: {unique: false}},
            ]
        },
        {
            store: 'object',
            storeConfig: {keyPath: 'id', autoIncrement: false},
            storeSchema: [
                {name: 'id', keyPath: 'id', options: {unique: true}},
                {name: 'content', keyPath: 'content', options: {unique: false}},
                {name: 'meta', keyPath: 'meta', options: {unique: false}},
                {name: 'created_by', keyPath: 'created_by', options: {unique: false}},
                {name: 'created_at', keyPath: 'created_at', options: {unique: false}},
            ]
        },
        {
            store: 'content',
            storeConfig: {keyPath: 'id', autoIncrement: false},
            storeSchema: [
                {name: 'id', keyPath: 'id', options: {unique: true}},
                {name: 'mime_type', keyPath: 'mime_type', options: {unique: false}},
                {name: 'size', keyPath: 'size', options: {unique: false}},
                {name: 'meta', keyPath: 'meta', options: {unique: false}},
                {name: 'created_by', keyPath: 'created_by', options: {unique: false}},
                {name: 'created_at', keyPath: 'created_at', options: {unique: false}},
            ]
        },
        {
            store: 'asset_object_relations',
            storeConfig: {keyPath: ['asset', 'object'], autoIncrement: false},
            storeSchema: [
                {name: 'asset', keyPath: 'asset', options: {unique: false}},
                {name: 'object', keyPath: 'object', options: {unique: false}}
            ]
        },
        {
            store: 'asset_class_content_relations',
            storeConfig: {keyPath: ['asset_class', 'content'], autoIncrement: false},
            storeSchema: [
                {name: 'asset_class', keyPath: 'asset_class', options: {unique: false}},
                {name: 'content', keyPath: 'content', options: {unique: false}}
            ]
        }
    ]
}