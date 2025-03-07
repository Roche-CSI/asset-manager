
const ROUTES = {
    ASSET: 'db/asset',
    ASSET_CLASS: 'db/asset_class',
    ASSET_COMMIT: 'db/asset_commit',
    ASSET_VERSION: 'db/asset_version',
    ASSET_REF: 'db/asset_ref',
    GCS_SIGNING: "db/file_url"
};

export default class URLs {
    base_url: string;

    constructor(base_url: string) {
        this.base_url = base_url;
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

    gcs_signing_route() {
        return this.construct_url(this.base_url + ROUTES.GCS_SIGNING)
    }

    construct_url(base_url: string, id?: string | number) {
        let url = base_url
        if (id) {
            url = base_url + "/" + id;
        }
        return url;
    }

}