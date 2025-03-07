import React, { useEffect, useState } from "react";
import styles from "./documentation.module.scss";
import DocumentHeader from './Header';
import AssetURLs from "../../servers/asset_server/assetURLs";
import { fetchGet } from "../../servers/base";
import { MarkdownEditor } from "../../components/markDownEditor";
import { SimpleToast } from "../../components/toasts";
import { ToastType } from "../../components/toasts/SimpleToast";
import EditDocumentation from "./EditDocumentation";
import IconButton from "@mui/material/IconButton";
import DownloadIcon from '@mui/icons-material/Download';
import { AccordionItemObject } from '../../components/accordion/AccordionItem';
import { Accordion } from '../../components/accordion';

export default function Documentation() {
    const [documentation, setDocumentation] = useState<string>('');
    const [installation, setInstallation] = useState<string>('');
    const [editDoc, setEditDoc] = useState<boolean>(false);
    const [toastData, setToastData] = useState<any>({ type: null, label: null, message: null });
    const [showToast, setShowToast] = useState<boolean>(false);

    useEffect(() => {
        fetchGet(new AssetURLs().asset_settings_route(), { name: "documentation" })
            .then((data: any) => {
                setDocumentation(data.value);
            })
            .catch((error: any) => {
                setDocumentation("Oops Snap! There is an error getting the documentation.")
            })
    }, [])

    useEffect(() => {
        fetchGet(new AssetURLs().asset_settings_route(), { name: "Installation Instructions" })
            .then((data: any) => {
                setInstallation(data.value);
            })
            .catch((error: any) => {
                setInstallation("Oops Snap! There is an error getting the documentation.")
            })
    }, [])

    function onReadMeSave(event: string, newDoc: string) {
        setEditDoc(false);
        if (event === "success") {
            setDocumentation(newDoc)
            setToastData((toastData: any) => {
                return { type: ToastType.Success, label: "Success", message: "Documentation updated" };
            })
            setShowToast(true);
        } else {
            setToastData((toastData: any) => {
                return { type: ToastType.Danger, label: "error", message: event };
            })
            setShowToast(true);
        }
    }

    function onReadMeCancel() {
        setEditDoc(false);
    }

    function onToastClose() {
        setShowToast(false);
    }

    function downloadScript(filename: string, text: string) {
        const regex = /```\{shell\}\r\n#!\/usr(.*?)```/s // match installation shell script
        const matched: any = text.match(regex)
        const script: string = matched?.[0]
        const trimmed = script?.substring(10, script.length - 3) // trim ```{shell} and ``` from the end
        const res = trimmed?.replace(/\r\n/g, '\n') // replace windows line endings with unix
        // console.log(res)
        const blob = new Blob([res], { type: 'application/x-shellscript' });
        const elem = window.document.createElement('a');
        elem.href = window.URL.createObjectURL(blob);
        elem.download = filename;
        document.body.appendChild(elem);
        elem.click();
        document.body.removeChild(elem);
    }

    const renderItem = (header: string, text: string) => {
        return (
            <div>
                {
                    header === "Installation" &&
                    <IconButton onClick={() => downloadScript("install.sh", text)}
                        className='mb-3'>
                        <DownloadIcon />
                        <span className='text-base ml-1'>Click to download install.sh</span>
                    </IconButton>
                }
                <div>
                    <MarkdownEditor mode={"preview"}
                        showTabs={false}
                        mdContent={text}
                        styles={styles} />
                </div>
            </div>
        )
    }

    const itemsList: AccordionItemObject[] = [
        {
            id: 1,
            header: `How to Install`,
            text: installation,
            render: () => renderItem("Installation", installation)
        },
        {
            id: 2,
            header: `How to Use`,
            text: documentation,
            render: () => renderItem("Documentation", documentation)
        }
    ]


    return (
        <div className='p-4'>
            <DocumentHeader />
            <Accordion itemsList={itemsList} />
            <SimpleToast
                title={toastData.label}
                message={toastData.message}
                type={toastData.type}
                onClose={onToastClose}
                autoHide={true}
                show={showToast} />
            <EditDocumentation
                doc={documentation}
                onSave={onReadMeSave}
                onCancel={onReadMeCancel}
                show={editDoc} />
        </div>
    )
}