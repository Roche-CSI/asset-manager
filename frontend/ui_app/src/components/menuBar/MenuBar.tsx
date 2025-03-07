import React from "react";
import {Link} from "react-router-dom";
import defaultStyles from "./menubar.module.scss"

interface MenuBarProps {
    paths: object[];
    styles?: any;
}

export default function MenuBar(props: MenuBarProps) {
    const children = props.paths.map(
        (path: any, index: number) =>
        {
            const Icon = path.icon;
            return (
                <Link key={index}
                      to={path.route}
                      onClick={() => {}}
                      className={defaultStyles.link}>
                    <div className={`${defaultStyles.menuItem} ${path.active ? defaultStyles.active : ''}`}>
                        {Icon ? <Icon className={defaultStyles.menuIcon}/> : null}
                        {path.label}
                    </div>
                </Link>
            )
        }
    );

    const styles: any = props.styles?? defaultStyles;

    return (
        <div className={styles.menuBarContainer}>
            <div className={defaultStyles.menuBar}>
                {children}
            </div>
        </div>
    )
}