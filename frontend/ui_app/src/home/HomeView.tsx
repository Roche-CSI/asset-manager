import React, {Fragment, useEffect, useState} from "react";
import styles from "./home_view.module.scss";
import {ViewWithSideBar} from "../components/layout";
import MenuIcon from '@mui/icons-material/Menu';
import PeopleOutlineIcon from '@mui/icons-material/PeopleOutline';
import SearchBar from "../components/search/searchBar/SearchBar";
import {Asset} from "../servers/asset_server";
import AssetViewer from "./AssetViewer";

export default function HomeView() {
    return (
        <div>
            {/*<ViewWithSideBar*/}
            {/*    headerContent={headerContent()}*/}
            {/*    sideBarContent={sideBarContent()}*/}
            {/*    pageContent={PageContent()}*/}
            {/*/>*/}
        </div>
    )

    function headerContent() {
        return (
            <Fragment>
                <MenuIcon className={styles.bar_icon}/>
                <h3 className={styles.app_title}>Asset Manager</h3>
                <img className={styles.logo} src={logo}/>
                <SearchBar/>
                <PeopleOutlineIcon className={styles.user_icon}/>
            </Fragment>
        )
    }

    function sideBarContent() {
        return (
            <Fragment>
                <h4>menu-1</h4>
                <h4>menu-2</h4>
            </Fragment>
        )
    }

    function PageContent() {
        return (
            <div>
                <h5>Page Content</h5>
                {/*<AssetViewer asset_id={'05872f3e-3305-40e8-bce0-2fe7ab75a0e0'}/>*/}
            </div>
        )
    }
}
