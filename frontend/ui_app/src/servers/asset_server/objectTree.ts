import AssetObject from "./assetObject";
import {getFileType} from "./contentType";
import Content from "./content";

export default class ObjectTree {
    objects: AssetObject[];
    private _fileTree: [] | null;

    constructor(objects: AssetObject[]) {
        this.objects = objects;
        this._fileTree = null;
    }

    public chonkyFileMap(rootName: string) {
        let rootId = "xsdsdsdwewe";
        let tree = this.fileTree();
        const fileMap = {
            [rootId]: {
                id: rootId,
                name: rootName,
                isDir: true,
                childrenIds: tree.map((o: any) => o.id),
                childrenCount: tree.length,
                parentId: null
            }
        }
        this.flatten(tree, fileMap, rootId);
        let result = {
            rootFolderId: rootId,
            fileMap: fileMap
        }
        return result;
    }

    /***
     * recursively flatten nested array
     * @param nested
     * @param flat
     * @param parentId
     * @private
     */
    private flatten(nested: any, flat: any, parentId: string) {
        for (let index = 0; index < nested.length; index++) {
            const element = nested[index];
            let childrenIds = [];
            if (element.children && element.children.length > 0) {
                childrenIds = element.children.map((o: any) => o.id);
                this.flatten(element.children, flat, element.id)
            }
            if (element.id) {
                flat[element.id] = {...element, childrenIds: childrenIds, parentId: parentId};
            }
        }
    }

    public fileTree() {
        if (!this._fileTree) {
            this._fileTree = this.constructTree()
        }
        return this._fileTree;
    }

    /**
     * Construct object tree to be used in this.ChonkyFileMap
     * FileData API: https://chonky.io/docs/2.x/basics/files
     * @returns {Array} file tree: [ {...FileData, children: [ {}, {}, ... ] } ]
     */
    private constructTree(): [] {
        let result: any = [];
        let level: any = {result};
        this.objects.forEach(obj => {
            const [contentId, objectPath] = AssetObject.parseId(obj.id);
            let path = this.normalizePath(objectPath);
            let storage = Content.storageSystem(contentId);
            const currentStorages: string[] = Content.STORAGE_SYSTEMS;
            let comps = currentStorages.includes(storage) ? path.split("/") : [path];
            // console.log("path:", path);
            comps.reduce((r, name, i, a) => {
                // console.log(`level:${JSON.stringify(level)}, r:${JSON.stringify(r)}, name:${name}, i:${i}, a:${a}`)
                if(!r[name]) {
                    r[name] = {result: []};
                    let isFile = Boolean(i === a.length - 1);
                    let isDir = !isFile;
                    let file_type = isDir ? null : getFileType(this.fileExtension(name as string), obj?.content?.mime_type);
                    let file: any = {
                        id: a.slice(0, i + 1).join("/"),
                        name: name,
                        ext: name.includes(".") ? undefined : "",
                        isFile: isFile,
                        isDir: isDir,
                        fileType: file_type,
                        size: isFile? obj?.content?.size: undefined,
                        object_id: isFile ? obj?.id : null,
                        content_id: isFile? obj?.content_id : null,
                        children: r[name].result,
                    }
                    file["childrenCount"] = file.children.length;
                    r.result.push(file)
                    // console.log(`result:`, JSON.stringify(r.result));
                }
                return r[name];
            }, level)
        })
        return result;
    }


    /**
     * if path starts with ./ or ../ then remove it
     * @param path
     * @private
     */
    private normalizePath(path: string) {
        if (path.startsWith("./")) {
            return path.substring("./".length, path.length);
        }else if (path.startsWith("../")) {
            return path.substring("../".length, path.length);
        } else if (path.startsWith("/")) {
            return path.substring("/".length, path.length);
        }
        return path;
    }

    private fileExtension(fileName: string) {
        let comps = fileName.split('.');
        return (comps.length > 1) ? comps.pop() : null;
    }

}