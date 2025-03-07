import {RestObject} from "../base";
import AssetURLs from "./assetURLs";
import {StringExt} from "utils/strUtils.ts";

export interface AssetClassData {
    id: string;
    name: string;
    owner: string;
    title: string;
    class_type: string;
    description: string;
    readme: string;
    created_by: string;
    created_at: string;
    counter: number;
    modified_at: string;
    modified_by: string;
    tags: string[];
    favorite?: boolean;
    attributes?: any;
    status: number;
}

const sample = {
    class_type: "",
    counter: 0,
    created_at: "2022/03/18 22-53-19 -0700",
    created_by: "user",
    description: "Game of Thrones Videos and Images here.",
    id: "72e6813b-043b-423f-bcab-43314bd4e7e8",
    modified_at: null,
    modified_by: null,
    name: "game of thrones",
    owner: "user",
    readme: null,
    soft_delete_at: null,
    soft_delete_by: null,
    status: 1,
    tags: [],
    title: "Game of Thrones",
};

export class Attributes {
    status: "active" | "deprecated" | "obsolete" | "deleted";
    constructor(data: any) {
        this.status = data && data.status ? data.status : "active";
    }
    toJSON() {
        return {status: this.status};
    }
    statusOptions() {
        return ["active", "deprecated", "obsolete", "deleted"];
    }
}


export default class AssetClass extends RestObject implements AssetClassData {
    id: string;
    name: string;
    created_by: string;
    created_at: string;
    counter: number;
    owner: string;
    modified_at: string;
    modified_by: string;
    title: string;
    class_type: string;
    readme: string;
    description: string;
    tags: string[];
    favorite?: boolean;
    attributes?: any;
    status: number;

    constructor(data: object) {
        super();
        const parsed = data as AssetClassData;
        this.id = parsed.id;
        this.name = parsed.name;
        this.owner = parsed.owner;
        this.title = parsed.title;
        this.class_type = parsed.class_type;
        this.description = parsed.description || this.sample_description();
        this.readme = parsed.readme;
        this.created_by = parsed.created_by;
        this.created_at = parsed.created_at;
        this.counter = parsed.counter;
        this.modified_at = parsed.modified_at;
        this.modified_by = parsed.modified_by;
        this.tags = parsed.tags;
        this.favorite = parsed.favorite || false;
        this.attributes = new Attributes(parsed.attributes);
        this.status = this.stringToNumber(parsed.status);
    }

    static URL(id?: string) {
        /* post, list url */
        return new AssetURLs().asset_class_route(id);
    }

    url() {
        /* get, update, delete url */
        return AssetClass.URL(this.id);
    }

    public static getFromServer(id?: string | null, name?: string | null, project_id?: string | null) {
        let url = id ? AssetClass.URL(id) : AssetClass.URL()
        let params: any = { project: project_id }; // server needs project to check access
        if (name) {
            params["class_names"] = [name]
        }
        return AssetClass.get(url, params)
    }

    public static create(data: any, dry_run = false) {
        if (dry_run) {
            return new Promise((resolve, reject) => {
                setTimeout(() => resolve(sample), 3000);
            });
        } else {
            return AssetClass.post(AssetClass.URL(), data);
        }
    }

    public static update(id: any, data: any, dry_run = false) {
        if (dry_run) {
            return new Promise((resolve, reject) => {
                resolve(sample);
            });
        } else {
            return AssetClass.put(AssetClass.URL(id), data);
        }
    }

    private sample_description() {
        //todo: add description to asset-class table
        return "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.";
    }
}
