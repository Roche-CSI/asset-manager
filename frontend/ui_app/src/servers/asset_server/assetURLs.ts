import URLs from "../base/urls";
import CONFIG from "../asset_server.config.json";

const BASE_URL = import.meta.env.VITE_API_URL || CONFIG.BASE_URL;
const ROUTES = CONFIG.ROUTES;

export default class AssetURLs extends URLs {

    constructor() {
        super(BASE_URL);
        // console.log("base-url:", this.base_url);
    }

    asset_route(id?: string) {
        return this.construct_url(this.base_url + ROUTES.ASSET, id)
    }

    asset_class_route(id?: string) {
        return this.construct_url(this.base_url + ROUTES.ASSET_CLASS, id);
    }

    asset_version_route(id?: number) {
        return this.construct_url(this.base_url + ROUTES.ASSET_VERSION, id);
    }

    asset_ref_route(id?: number) {
        return this.construct_url(this.base_url + ROUTES.ASSET_REF, id);
    }

    asset_object_route(id?: number) {
        return this.construct_url(this.base_url + ROUTES.ASSET_OBJECT, id)
    }

    gcs_signing_route() {
        return this.construct_url(this.base_url + ROUTES.GCS_SIGNING)
    }

    login_route() {
        return this.construct_url(this.base_url + ROUTES.GOOGLE_LOGIN);
    }

    token_login_route() {
        return this.construct_url(this.base_url + ROUTES.TOKEN_LOGIN);
    }

    content_route(id?: number) {
        return this.construct_url(this.base_url + ROUTES.CONTENT, id)
    }

    signup_route() {
        return this.construct_url(this.base_url + ROUTES.SIGN_UP)
    }

    asset_settings_route() {
        return this.construct_url(this.base_url + ROUTES.ASSET_SETTINGS)
    }

    project_route(id?: string) {
        return this.construct_url(this.base_url + ROUTES.PROJECT, id)
    }

    user_role_route(id?: string) {
        return this.construct_url(this.base_url + ROUTES.USER_ROLE, id)
    }

    tag_route(id?: string) {
        return this.construct_url(this.base_url + ROUTES.TAG, id)
    }

    issues_route() {
        return this.construct_url(this.base_url + ROUTES.ISSUES)
    }
    
    bucket_route(id?: string) {
        return this.construct_url(this.base_url + ROUTES.BUCKET, id)
    }
    
    template_route(id?: string) {
        return this.construct_url(this.base_url + ROUTES.TEMPLATE, id)
    }
    
    asset_search_route() {
        return this.construct_url(this.base_url + ROUTES.ASSET_SEARCH)
    }
}
