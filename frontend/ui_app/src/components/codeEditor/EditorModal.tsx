import React from "react";
import { Button } from "react-bootstrap";
import IconButton from "@mui/material/IconButton";
import { CloseOutlined } from "@mui/icons-material";
import Modal from "../modal/Modal";
import ReactAceEditor from "./ReactAceEditor";
import {Expand, Maximize2} from "lucide-react";


interface Props {
    value: any;
    onChange?: Function;
    readonly?: boolean;
    height?: number;
    className?: string;
    setShow: Function;
    show?: boolean;
    title: string;
}

export default function EditorModal(props: Props) {

    return (
        <div className="relative">
            <div className="flex justify-end absolute top-2 right-0 z-10">
                <button className="btn btn-ghost rounded-full text-sm text-gray-500" onClick={() => props.setShow(true)}>
                    <Maximize2 className="h-4 w-4"/>
                </button>
            </div>
            {
                props.show &&
                <Modal className={"overflow-scroll p-1"}>
                    <div>
                        <div className="flex justify-between">
                            <h3>{props.title}</h3>
                            <div className={""}>
                                <IconButton onClick={() => props.setShow(false)}>
                                    <CloseOutlined />
                                </IconButton>
                            </div>
                        </div>
                        <ReactAceEditor
                            height={props.height}
                            value={props.value}
                            onChange={props.onChange}
                            readonly={props.readonly}
                            foldData={true}
                        />
                    </div>
                </Modal>
            }
        </div>
    );
}
