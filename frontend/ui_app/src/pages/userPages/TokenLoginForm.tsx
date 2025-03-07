import React from "react";
import { Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import { StoreNames, useStore } from "../../stores";

export default function GoogleLoginForm() {
    const [token, setToken] = React.useState<string>("")
    const userStore = useStore(StoreNames.userStore, true);
    const navigate = useNavigate();

    /**
     * Redirect to projects page with token, to be used for authentication in PrivateRoute
     */
    const onSubmit = () => {
        navigate(`${userStore.get("redirect_url") ?? "/projects"}?token=${token}`);
    }

    return (
        <div>
            <label>Enter User Token</label>
            <textarea className={'my-2 border border-gray-300 rounded-md p-2 w-full'}
                required={true}
                onChange={(e) => setToken(e.target.value)}>
            </textarea>
            <Button variant={"primary"}
                onClick={() => { onSubmit() }}>
                Login with Token
            </Button>
        </div>
    );
}