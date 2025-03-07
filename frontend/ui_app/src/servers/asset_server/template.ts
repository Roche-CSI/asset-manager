import { RestObject } from "../base";
import AssetURLs from "./assetURLs";

export interface TemplateData {
    id: string
    name: string
    title: string
    category: string // asset or object
    configs: any
    sample_data: any
    version: string
    description: string
    created_at: string
    created_by: string
    is_active: boolean
    readme: string
}

export const TEMPLATE_CATEGORIES = {
    EMPTY: "",
    ASSET: "asset",
    OBJECT: "object"
}

export default class Template extends RestObject implements TemplateData {
    created_by: string;
    created_at: string;
    description: string;
    id: string;
    is_active: boolean;
    name: string;
    title: string;
    readme: string;
    version: string;
    category: string;
    configs: any;

    constructor(data: TemplateData) {
        super()
        this.id = data.id;
        this.name = data.name;
        this.is_active = data.is_active;
        this.description = data.description;
        this.created_at = data.created_at;
        this.created_by = data.created_by;
        this.readme = data.readme;
        this.version = data.version;
        this.title = data.title;
        this.category = data.category;
        this.configs = data.configs;
    }

    static URL(id?: string) {
        return new AssetURLs().template_route(id);
    }

    public url(): String {
        return Template.URL(this.id);
    }

    public static getFromServer(username: string, id?: string) {
        if (id) {
            return Template.get(Template.URL(id), { user: username })
        }
        return Template.get(Template.URL(), { user: username });
    }

    public static create(username: string, data: any, dry_run = false) {
        if (dry_run) {
            return new Promise((resolve, reject) => {
                setTimeout(() => resolve(null), 3000);
            });
        } else {
            data = { ...data, user: username }
            return Template.post(Template.URL(), data, undefined);
        }
    }

    public static update(id: any, username: string, data: any, dry_run = false) {
        if (dry_run) {
            return new Promise((resolve, reject) => {
                resolve(null);
            })
        } else {
            data = { ...data, user: username }
            return Template.put(Template.URL(id), data);
        }
    }

    // add template to asset-class or asset
    public static addEntity(created_by: string, username: string, entity_name: string, entity_id: string) {
        const templateURL: string = new AssetURLs().template_route()
        return Template.post(templateURL,
            { created_by: created_by, username: username, entity_name: entity_name, entity_id: entity_id });
    }

    // remove template from asset-class or asset
    public static removeEntity(id: string, deleted_by: string, entity_name: string, entity_id: string) {
        const userRoleURL: string = new AssetURLs().user_role_route(id)
        return Template.delete(userRoleURL,
            { deleted_by: deleted_by, entity_name: entity_name, entity_id: entity_id });
    }

    public static getTemplateList(username: string, entity_name: string, entity_id: string) {
        const url: string = new AssetURLs().template_route()
        return Template.get(url, { user: username,  entity_name: entity_name, entity_id: entity_id});
    }
}
