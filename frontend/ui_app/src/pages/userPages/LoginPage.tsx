import React, { useState } from "react";
import styles from "./login.module.scss";
import { useQuery } from "../../utils/utils";
import TokenLoginForm from "./TokenLoginForm";
import { fetchGet } from "../../servers/base";
import AssetURLs from "../../servers/asset_server/assetURLs";
import { useNavigate } from "react-router-dom";
import {Alert} from "../../components/errorBoundary";
import {LoginV2} from "./LoginV2";
import {SignupV2} from "./SignupV2";


export default function LoginPage() {
    const navigate = useNavigate();
    const query = useQuery();
    const action = query.get("action");
    const error = query.get("error");
    const [loginError, setLoginError] = useState('');

    function onSubmit(event: any) {
        fetchGet(new AssetURLs().login_route()).then((data: any) => {
            console.log("res: ", data);
            window.location.assign(data.auth_url);
        }).catch((err) =>
            setLoginError("Oh Snap! You've got an unexpected error."));
    }

    return (
        <div className={`${styles.page}`}>
            {loginError && renderError()}
            {loginActions(action)}
        </div>
    )

    function loginForm() {
        return <LoginV2/>
    }

    function loginActions(action: string) {
        let content;

        switch (action) {
            case "signup":
                content = <SignupV2 onClick={onSubmit}/>
                break;
            case "login-with-token":
                content = <div className={styles.card}>
                    <TokenLoginForm />
                </div>
                break;
            default:
                content = loginForm();
                break;
        }
        return <div>{content}</div>;
    }

    function renderError() {
        return (
            <Alert variant={"error"} title={"Oh snap! You got an error!"} 
				description={[
					loginError, 
					"Also: Make sure you are connected to VPN"]}
				/>
        )
    }
}
