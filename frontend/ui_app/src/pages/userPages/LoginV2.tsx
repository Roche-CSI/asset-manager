import React, {useState} from 'react';
import { useNavigate, Link } from "react-router-dom";

import {useQuery} from "../../utils/utils";
import {fetchGet} from "../../servers/base";
import AssetURLs from "../../servers/asset_server/assetURLs";
import {Logo} from "../../components/logo";

export const LoginV2 = () => {
	const query = useQuery();
	const action = query.get("action");
	const error = query.get("error");
	const [loginError, setLoginError] = useState('');
	const navigate = useNavigate();
	
	function onSubmit(event: any) {
		const clientUrl = window.location.origin + "/projects";
		fetchGet(new AssetURLs().login_route(), {client_url: encodeURIComponent(clientUrl)} ).then((data: any) => {
			// console.log("res: ", data);
			window.location.assign(data.auth_url);
		}).catch((err) =>
			setLoginError("Oh Snap! You've got an unexpected error."));
	}

	const toSignup = () => {
        navigate("/login?action=signup")
    }
	
	return (
		<div className="min-h-screen w-full bg-slate-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
			<Link className="sm:mx-auto sm:w-full sm:max-w-md"
			      to={"/"}>
				<div className="w-full flex items-center justify-center">
					<Logo/>
				</div>
				<h2 className="text-center text-3xl font-extrabold text-blue-500">
					Asset Manager
				</h2>
			</Link>
			
			<div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
				<div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
					<div className="space-y-6">
						<div>
							<p className="text-sm text-gray-600 text-center mb-4">
								Use your Google account to sign in
							</p>
							<button
								onClick={onSubmit}
								type="button"
								className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
							>
								<svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
									<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
									<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
									<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
									<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
									<path d="M1 1h22v22H1z" fill="none"/>
								</svg>
								Sign in with Google
							</button>
						</div>
					</div>
					
					<div className="mt-6">
						<div className="relative">
							<div className="absolute inset-0 flex items-center">
								<div className="w-full border-t border-gray-300"></div>
							</div>
							<div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white text-gray-500">
                  New to Asset Manager?
                </span>
							</div>
						</div>
						
						<div className="mt-6 text-center">
							<div className="text-sm font-medium text-blue-600 hover:text-blue-500 cursor-pointer"
								onClick={toSignup}>
								Sign Up
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};

export default LoginV2;
