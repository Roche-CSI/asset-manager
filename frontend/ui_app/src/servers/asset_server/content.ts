import {ReadOnlyRestObject} from "../base";
import AssetURLs from './assetURLs';

export interface ContentInterface {
    id: string;
    mime_type: string | null;
    size: number;
    meta: object | null;
    created_by: string;
    created_at: string;
}

const MB_TO_BYTES: number = 1000000;

export default class Content extends ReadOnlyRestObject implements ContentInterface{
    private static HASH_SEP: string = "_";
    private static ID_SEP: string = ":";
    public static STORAGE_SYSTEMS: string[] = ["gs", "s3"];
    public static DOWNLOAD_SIZE_LIMIT: number = 100 * MB_TO_BYTES; // 10 MB maximum
    id: string;
    mime_type: string | null;
    size: number;
    meta: object | null;
    created_by: string;
    created_at: string;

    constructor(data: object) {
        super();
        let parsed = data as ContentInterface;
        this.id = parsed.id;
        this.mime_type = parsed.mime_type;
        this.size = parsed.size;
        this.meta = parsed.meta;
        this.created_by = parsed.created_by;
        this.created_at = parsed.created_at;
    }

    /* post, list url, param:{ user: username} */
    public static URL(id?: number) {
        return new AssetURLs().content_route(id);
    }

    public hash() {
        return Content.parseHash(this.id);
    }

    public static parseId(id: string) {
        return id.split(Content.ID_SEP);
    }

    public static storageSystem(id: string) {
        return Content.parseId(id)[0];
    }

    public static parseHash(id: string) {
        return Content.parseId(id)[1].split(Content.HASH_SEP);
    }

    /**
     * Fetch content objects by username and a list of content ids
     * @returns Object {[content_id_0]: Content{}, [content_id_1]: {}, ...}
     */
    public static getContents(user: string, contentIdList: string[]): Promise<any> {
        let url = new AssetURLs().content_route();
        return Content.get(url, {content_ids: contentIdList, user: user});
    }
}