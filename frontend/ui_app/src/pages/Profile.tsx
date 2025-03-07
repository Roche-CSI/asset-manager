import React from "react";
import styles from "./pages.module.scss"
import { AccountCircleRounded } from "@mui/icons-material";
import { StoreNames, useStore } from "../stores";
import { CopyButton } from "../components/copyButton"

export default function Profile() {
    //stores
    const userStore = useStore(StoreNames.userStore);
    const userInfo: any = userStore.get("user")

    return (
        <div className={styles.page}>
            <h5 className={styles.pageHeader}>User Profile</h5>
            <div className={styles.card}>
                <div className={styles.cardHeader}>
                    <AccountCircleRounded />
                    <h4>
                        {userInfo.username}
                    </h4>
                </div>
                <div className={styles.cardBody}>
                    <div className={styles.cardItem}>
                        <p>Email:</p>
                        {userInfo.email}
                    </div>
                    <div className={styles.cardItem}>
                        <p>User Token:</p>
                        <div className={styles.userToken}>
                            <CopyButton textToCopy={userInfo.token} />
                            <textarea name="userToken" wrap="soft" 
                                disabled={true}
                                value={userInfo.token} />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )

}