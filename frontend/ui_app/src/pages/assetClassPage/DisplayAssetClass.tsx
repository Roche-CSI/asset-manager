import React, {useEffect, useState} from "react";
import styles from "./classpage.module.scss";
import {StoreNames, useStore} from "../../stores";
import {Link} from "react-router-dom";
import {AssetClass} from "../../servers/asset_server";
import {AssetClassBrowser} from "../../components/assetClassBrowser";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";
import {useQuery} from "../../utils/utils";
import Breadcrumb, { BreadcrumbItem } from "../../components/breadCrumb/Breadcrumb";

interface Props {
    project_id: string;
}

export default function DisplayAssetClass(props: Props) {
    const classNameStore = useStore(StoreNames.classNameStore);
    const classIdStore = useStore(StoreNames.classIdStore);
    const userStore = useStore(StoreNames.userStore);
    const assetClassName: string = useQuery().get("name");
    const [assetClass, setAssetClass] = useState<AssetClass | null>(classNameStore.get(assetClassName));
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        /***
         * user could directly copy & paste the class-url in browser, in which case the
         * store may not have the class data. we check and load from asset_server if required.
         */
        const active_project_id: string = userStore.get("active_project");
        console.log("active_project_id:", active_project_id, " props.project_id:", props.project_id)
        if (props.project_id !== active_project_id) {
            if (Object.keys(userStore.get("projects")).includes(props.project_id)) {
                userStore.set("active_project", props.project_id);
            } else {
                setError("Oops! You do not have access to the project where this asset class is located");
                return
            }
        }
        if (assetClassName) {
            if (!classNameStore.get(assetClassName)) {
                console.log("fetching from asset_server")
                AssetClass.getFromServer(null, assetClassName, userStore.get("active_project")).then((json) => {
                    let newClass = new AssetClass(json[0]);
                    classNameStore.set(assetClassName, newClass);
                    classIdStore.set(newClass.id, newClass); // store by both name and id
                    setAssetClass(newClass);
                }).catch((error: any) => {
                    console.log(error.message);
                    setError("Asset Class Not Found In Current Project");
                })
            }else {
                setAssetClass(classNameStore.get(assetClassName));
            }
        }
    }, [assetClassName])

    console.log("className:", assetClassName, " assetClass:", assetClass);

    return (
        // <div className={styles.page}>
        <div>
            {header(assetClassName)}
            {assetClass &&
                <AssetClassBrowser assetClass={assetClass}
                                   className={styles.card}/>}
            {error && <h2>{error}</h2>}
        </div>
    )

    function header(className: string) {
        const items: BreadcrumbItem[] = [
            { index: 0, name: "Assets", url: "/assets" },
            { index: 1, name: className, url: "/assets" }
        ]
        return (
            <Breadcrumb items={items} title={`Assets / ${className}`}/>
        )
    }


    function pageTitle(className: string) {
        return (
            <div style={{border: "none", display: "flex"}}>
                <div className={styles.pageHeader}>
                    <h5>
                        <Link to ="/assets">assets</Link>
                        <ArrowRightIcon/>
                        <span>{className}</span>
                    </h5>
                </div>
            </div>
        )
    }
}