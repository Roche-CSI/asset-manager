import React, { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation, useNavigate } from "react-router-dom";
import { StoreNames, useStore } from "../../stores";
import { isEmptyObject } from "../../utils";
import { useQuery } from "../../utils/utils";
import AssetURLs from "../../servers/asset_server/assetURLs";
import { fetchPost } from "../../servers/base";


export function save_user(store: any, userInfo: any) {
    if (!userInfo.user) {
        throw new Error("invalid user")
    }
    store.set("user", userInfo.user);
    store.set("roles", userInfo.roles);
    const projects_data = parse_projects(userInfo.roles, userInfo.default_project)
    store.set("projects", projects_data.projects);
    store.set("active_project", projects_data.active)
    store.set("redirect_url", userInfo.redirect_url)
    store.set("dashboard_settings", userInfo.dashboard_settings)
    return userInfo.user.token;
}

function parse_projects(roles: object[], default_project: string): any {
    let projects: any = {};
    roles.forEach((role: any, idx: number) => {
        let project: any = role.project;
        let existing = projects[project.id] || {};
        project.can_edit = Boolean(role.can_edit || existing.can_edit);
        project.can_read = Boolean(role.can_read || existing.can_read);
        project.can_delete = Boolean(role.can_delete || existing.can_delete);
        project.can_admin_project = Boolean(role.can_admin_project || existing.can_admin_project);
        projects[project.id] = project;
    })
    // active: default if only one project, or the fist project excluding default if more than one project
    let active: string | null = !isEmptyObject(projects) ? Object.keys(projects)[0] : null;
    if (Object.keys(projects).length > 1) {
        let keys: string[] = Object.keys(projects);
        let defaultIndex: number = keys.indexOf(default_project)
        if (defaultIndex > -1) {
            keys.splice(keys.indexOf(default_project), 1)
            active = keys[0]
        }
    }
    return { projects: projects, active: active }
}


export function PrivateRoute({ children }: any) {
    const userStore = useStore(StoreNames.userStore);
    const urlStack = useStore(StoreNames.urlHistoryStore);
    const location = useLocation();
    const query = useQuery();
    const [token, setToken] = useState<string>((userStore.get("user") || {}).token)
    const [error, setError] = useState<string | null>(null);
    const navigate = useNavigate();

    const loginWithToken = (jwtToken: string | null) => {
        let data: Record<string, string> = {};
        if (jwtToken) {
            data = { jwt: jwtToken }
        }
        fetchPost(new AssetURLs().token_login_route(), data).then((data: any) => {
            // console.log("res: ", data);
            if (data.error) {
                throw new Error(data.error);
            }
            let token = save_user(userStore, data);
            setToken(token);
        }).catch((err) => {
            setError(JSON.stringify(err.message))
            // urlStack.set('redirect_from', `${window.location.pathname}${window.location.search}`)
            setError(error || 'Please login to access the page you requested');
        })
    }

    useEffect(() => {
        if (token) return;
        const cliToken = query.get('token');
        if (cliToken) { // Coming from Python CLI
            loginWithToken(cliToken);
        } else { // Coming from web login, cookies based login
            loginWithToken(null);
        }
    }, [token])

    if (error) {
        const route = `/login?error=${error}`
        return <Navigate to={route} replace={true} />
    }

    return (
        <div>
            {token ?
                (children ?? <Outlet />)
                :
                null
            }
        </div>
    )

}
