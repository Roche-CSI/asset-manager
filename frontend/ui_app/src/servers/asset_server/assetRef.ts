import {ReadDeleteRestObject} from "../base";
import AssetURLs from "./assetURLs";

interface VersionSummary {
    id: number;
    name: string;
    asset: string; // asset-id
    asset_class: string; // asset-class-id
    class_title?: string;
    class_type?: string;
}

export interface AssetRefInterface {
    id: number;
    src_version: VersionSummary;
    dst_version: VersionSummary;
    created_by: string;
    created_at: string;
    label: string;
    properties: any;
    tags: string[];
}

export default class AssetRef extends ReadDeleteRestObject implements AssetRefInterface {
    id: number;
    dst_version: VersionSummary;
    src_version: VersionSummary;
    created_at: string;
    created_by: string;
    label: string;
    properties: any;
    tags: string[];

    constructor(data: object) {
        super();
        const parsed = data as AssetRefInterface;
        this.id = parsed.id;
        this.dst_version = parsed.dst_version;
        this.src_version = parsed.src_version;
        this.created_at = parsed.created_at;
        this.created_by = parsed.created_by;
        this.tags = parsed.tags ? parsed.tags : [];
        this.label = parsed.label || "";
        this.properties = parsed.properties;
    }

    public static URL(id?: number): string {
        /* post, list url */
        return new AssetURLs().asset_ref_route(id);
    }

    public url(): string {
        return AssetRef.URL(this.id);
    }

    /**
     * Find asset ref by asset name and version number
     */
    public static getRefs(user: string, project_id: string, asset_name: string[],
        version_number?: string[])
    : Promise<any> {
            let url = new AssetURLs().asset_ref_route() + "/find";
            let params: any = {user: user, asset_name: asset_name, project_id: project_id}
            if (version_number) {
                params["version_number"] = version_number
            }
            return AssetRef.get(url, params);
    }
}
