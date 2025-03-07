import React from "react";
import FileTree from "../../utils/FileTree";
import { Tree } from "."
import styles from "./tree.module.scss";

interface DiffTreeProps {
    path?: string;
    onPathClick: Function;
    diffArray: any;
}

export const DiffTreeViewer = (props: DiffTreeProps) => {
    const treeData: any = FileTree.diffArrayToTree(props.diffArray)
    // console.log(treeData)

    return (
        <div className={styles.treeContainer}>
            <div className={styles.fileTree}>
                <Tree treeData={treeData} path={props.path} onPathClick={props.onPathClick} />
            </div>
        </div>
    )
}