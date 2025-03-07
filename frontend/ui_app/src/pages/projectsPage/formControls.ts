export interface ProjectFormData {
    name: string;
    description: string;
    is_active: boolean;
    staging_url: string;
    remote_url: string;
    credentials_user: any;
    credentials_server: any;
    readme: string;
    user: string;
    modified_by?: string;
}

export interface ProjectFormErrors {
    name?: string | null;
    description?: string | null;
    is_active?: string | null;
    staging_url?: string | null;
    remote_url?: string | null;
    credentials_user?: string | null;
    credentials_server?: string | null;
    readme?: string | null;
    user?: string | null;
    modified_by?: string | null;
    unknown?: string | null;
}