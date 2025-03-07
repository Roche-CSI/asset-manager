import React, { useState } from 'react';
import { useNavigate } from "react-router-dom";
import { useQuery } from "../../utils/utils";
import { fetchPost } from "../../servers/base";
import AssetURLs from "../../servers/asset_server/assetURLs";
import { Logo } from "../../components/logo";
import { StoreNames, useStore } from "../../stores";
import { ButtonSpinner } from "../assetClassPageV2/forms/FormHelpers";


export const SignupV2 = ({ onClick }) => {
	const query = useQuery();
	const action = query.get("action");
	const error = query.get("error");
	const [signupError, setSignupError] = useState('');
	const [email, setEmail] = useState('');
	const [userId, setUserId] = useState('');
	const [confirmUserId, setConfirmUserId] = useState('');
	const userStore = useStore(StoreNames.userStore, true);
	const [loading, setLoading] = useState(false);
	const navigate = useNavigate()

	const onClickSignIn = () => {
		navigate("/login")
	}

	function onSubmit(event: React.FormEvent) {
		event.preventDefault();
		if (userId !== confirmUserId) {
			setSignupError("User ID and Confirm User ID do not match.");
			return;
		}
		setLoading(true);
		fetchPost(new AssetURLs().signup_route(), { 'email': email, 'username': userId })
			.then((data) => {
				console.log("res: ", data);
				onClick()
			})
			.catch((err) => {
				setLoading(false);
				setSignupError("Oh Snap! You've got an unexpected error.")
			});
	}

	return (
		<div className="min-h-screen w-full bg-slate-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
			<div className="sm:mx-auto sm:w-full sm:max-w-md">
				<div className="w-full flex items-center justify-center">
					<Logo />
				</div>
				<h2 className="text-center text-3xl font-extrabold text-blue-500">
					Asset Manager
				</h2>
			</div>

			<div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
				<div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
					<form className="space-y-6" onSubmit={onSubmit}>
						<div>
							<label htmlFor="email" className="block text-sm font-medium text-gray-700">
								Email address
							</label>
							<div className="mt-1">
								<input
									id="email"
									name="email"
									type="email"
									autoComplete="email"
									required
									value={email}
									onChange={(e) => setEmail(e.target.value)}
									className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
								/>
							</div>
						</div>

						<div>
							<label htmlFor="text" className="block text-sm font-medium text-gray-700">
								Unix ID
							</label>
							<div className="mt-1">
								<input
									id="unix-id"
									name="user_id"
									type="text"
									// autoComplete="user_id"
									required
									value={userId}
									onChange={(e) => setUserId(e.target.value)}
									className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
								/>
							</div>
						</div>

						<div>
							<label htmlFor="text" className="block text-sm font-medium text-gray-700">
								Confirm Unix ID
							</label>
							<div className="mt-1">
								<input
									id="unix-id"
									name="confirm_user_id"
									type="text"
									autoComplete="user_id"
									required
									value={confirmUserId}
									onChange={(e) => setConfirmUserId(e.target.value)}
									className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
								/>
							</div>
						</div>

						{signupError && (
							<div className="text-red-500 text-sm">{signupError}</div>
						)}
						<div>
							<button
								type="submit"
								className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
								disabled={loading}
							>
								{loading ? <ButtonSpinner message="Signing up..." /> : 'Sign up'}
							</button>
						</div>
					</form>

					<div className="mt-6">
						<div className="relative">
							<div className="absolute inset-0 flex items-center">
								<div className="w-full border-t border-gray-300"></div>
							</div>
							<div className="relative flex justify-center text-sm">
								<span className="px-2 bg-white text-gray-500">
									Already have an account?
								</span>
							</div>
						</div>

						<div className="mt-6 text-center">
							<div onClick={onClickSignIn}
								className="text-sm font-medium text-blue-600 hover:text-blue-500 cursor-pointer">
								Sign In
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
};
