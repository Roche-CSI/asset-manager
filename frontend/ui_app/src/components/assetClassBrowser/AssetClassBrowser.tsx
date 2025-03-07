import React, { useEffect, useState } from "react";
import styles from "./browser.module.scss";
import { Asset, AssetClass } from "../../servers/asset_server";
import AssetList from "./AssetList";
import { convertToCurrentTimeZone } from "../../utils";
import { GlobalStore, useStore } from "../../stores";
import { StoreNames } from "../../stores";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import AccessTimeIcon from "@mui/icons-material/AccessTime";
import SettingsOutlinedIcon from '@mui/icons-material/SettingsOutlined';
import { Col, Row } from "react-bootstrap";
import IconButton from "@mui/material/IconButton";
import FormatListBulletedOutlinedIcon from '@mui/icons-material/FormatListBulletedOutlined';
import ModeEditOutlineOutlinedIcon from '@mui/icons-material/ModeEditOutlineOutlined';
import StickyNote2OutlinedIcon from '@mui/icons-material/StickyNote2Outlined';
import EditAssetClass from "../../pages/assetClassPage/EditAssetClass";
import { SimpleToast } from "../toasts";
import { ToastType } from "../toasts/SimpleToast";
import EditReadMe from "../../pages/assetClassPage/EditReadMe";
import { MarkdownEditor } from "../markDownEditor";
import AssetClassIcon from "./ClassIcons";


interface BrowserProps {
    assetClass: AssetClass;
    className?: string
}

export default function AssetClassBrowser(props: BrowserProps) {
    const classIdStore = useStore(StoreNames.classIdStore);
    const [editMode, setEditMode] = useState<boolean>(false);
    const [editReadMe, setEditReadMe] = useState<boolean>(false);
    const [assetClass, setAssetClass] = useState<any>(null);
    const [toastData, setToastData] = useState<any>({ type: null, label: null, message: null });
    const [showToast, setShowToast] = useState<boolean>(false);

    useEffect(() => {
        setAssetClass((assetClass: any) => { return { ...props.assetClass } });
    }, [props.assetClass.id])

    const onEdit = (e: any) => {
        console.log("on Edit clicked: ", e)
        setEditMode(true);
    }

    const onEditReadMe = (e: any) => {
        console.log("on Edit Readme clicked: ", e)
    }

    const onEditCancel = (e: any) => {
        console.log("on Edit closed: ", e)
        setEditMode(false);
    }

    const onEditSuccess = (e: any) => {
        console.log("on Edit success");
        setAssetClass((assetClass: any) => { return { ...classIdStore.get()[props.assetClass.id] } });
        setEditMode(false);
        setToastData((toastData: any) => {
            return { type: ToastType.Success, label: "Success", message: "Asset Class updated" };
        })
        setShowToast(true);
    }

    if (!assetClass) {
        return null;
    }
    console.log("asset_class:", assetClass);

    return (
        <div>
            <div className='has-bootstrap'>
                <div className='grid grid-cols-3 gap-5'>
                    {/* <div>
                <AssetClassTagsBrowser assetClass={assetClass}/>
                </div>
                */}
                    <div className='col-span-2'>
                        <AssetList assetClass={assetClass} />
                    </div>
                    <div className='col-span-1'>
                        {assetClassInfo()}
                    </div>
                </div>
                <Col md={12}>
                    <div className={styles.card}>
                        <div className={styles.textBoxHeader}>
                            <div className={styles.tbHeaderContents}>
                                <div className={styles.readMeContainer}>
                                    <FormatListBulletedOutlinedIcon />
                                    <span>README.md</span>
                                </div>
                                <IconButton onClick={(e: any) => setEditReadMe(true)}>
                                    <ModeEditOutlineOutlinedIcon />
                                </IconButton>
                            </div>
                        </div>
                        <div>
                            <MarkdownEditor mode={"preview"}
                                showTabs={false}
                                mdContent={assetClass.readme} />
                        </div>
                    </div>
                </Col>
                {
                    editMode && editForm()
                }
                {
                    showToast && <SimpleToast title={toastData.label}
                        message={toastData.message}
                        type={toastData.type}
                        onClose={onToastClose}
                        autoHide={true}
                        show={showToast} />
                }
                <EditReadMe classId={assetClass.id}
                    readmeText={assetClass.readme}
                    onSave={onReadMeSave}
                    onCancel={onReadMeCancel}
                    show={editReadMe} />
            </div >
        </div >
    )

    function assetClassInfo() {
        return (
            <div className={`${styles.card}`}>
                <div className={styles.textBox}>
                    <div className='flex flex-row items-start justify-between text-sm p-3 border-stroke border-b-2'>
                        <div className='flex flex-row space-x-2'>
                            <div className='flex flex-col '>
                                <p>{assetClass.title}</p>
                                <div className='w-15 text-xs text-center text-white !bg-primary rounded-lg p-1'>
                                    {assetClass.class_type || "No type provided"}
                                </div>
                            </div>
                            <div className='text-lg !text-primary'>
                                <AssetClassIcon classType={assetClass.class_type as string} />
                            </div>
                        </div>
                        <IconButton onClick={onEdit}>
                            <SettingsOutlinedIcon />
                        </IconButton>
                    </div>
                    <div className={styles.textBoxBody}>
                        <div>
                            <h6>About</h6>
                            <div>
                                {assetClass.description || "No description provided"}
                            </div>
                        </div>
                    </div>
                    <div className={styles.textBoxFooter}>
                        <div className={styles.textBoxFooterItem}>
                            <div>
                                <AccountCircleIcon className={styles.icon} />
                                <span style={{ fontWeight: "bold" }}>{assetClass.created_by}</span>
                            </div>
                            <div>
                                <AccessTimeIcon className={styles.icon} />
                                <span>{convertToCurrentTimeZone(assetClass.created_at, "date")}</span>
                            </div>
                        </div>
                        <div className={styles.textBoxFooterItem}>
                            <div>
                                <StickyNote2OutlinedIcon className={styles.icon} />
                                <span>{assetClass.id}</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        )
    }

    function onReadMeSave(event: string) {
        setEditReadMe(false);
        if (event === "success") {
            // const classList = classIdStore.get();
            // const updated = classList[props.assetClass.id];
            // console.log("updated:", updated.readme);
            setAssetClass((assetClass: any) => { return { ...classIdStore.get()[props.assetClass.id] } });
            setToastData((toastData: any) => {
                return { type: ToastType.Success, label: "Success", message: "Asset Class updated" };
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
        setEditReadMe(false);
    }

    function onToastClose() {
        setShowToast(false);
    }

    function editForm() {
        return (
            <EditAssetClass show={editMode} assetClass={assetClass} onSave={onEditSuccess} onCancel={onEditCancel} />
        )
    }
}