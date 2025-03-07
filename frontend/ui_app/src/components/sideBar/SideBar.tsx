import styles from "./sidebar.module.scss";
import React, {useEffect, useState} from "react";
import {SidebarMenu} from "./sidebarMenu";
import {MenuItem} from "../common";
import {SidebarItem} from "./sidebarItem";
import {useLocation, useParams} from 'react-router-dom'

export default function Sidebar(props?: any) {
    const location = useLocation()
    const pathComps = location.pathname.split("/")
    // pathname starts with "/", so the first element in array is a empty string
    let path = pathComps.length >= 2 ? pathComps[1] : "";
    let [active, setActive] = useState(Object.keys(SidebarMenu)[0]);
    // let [sidebarOpen, setSidebarOpen] = useState(false);

    useEffect(() => {
        // todo: refactor to remove hardcoding
        if (path === "pipeline") {
            path = "pipelines";
        }
        if (path === "project") {
            path = "projects"
        }
        path = SidebarMenu.hasOwnProperty(path) ? path : Object.keys(SidebarMenu)[0];
        setActive(path);
    }, [path])


    const onMenuClick = (name: string) => {
        setActive(name);
    }

    // console.log(Object.getOwnPropertyNames(SidebarMenu), SidebarMenu.hasOwnProperty(path));
    //console.log("location:", location, ", comps:", pathComps, ", path:", path, ", active:", active);

    return (
        <div className={`${props.sidebarOpen && styles.sidebar}`}>
            <div className={`${styles.sidebarWrapper} ${!props.sidebarOpen && 'hidden'}`}>
                <div className={styles.sidebarLogo}>
                    <div className={styles.logoText}>
                        <h6>asset manager</h6>
                    </div>
                    <br/>
                </div>
            </div>
        </div>
    );

    function mainMenu(active: string, onSelect?: Function): any {
        return Object.keys(SidebarMenu).map(
            (key, idx) => SidebarItem(SidebarMenu[key]["menu"], active, onSelect));
    }

    function subMenu(active: string, onSelect?: Function) {
        const subMenus: MenuItem[] = SidebarMenu[active]["subMenus"];
        if (subMenus.length === 0) {
            return null;
        }
        return (
            <div className={styles.sidebarMenu}>
            <h3 className={styles.sidebarTitle}>Section Menu</h3>
            <ul className={styles.sidebarList}>
                {subMenus.map(menu => SidebarItem(menu))}
            </ul>
        </div>
        )
    }
}
