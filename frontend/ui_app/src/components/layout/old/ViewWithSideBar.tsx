import React from "react";
import styles from "./sidebar.module.scss";
import {TopBar} from "../../topBar";
import {SideBar} from "../../sideBar";

interface Props {
    headerContent: React.ReactNode
    sideBarContent: React.ReactNode
    pageContent: React.ReactNode
}

export default function ViewWithSideBar(props: Props) {
    return (
        <div className={styles.sideBarLayout}>
            {/*<TopBar children={props.headerContent}/>*/}
            {/*<div className={styles.topBar}>*/}
            {/*    <div className={styles.topBarContent}>*/}
            {/*        {props && props.headerContent}*/}
            {/*    </div>*/}
            {/*</div>*/}

            <div className={styles.page}>
                <SideBar/>
                {/*<div className={styles.sideBar}>*/}
                {/*    {props && props.sideBarContent}*/}
                {/*</div>*/}
                {/*<div className={styles.content}>*/}
                {/*    {props && props.pageContent}*/}
                {/*</div>*/}
            </div>
        </div>
    )
}