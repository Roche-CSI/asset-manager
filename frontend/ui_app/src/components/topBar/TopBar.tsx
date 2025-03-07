import React from "react";
import styles from "./topbar.module.scss";
import {NotificationsNone, Language, Settings} from "@mui/icons-material";
import {SearchBar} from "../index";

interface topBarProps {
    children?: any
}

export default function TopBar() {
    return (
        <div className={styles.topBar}>
            <div className={styles.topBarContent}>
                {logo()}
                <SearchBar/>
                {defaultMenu()}
            </div>
        </div>
    )

    function logo() {
        return (
            <div>
                <span className={styles.logo}>asset-manager</span>
            </div>
        )
    }

    function defaultMenu() {
        const user = "https://images.pexels.com/photos/1526814/pexels-photo-1526814.jpeg?auto=compress&cs=tinysrgb&dpr=2&w=500";
        return (
            <div className={styles.topRight}>
                <div className={styles.topbarIconContainer}>
                    <NotificationsNone />
                    <span className={styles.topIconBadge}>2</span>
                </div>
                <div className={styles.topbarIconContainer}>
                    <Language />
                    <span className={styles.topIconBadge}>2</span>
                </div>
                <div className={styles.topbarIconContainer}>
                    <Settings />
                </div>
                <img src={user} alt="" className={styles.topAvatar} />
            </div>
        )
    }
}

