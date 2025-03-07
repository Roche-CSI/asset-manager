import React from "react";
import { Check, Copy } from "lucide-react";

import { StoreNames, useStore } from "../../stores";
import { CircularAvatar } from "../projectsPage/v2/cards/UserCard"
import { StringExt } from "utils/strUtils.ts";

export default function ProfileV2() {
    //stores
    const userStore = useStore(StoreNames.userStore);
    const user: any = userStore.get("user")
    const fullName = new StringExt(user.email.split("@")[0].split(".").slice(0, 2).join(" ")).toTitleCase();
    const [copied, setCopied] = React.useState(false);
    const [showToken, setShowToken] = React.useState(false);

    const userInfo: any = [
        { label: "Full Name", value: fullName || user.username },
        { label: "Email", value: user.email },
        { label: "Username", value: user.username },
        { label: "Active Status", value: "Active" },
    ]

    const copyToClipboard = async () => {
        try {
            await navigator.clipboard.writeText(user.token);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
        }
    };

    return (
        <div className="">
            <div className="h-72 text-lg text-neutral 
                flex flex-col items-center justify-center gap-5">
                <div className="">
                    <CircularAvatar username={user.username} size="xl"
                        bgColor="bg-gradient-to-r from-blue-500 to-blue-700" />
                </div>
                <div className="flex flex-col items-center gap-2">
                    <span className="text-3xl text-gray-600">
                        {fullName || user.username}
                    </span>
                </div>
            </div>
            <div className="bg-slate-100 px-8 py-12 text-gray-900">
                <div className="text-xl px-6 mb-6">
                    Profile
                </div>
                <div className="px-6 py-12 border rounded bg-white text-lg">
                    <div className="flex flex-row justify-between max-w-7xl">
                        {userInfo.map((info: any, index: number) => (
                            <div key={index} className="flex flex-col gap-1">
                                <p className="text-gray-900">{info.label}</p>
                                <p className="text-gray-500">{info.value}</p>
                            </div>
                        ))}
                    </div>
                    <div className="mt-6">
                        <p className="">User Token</p>
                        {showToken ?
                            <div className="group flex items-center space-x-2 px-3 py-0.5 text-xs w-1/3 h-30 whitespace-normal bg-slate-100 text-neutral rounded font-medium cursor-pointer">
                                <span className="break-all p-2 text-gray-500">
                                    {user.token}
                                </span>
                                <button
                                    onClick={copyToClipboard}
                                    className={`${copied ? 'opacity-100' : 'opacity-0 group-hover:opacity-100'} rounded-full transition-all p-0.5`}
                                    title="Copy to clipboard"
                                >
                                    {copied ? (
                                        <Check className="size-5 text-neutral" />
                                    ) : (
                                        <Copy className="size-4 text-neutral-400 hover:text-neutral" />
                                    )}
                                </button>
                            </div>
                            :
                            <button
                                onClick={() => setShowToken(true)}
                                className="text-blue-500 hover:underline"
                            >
                                Show Token
                            </button>
                        }
                    </div>
                </div>
            </div>
        </div>
    )

}