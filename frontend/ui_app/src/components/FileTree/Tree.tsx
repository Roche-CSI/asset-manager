import React from "react";
import TreeNode from "./TreeNode";
import styles from "./tree.module.scss";

interface Props {
    path?: string;
    onPathClick: Function;
    treeData: any[];
}


export default function Tree(props: Props) {
    return (
      <ul className="ml-2">
        {props.treeData.map((node) => (
          <TreeNode node={node} key={node.name} path={props.path} onPathClick={props.onPathClick} />
        ))}
      </ul>
    );
  }
