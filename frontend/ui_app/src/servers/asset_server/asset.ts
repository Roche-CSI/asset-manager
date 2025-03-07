import {RestObject} from "../base";
import {AssetVersion} from "./assetVersion";
import AssetObject from "./assetObject";
import AssetURLS from "./assetURLs";

export interface AssetInterface {
    id: string;
    asset_class: string;
    seq_id: number;
    title: string;
    description: string;
    owner: string;
    version?: object;
    top_hash: string;
    refs: object | null;
    alias: string;
    all_objects: object[];
    versions: object[];
    leaf_version: object | null;
    created_by: string;
    created_at: string;
    modified_at: string;
    modified_by: string;
    root_version_id: number;
    leaf_version_id: number;
    status: number;
    metadata: object;
    tags: string[];
    attributes: object;
    phase: number;
}

const sampleAsset: AssetInterface = {
    id: "9f7e6d5c-4b3a-2d1e-8f9g-7h6i5j4k3l2m",
    asset_class: "video",
    seq_id: 1234,
    title: "The Long Night",
    description: "Battle of Winterfell - Episode 3, Season 8 of Game of Thrones",
    owner: "hbo_productions",
    version: {
        id: 1,
        created_at: "2023-09-15T14:30:22-0500",
        created_by: "jonsnow"
    },
    top_hash: "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6",
    refs: {
        previous_version: "9f7e6d5c-4b3a-2d1e-8f9g-7h6i5j4k3l2n",
        related_assets: ["9f7e6d5c-4b3a-2d1e-8f9g-7h6i5j4k3l2o", "9f7e6d5c-4b3a-2d1e-8f9g-7h6i5j4k3l2p"]
    },
    alias: "s08e03_battle_of_winterfell",
    all_objects: [
        { type: "video", path: "/assets/videos/game_of_thrones/season8/s08e03.mp4" },
        { type: "subtitle", path: "/assets/subtitles/game_of_thrones/season8/s08e03_en.srt" }
    ],
    versions: [
        {
            id: 1,
            created_at: "2023-09-15T14:30:22-0500",
            created_by: "jonsnow",
            changes: "Initial upload"
        },
        {
            id: 2,
            created_at: "2023-09-16T09:45:10-0500",
            created_by: "tyrionlannister",
            changes: "Updated metadata"
        }
    ],
    leaf_version: {
        id: 2,
        created_at: "2023-09-16T09:45:10-0500",
        created_by: "tyrionlannister",
        changes: "Updated metadata"
    },
    created_by: "jonsnow",
    created_at: "2023-09-15T14:30:22-0500",
    modified_at: "2023-09-16T09:45:10-0500",
    modified_by: "tyrionlannister",
    root_version_id: 1,
    leaf_version_id: 2,
    metadata: {}
};

export default class Asset extends RestObject implements AssetInterface {
    id: string;
    alias: string;
    asset_class: string;
    title: string;
    description: string;
    owner: string;
    refs: any = {};
    seq_id: number;
    top_hash: string;
    versions: AssetVersion[] = [];
    leaf_version: AssetVersion | null;
    created_by: string;
    created_at: string;
    modified_at: string;
    modified_by: string;
    all_objects: any = {};
    // active_version_id: number;
    root_version_id: number;
    leaf_version_id: number;
    status: number;
    metadata: object;
    tags: string[];
    attributes: any = {};
    phase: number;

    constructor(data: object | null) {
        super();
        const parsed = data as AssetInterface;
        this.id = parsed.id;
        this.seq_id = parsed.seq_id;
        this.owner = parsed.owner;
        this.title = parsed.title;
        this.description = parsed.description;
        this.created_by = parsed.created_by;
        this.created_at = parsed.created_at;
        this.modified_at = parsed.modified_at;
        this.modified_by = parsed.modified_by;
        this.top_hash = parsed.top_hash;
        this.refs = parsed.refs || {};
        this.alias = parsed.alias;
        this.asset_class = parsed.asset_class;
        // this.asset_class = new AssetClass(parsed.asset_class as AssetClassInterface);
        if (Array.isArray(parsed.all_objects)) {
            this.updateObjects(parsed.all_objects)
        }
        this.versions = [];
        this.leaf_version = parsed.leaf_version? new AssetVersion(parsed.leaf_version): null;
        if (parsed.versions) {
            //sort by id
            parsed.versions.sort(version => (version as any).id);
            this.versions = parsed.versions.map(version_data => new AssetVersion(version_data, this));
        }
        // this.active_version_id = this.versions[this.versions.length - 1].id;
        this.root_version_id = parsed.root_version_id;
        this.leaf_version_id = parsed.leaf_version_id;
        this.status = parsed.status;
        this.metadata = parsed.metadata;
        this.tags = parsed.tags || [];
        this.attributes = parsed.attributes || {};
        this.phase = parsed.phase;
    }

