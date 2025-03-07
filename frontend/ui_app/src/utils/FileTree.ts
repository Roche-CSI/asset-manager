/**
 * file tree class to construct directory tree for a list of File object
 */
import { diffItem } from "../servers/asset_server/assetVersion"

export default class FileTree {
    files: any[] | null;
    paths: string[];
    tree: any[];

    constructor(files: any[] | null) {
        this.files = files;
        this.paths = [];
        this.tree = [];
    }

    build = () => {
        this.paths = FileTree.getPaths(this.files);
        this.tree = FileTree.pathsToTree(this.paths);
    }

    getTree = () => {
        return this.tree;
    }

    /**
     * return an array of paths for each File object in FileList
     * @param files FileList: array like object; consists of list of File objects
     * @returns paths
     */
    static getPaths(files: any[] | null) {
        let paths: string[] = [];
        if (!files) return paths;
        for (let i = 0; i < files.length; i++) {
            paths.push(files[i].webkitRelativePath)
        }
        return paths;
    }

    /**
     * Construct directory's tree structure based on a list of paths
     * @param paths 
     * @returns [ {root_0: {name: root_0_name, children: [....]} }, ...]
     */
    public static pathsToTree(paths: string[]) {
        let tree: any = [];
        if (paths.length === 0) return tree;

        paths.reduce((r, path) => {
            let names = path.split('/');
            names.reduce((q, name) => {
                let temp = q.find((o: { name: string; }) => o.name === name);
                if (!temp) {
                    q.push(temp = { name, children: [] });
                }
                return temp.children
            }, r)
            return r;
        }, tree)

        return tree;
    }

    public static diffArrayToTree(diffArray: diffItem[]) {
        let tree: any = [];
        if (diffArray.length === 0) return tree;

        diffArray.reduce((r, current) => {
            let names = current.path.split('/');
            names.reduce((q: any, name: any) => {
                let temp = q.find((o: { name: string; }) => o.name === name);
                if (!temp) {
                    temp = { ...current, name, children: [] }
                    q.push(temp);
                }
                return temp.children
            }, r)
            return r;
        }, tree)

        return tree;
    }

    static prettyPrintTree(tree: any[]) {
        if (!tree || tree.length === 0) return null;
        const print: any = (data: any[], indentation: number, prefix: string = '') => {
            return data.map(({ name, children }) => children.length > 0
                ? prefix + name + '\n' + print(children, indentation, (prefix || '|') + '_'.repeat(indentation))
                : prefix + name
            ).join('\n')
        }
        return print(tree, 3)
    }
}