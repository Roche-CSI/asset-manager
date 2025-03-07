import React, { useState } from "react";
import Tree from "./Tree"
import FolderIcon from '@mui/icons-material/Folder';
import KeyboardArrowRightIcon from '@mui/icons-material/KeyboardArrowRight';
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import InsertDriveFileOutlinedIcon from '@mui/icons-material/InsertDriveFileOutlined';
import { icon } from "../tables/historyTable/HistoryTable";
import styles from "./tree.module.scss";
import {ChevronDown, ChevronRight, File, Folder, FolderDown, FolderInput} from "lucide-react";

interface Props {
    node?: any;
    path?: string;
    onPathClick: Function;
}

export default function TreeNode(props: Props) {
    const { name, category, path, id, prevId, children } = props.node;
    let isFolder: boolean = children.length > 0
    let active: boolean = path === props.path
    
    const [showChildren, setShowChildren] = useState(props.path?.includes(name));
    
    const handleClick = () => {
        setShowChildren(!showChildren);
    };
    
    const folderView = () => {
        return (
            <div className={`my-1 flex items-center text-sm px-1 py-0.5 rounded transition duration-100 ease-in-out
        ${active ? 'text-neutral-800' : 'hover:bg-gray-200 hover:bg-opacity-60'} cursor-pointer`}>
                <div className="flex-shrink-0 mr-1">
                    {
                        showChildren ?
                            <FolderDown className="w-4 h-4 text-primary" />
                            :
                            <Folder className="w-4 h-4 mr-1 text-neutral-500" />
                    }
                </div>
                {/*<Folder className="w-4 h4 mr-2 text-primary border"/>*/}
                <span className="truncate flex-grow min-w-0">{name}</span>
            </div>
        )
    }
    
    const fileView = () => {
        return (
            <div className={`text-sm flex justify-between my-1 pl-1 cursor-pointer items-center ${active ? "bg-base-300 font-semibold py-0.5" : ""}`}>
                <div className="flex-shrink-0">
                    <File className="w-4 h-4 mr-1 text-neutral-400" />
                </div>
                <span className={`truncate flex-grow min-w-0`}
                      onClick={() => props.onPathClick && props.onPathClick(path)}>
                    {name}
                </span>
                <div className={styles.fileIcon}>
                    {icon(category)}
                </div>
            </div>
        )
    }
    const sorted = sortFileTreeNodes(children);
    
    return (
        <div>
            <div onClick={handleClick}>
                {isFolder ? folderView() : fileView()}
            </div>
            <ul className={styles.children}>
                {showChildren && <Tree treeData={sorted} path={props.path} onPathClick={props.onPathClick} />}
            </ul>
        </div>
    );
}

function sortFileTreeNodes(nodes) {
    return nodes.sort((a, b) => {
        // First, separate files and folders
        const aIsFolder = a.children.length > 0;
        const bIsFolder = b.children.length > 0;
        
        if (aIsFolder && !bIsFolder) {
            return 1; // a is a folder, b is a file, so b comes first
        }
        if (!aIsFolder && bIsFolder) {
            return -1; // a is a file, b is a folder, so a comes first
        }
        
        // If both are files or both are folders, sort alphabetically
        return a.name.localeCompare(b.name);
    });
}


