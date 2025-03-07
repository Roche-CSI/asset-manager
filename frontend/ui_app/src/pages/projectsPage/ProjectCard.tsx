import React from "react"
import styles from "./project_card.module.scss";
import Paper from "@mui/material/Paper";

interface Props {
    id?: string;
    name?: string;
    label: string;
    icon: any;
    onClick?: Function;
}

export default function ProjectCard(props: Props) {
    const Icon = props.icon;

    return (
        <Paper className={styles.iconContainer}>
            <div className={styles.iconBody} onClick={() => props.onClick && props.onClick(props.id)}>
                {Icon && <Icon className={styles.projectIcon}/>}
                <div className={styles.iconLabel}>{props.label}</div>
            </div>
        </Paper>
    )
}