    public updateObjects(data: Array<object>) {
        data.forEach((obj_data: any) => {
            let obj = new AssetObject(obj_data);
            this.all_objects[obj.id] = obj;
        })
    }

    public updateRefs(data: any) {
        this.refs = data
    }

    public static URL(id?: string) {
        /* post, list url */
        return new AssetURLS().asset_route(id);
    }

    public static getName(className: string, seqId: number) {
        return `${className}/${seqId.toString()}`;
    }

    public name(className: string): string {
        return Asset.getName(className, this.seq_id);
    }

    public versionName(className: string, version: string): string {
        return `${this.name(className)}/${version}`;
    }
    
    public getNumObjects(leaf=false): number {
        if (leaf) {
            return this.leaf_version?.num_objects || 0;
        }
        return this.all_objects ? Object.keys(this.all_objects).length : this.leaf_version?.num_objects!;
    }
    
    public getSize(leaf=false): number {
        if (leaf) {
            return this.leaf_version?.size || 0;
        }
        if (this.all_objects && this.all_objects.length > 0) {
            return this.all_objects.reduce((total: number, object: AssetObject) => {
                return total + (object.content?.size || 0);
            }, 0);
        } else {
            return this.leaf_version?.num_objects || 0;
        }
    }
    
    
    public url() {
        /* get, update, delete url */
        if (!this.id) {
            throw new Error("invalid asset")
        }
        return Asset.URL(this.id);
    }

    public static getFromServer(id?: string | null, name?: string, project_id?: string) {
        if (id) {
            return Asset.get(Asset.URL(id))
        } else {
            return Asset.get(Asset.URL(), {asset_names: [name], project_id: project_id})
        }
    }
    
    public static update(id: any, data: any, dry_run = false) {
        if (dry_run) {
            return new Promise((resolve, reject) => {
                resolve(sampleAsset);
            });
        } else {
            return Asset.put(Asset.URL(id), data);
        }
    }

    public fileTree(objects: AssetObject[]) {
        let result: any[] = [];
        let level = {result};
        objects.forEach((obj) => {
            obj.path().split('/').reduce(
                (r: any, name: string, i, a) => {
                    // console.log(r);
                    if (!r[name]) {
                        r[name] = {result: []};
                        r.result.push({name, children: r[name].result})
                    }
                    return r[name];
                }, level)
        })
        return result;
    }

    /***
     * returns the AssetVersion matching the given
     * @param versionNumber
     * @param id
     */
    public getVersion(versionNumber?: string | null, id?: number): AssetVersion | null {
        if (!this.versions) return null;
        for (let index in this.versions) {
            if (versionNumber === this.versions[index].number || id === this.versions[index].id) {
                return this.versions[index];
            }
        }
        return null;
    }

    public updateVersion(version: AssetVersion) {
        for (let index in this.versions) {
            if (version.id === this.versions[index].id) {
                this.versions[index] = version;
                return;
            }
        }
        // if not existing, then add
        this.versions.push(version);
    }

    public updateVersions(data: Array<object>) {
        this.versions = data.map((version_data: any) => new AssetVersion(version_data))
    }

    /***
     * returns the latest version of the asset
     */
    public leafVersion(): AssetVersion {
        if (this.leaf_version_id) {
            const leaf_version: any = this.versions.find((ver: any) => ver.id === this.leaf_version_id)
            if (leaf_version) return leaf_version
        }
        return this.leaf_version || this.versions[this.versions.length - 1];
    }

    public leafVersionNumber(): string {
        let leaf = this.leafVersion();
        return leaf ? leaf.number : "0.0.0";
    }
    
    /**
     * Checks if the asset matches the given search term
     * Search is case-insensitive and matches partial strings
     * @param searchTerm - The term to search for
     * @returns boolean - True if the asset matches the search term
     */
    public matchesSearch(searchTerm: string): boolean {
        // Convert search term to lowercase for case-insensitive comparison
        const term = searchTerm.toLowerCase().trim();
        
        // Return false if search term is empty
        if (!term) return false;
        
        // Fields to check for matches
        const searchableFields = [
            this.title,
            this.description,
            this.seq_id?.toString(),
            this.alias,
            this.created_by,
            this.modified_by,
            ...this.tags
        ];
        
        // Check if any field matches the search term
        return searchableFields.some(field => {
            if (field) {
                return field.toString().toLowerCase().includes(term);
            }
            return false;
        });
    }
    
    /**
     * Static method to filter an array of assets based on a search term
     * @param assets - Array of assets to filter
     * @param searchTerm - The term to search for
     * @returns Asset[] - Array of assets that match the search term
     */
    public static filterAssets(assets: Asset[], searchTerm: string): Asset[] {
        return assets.filter(asset => asset.matchesSearch(searchTerm));
    }
    
    public getHandle(className: string) {
        return `${className}/${this.alias || this.seq_id}`;
    }
}
