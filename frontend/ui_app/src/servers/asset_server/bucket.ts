import { RestObject } from "../base";
import AssetURLs from "./assetURLs";

export interface BucketData {
    id: string;
    bucket_url: string;
    is_active: boolean;
    keys: string;
    title: string;
    description: string;
    created_at: string;
    created_by: string;
    is_primary: boolean; // primary bucket for a project
    configs: object;
}

export default class Bucket extends RestObject implements BucketData {
    bucket_url: string;
    configs: object;
    created_at: string;
    created_by: string;
    title: string;
    description: string;
    id: string;
    is_active: boolean;
    keys: string;
    is_primary: boolean;
    
    constructor(data: BucketData) {
        super()
        this.title = data.title;
        this.id = data.id;
        this.bucket_url = data.bucket_url;
        this.is_active = data.is_active;
        this.description = data.description;
        this.created_at = data.created_at;
        this.created_by = data.created_by;
        this.keys = data.keys;
        this.configs = data.configs;
        this.is_primary = data.is_primary;
    }

    static URL(id?: string) {
        return new AssetURLs().bucket_route(id);
    }

    public url(): String {
        return Bucket.URL(this.id);
    }

    public static getFromServer(username: string, id?: string) {
        if (id) {
            return Bucket.get(Bucket.URL(id), { user: username })
        }
        return Bucket.get(Bucket.URL(), { user: username });
    }

    public static create(username: string, data: any, dry_run = false) {
        if (dry_run) {
            return new Promise((resolve, reject) => {
                setTimeout(() => resolve(null), 3000);
            });
        } else {
            data = { ...data, user: username }
            return Bucket.post(Bucket.URL(), data, undefined);
        }
    }

    public static update(id: any, username: string, data: any, dry_run = false) {
        if (dry_run) {
            return new Promise((resolve, reject) => {
                resolve(null);
            })
        } else {
            data = { ...data, user: username }
            return Bucket.put(Bucket.URL(id), data);
        }
    }
}
