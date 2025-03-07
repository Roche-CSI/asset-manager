import { RestObject } from "../base";
import AssetURLs from "./assetURLs";

export interface UserRole {
    access_level: string
    created_at: string
    email: string
    id: number
    role_id: number
    username: string
}

export interface ProjectData {
    id: string;
    name: any;
    title: string;
    is_active: boolean;
    staging_url: string;
    remote_url: string;
    description: string;
    created_at: string;
    created_by: string;
    credentials_server: any;
    credentials_user: any;
    readme: string;
}

export default class Project extends RestObject implements ProjectData {
    id: string;
    name: string;
    title: string;
    is_active: boolean;
    staging_url: string;
    remote_url: string;
    description: string;
    created_at: string;
    created_by: string;
    credentials_server: any;
    credentials_user: any;
    readme: string;

    constructor(data: ProjectData) {
        super()
        this.id = data.id;
        this.name = data.name;
        this.title = data.title;
        this.is_active = data.is_active;
        this.staging_url = data.staging_url;
        this.remote_url = data.remote_url;
        this.description = data.description;
        this.created_at = data.created_at;
        this.created_by = data.created_by;
        this.readme = data.readme;
        this.credentials_server = data.credentials_server;
        this.credentials_user = data.credentials_user;
    }

    static URL(id?: string) {
        return new AssetURLs().project_route(id);
    }

    public url(): String {
        return Project.URL(this.id);
    }

    public static getFromServer(username: string, id?: string) {
        if (id) {
            return Project.get(Project.URL(id), { user: username })
        }
        return Project.get(Project.URL(), { user: username });
    }

    public static create(username: string, data: any, dry_run = false) {
        if (dry_run) {
            return new Promise((resolve, reject) => {
                setTimeout(() => resolve(null), 3000);
            });
        } else {
            data = { ...data, user: username }
            return Project.post(Project.URL(), data, undefined);
        }
    }

    public static update(id: any, username: string, data: any, dry_run = false) {
        if (dry_run) {
            return new Promise((resolve, reject) => {
                resolve(null);
            })
        } else {
            data = { ...data, user: username }
            return Project.put(Project.URL(id), data);
        }
    }

    // give user access to project
    public static addUserRole(data: any) {
        const userRoleURL: string = new AssetURLs().user_role_route()
        return Project.post(userRoleURL, data);
    }
    
    // give user access to project
    public static updateUserRole(id: string, data: any) {
        const userRoleURL: string = new AssetURLs().user_role_route(id)
        return Project.put(userRoleURL, data);
    }

    // remove user access
    public static deleteUserRole(id: string, deleted_by: string, project_name: string) {
        const userRoleURL: string = new AssetURLs().user_role_route(id)
        return Project.delete(userRoleURL,
            { deleted_by: deleted_by, project_name: project_name });
    }

    public static getUsersList(username: string, project_name: string) {
        const userRoleURL: string = new AssetURLs().user_role_route()
        return Project.get(userRoleURL, { user: username,  project_name: project_name});
    }
    
    public static getBucketsList(username: string, project_id: string) {
        const bucketURL: string = new AssetURLs().bucket_route()
        return Project.get(bucketURL, { user: username,  project_id: project_id});
    }
    
    public static removeBucket(id: string, deleted_by: string, project_id: string) {
        const bucketURL: string = new AssetURLs().bucket_route(id)
        return Project.delete(bucketURL,
            { deleted_by: deleted_by, project_id: project_id, bucket_id: id });
    }
}
