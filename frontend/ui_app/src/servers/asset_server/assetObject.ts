import Content from "./content";
import {ReadOnlyRestObject} from "../base";
import AssetURLs from "./assetURLs";
import {getFileType} from "./contentType";

export interface AssetObjectInterface {
    id: string;
    url_id: number;
    content_id: string;
    content: object;
    created_by: string;
    created_at: string;
}

export default class AssetObject extends ReadOnlyRestObject implements AssetObjectInterface {
    private static ID_SEP: string = "::";
    id: string;
    url_id: number;
    content_id: string;
    content: Content;
    created_by: string;
    created_at: string;

    constructor(data: object) {
        super();
        const parsed = data as AssetObjectInterface
        this.id = parsed.id;
        this.url_id = parsed.url_id;
        this.created_by = parsed.created_by;
        this.created_at = parsed.created_at;
        this.content_id = parsed.content.toString();
        this.content = new Content(parsed.content);
    }

    public static URL(id?: number) {
        /* post, list url */
        return new AssetURLs().asset_object_route(id);
    }

    /**
     * returns the path to which the object points
     */
    path(): string {
        return AssetObject.parseId(this.id)[1];
    }

    /**
     * Returns content id and path of the object
     */
    public static parseId(id: string) {
        return id.split(AssetObject.ID_SEP);
    }

    public static getContentId(id: string) {
        return AssetObject.parseId(id)[0]
    }

    /**
     * get the signed url for the object
     * @param classId the class id of the object
     * @param objectId object id - if parsed from url, use decoded object id using decodeURIComponent
     * @returns promise with the signed url response
     */
    public static getSignedGCSURL(classId: string, objectId: string): Promise<any> {
        let url = new AssetURLs().gcs_signing_route();
        return AssetObject.get(url, {class_id: classId, object_id: objectId});
    }

    public static getContentType(objectId: string, contentType?: string | null) {
        const [content_id, path] = AssetObject.parseId(objectId);
        return getFileType((path as string).split('.').pop(), contentType);
    }

}