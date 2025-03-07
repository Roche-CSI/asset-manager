import {ReadOnlyRestObject} from "../base";
import Asset from "./asset";
import AssetURLs from "./assetURLs";
import AssetObject from "./assetObject";

interface Patch {
    added: string[],
    removed: string[]
}

export interface diffItem {
    path: string;
    category: "added" | "altered" | "removed";
    id: string | null;
    prevId: string | null;
    children?: any[];
}

export interface diffObject {
    [key: string]: diffItem;
}

export interface AssetVersionInterface {
    id: number;
    commit_hash: string;
    commit_message: string;
    number: string;
    parent?: object; // parent version
    patch: Patch;
    created_by: string;
    created_at: string;
    tags: string[];
    size?: number;
    num_objects?: number;
}

export class AssetVersion extends ReadOnlyRestObject implements AssetVersionInterface {
    id: number;
    commit_hash: string;
    commit_message: string;
    number: string;
    parent?: AssetVersion; // parent version
    patch: Patch;
    created_by: string;
    created_at: string;
    tags: string[];
    asset: any // AssetPage, not imported to avoid circular reference
    size?: number;
    num_objects?: number;
    objects?: AssetObject[];

    constructor(data: object, asset?: any) {
        super();
        const parsed = data as AssetVersionInterface;
        this.id = parsed.id;
        this.commit_hash = parsed.commit_hash;
        this.commit_message = parsed.commit_message;
        this.number = parsed.number;
        this.patch = parsed.patch;
        this.created_by = parsed.created_by;
        this.created_at = parsed.created_at
        this.tags = parsed.tags ? parsed.tags : [];
        this.size = parsed.size;
        this.num_objects = parsed.num_objects;
        this.asset = asset;
        if (parsed.parent) {
            this.parent = new AssetVersion(parsed.parent);
        }
    }

    public static URL(id?: number) {
        /* post, list url */
        return new AssetURLs().asset_version_route(id);
    }

    public url() {
        /* get, update, delete url */
        if (!this.id) {
            throw new Error("invalid asset")
        }
        return AssetVersion.URL(this.id);
    }

    public static resolveVersions(versions: AssetVersion[], upto: AssetVersion): Set<string> {
        let result = new Set<string>();
        // applyPatch from the earliest version
        versions.sort((a: any, b: any) => a.id - b.id)
        versions.forEach(version => {
            if (version.id <= upto.id) {
                AssetVersion.applyPatch(result, version.patch);
            }
        })
        return result
    }
    
    public static applyPatch(base: Set<any>, patch: object) {
        let added: string[] = (patch as any)["added"];
        let removed: string[] = (patch as any)["removed"];
        added.forEach(object_id => base.add(object_id));
        removed.forEach(object_id => base.delete(object_id));
    }

    /**
     * Compute object difference between base version and compare version
     * @param base {AssetVersion}
     * @param compare {AssetVersion}
     * @returns an object {diffObject: {path: diffItem}, diffArray: diffItem[]}
     */
    public static computeDiff(base: AssetVersion | null, compare: AssetVersion | null): any {
            let baseObjects: AssetObject[] = (!base || !base.objects) ? [] : base.objects;
            let compareObjects: AssetObject[] = (!compare || !compare.objects)? [] :compare.objects;
            let diffObject: diffObject = {}
            baseObjects.forEach((obj: any) => {
                const path: string = AssetObject.parseId(obj.id)[1]
                diffObject[path] = {path: path, category: "removed", prevId: obj.id, id: null}
            })
            compareObjects.forEach((obj: any) => {
                const path: string = AssetObject.parseId(obj.id)[1]
                const baseItem: diffItem | undefined = diffObject[path]
                if (baseItem && obj.id === baseItem.prevId) {
                    delete diffObject[path]
                } else if (baseItem && obj.id !== baseItem.prevId) {
                    let alteredItem: diffItem =
                        {path: path, category: "altered", prevId: baseItem.prevId, id: obj.id}
                    diffObject[path] = alteredItem
                } else {
                    diffObject[path] = {path: path, category: "added", prevId: null, id: obj.id}
                }
            })
            return {
                diffObject: diffObject,
                diffArray: Object.values(diffObject)
            }
        }

    
    public static updateVersionObjects(asset: Asset, version: AssetVersion | null) {
        if (version && (!version.objects || version.objects.length === 0)) {
            let object_ids: Set<string> = AssetVersion.resolveVersions(asset.versions, version);
            let objects = new Set<any>();
            object_ids.forEach((id) => {
                const obj = asset.all_objects[id]
                if (obj) {
                    objects.add(obj);
                }
            })
            version.objects = Array.from(objects);
        }
    }
}
